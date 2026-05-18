"""PunchLine AI Server — 비전 검사 + 원인 분석 + 시계열 추적 API."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai.analysis.shap_analyzer import ShapAnalyzer
from ai.analysis.timeline import TimelineTracker

app = FastAPI(title="PunchLine AI", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 데이터 소스 설정 ===
_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _ROOT / "data" / "sample"
MODEL_DIR = _ROOT / "models"

USE_DB = os.environ.get("USE_DB", "true").lower() in ("true", "1", "yes")

# CSV fallback (DB 미사용 시)
_process_df: pd.DataFrame | None = None
_inspect_df: pd.DataFrame | None = None

_analyzer: ShapAnalyzer | None = None
_tracker: TimelineTracker | None = None


def _get_inspect_df() -> pd.DataFrame:
    """DB 모드면 매번 최신 데이터, CSV 모드면 캐시된 데이터 반환."""
    if USE_DB:
        from ai.db import read_inspections
        return read_inspections()
    if _inspect_df is not None:
        return _inspect_df
    raise HTTPException(status_code=503, detail="데이터 미로드")


def _get_process_df() -> pd.DataFrame:
    if USE_DB:
        from ai.db import read_process_params
        return read_process_params()
    if _process_df is not None:
        return _process_df
    raise HTTPException(status_code=503, detail="데이터 미로드")


def _load_data():
    global _process_df, _inspect_df, _analyzer, _tracker

    if not USE_DB:
        proc_path = DATA_DIR / "sim_process_params.csv"
        insp_path = DATA_DIR / "sim_inspection_results.csv"
        if proc_path.exists():
            _process_df = pd.read_csv(proc_path)
        if insp_path.exists():
            _inspect_df = pd.read_csv(insp_path)

    # SHAP 모델 (DB/CSV 공용)
    _analyzer = ShapAnalyzer()
    model_path = MODEL_DIR / "lgbm_sim.pkl"
    if model_path.exists():
        _analyzer.load_model(model_path)
    elif not USE_DB:
        if _process_df is not None and _inspect_df is not None:
            _analyzer.train(_process_df, _inspect_df, save_path=model_path)

    _tracker = TimelineTracker(alert_threshold=0.10, alert_window=20)


@app.on_event("startup")
def startup():
    _load_data()


# === Health ===

@app.get("/health")
def health():
    if USE_DB:
        from ai.db import count_inspections
        cnt = count_inspections()
    else:
        cnt = len(_inspect_df) if _inspect_df is not None else 0

    return {
        "status": "ok",
        "mode": "db" if USE_DB else "csv",
        "data_loaded": cnt > 0,
        "model_loaded": _analyzer is not None and _analyzer.model is not None,
        "inspect_count": cnt,
    }


# === 시계열 추적 ===

@app.get("/quality/timeline")
def quality_timeline(
    line_id: str = Query("A"),
    freq: str = Query("15min"),
):
    df = _get_inspect_df()
    if len(df) == 0:
        raise HTTPException(status_code=404, detail="검사 데이터 없음")

    result = _tracker.aggregate(df, line_id=line_id, freq=freq)
    return result.to_dict()


@app.get("/quality/hourly")
def quality_hourly(line_id: str = Query("A")):
    df = _get_inspect_df()
    if len(df) == 0:
        raise HTTPException(status_code=404, detail="검사 데이터 없음")

    return _tracker.hourly_pattern(df, line_id=line_id)


# === 원인 분석 ===

class RootCauseRequest(BaseModel):
    line_id: str = "A"
    time_start: str
    time_end: str


@app.post("/quality/root-cause")
def quality_root_cause(req: RootCauseRequest):
    proc = _get_process_df()
    insp = _get_inspect_df()

    if len(proc) == 0 or len(insp) == 0:
        raise HTTPException(status_code=404, detail="데이터 없음")

    try:
        t_start = pd.Timestamp(req.time_start)
        t_end = pd.Timestamp(req.time_end)
    except Exception:
        raise HTTPException(status_code=400, detail="time_start/time_end 형식 오류 (ISO 8601)")

    proc = proc.copy()
    insp = insp.copy()
    proc["ts"] = pd.to_datetime(proc["recorded_at"])
    insp["ts"] = pd.to_datetime(insp["inspected_at"])

    proc_window = proc[(proc["ts"] >= t_start) & (proc["ts"] <= t_end)]
    insp_window = insp[(insp["ts"] >= t_start) & (insp["ts"] <= t_end)]

    if len(insp_window) == 0:
        raise HTTPException(status_code=404, detail="해당 시간 구간에 검사 데이터 없음")

    # 모델이 없으면 현재 데이터로 학습
    if _analyzer.model is None:
        _analyzer.train(proc, insp, save_path=MODEL_DIR / "lgbm_sim.pkl")

    result = _analyzer.analyze(
        proc_window, insp_window, line_id=req.line_id, top_n=5
    )
    return result.to_dict()


# === KPI 요약 ===

@app.get("/quality/kpi")
def quality_kpi(line_id: str = Query("A")):
    df = _get_inspect_df()
    if len(df) == 0:
        return {
            "total_inspected": 0,
            "defect_rate": 0,
            "defect_rate_delta": 0,
            "top_defect_type": None,
            "top_defect_pct": 0,
            "top_cause_name": "데이터 수집 중",
            "top_cause_shap": 0,
            "active_alerts": 0,
        }

    timeline = _tracker.aggregate(df, line_id=line_id, freq="15min")
    s = timeline.summary

    # 전반부 vs 후반부 불량률 비교
    df = df.copy()
    df["ts"] = pd.to_datetime(df["inspected_at"])
    df["is_defect"] = (df["verdict"] == "defect").astype(int)
    total_ts = df["ts"].max() - df["ts"].min()
    if total_ts.total_seconds() > 0:
        mid = df["ts"].min() + total_ts / 2
        recent = df[df["ts"] >= mid]["is_defect"].mean()
        earlier = df[df["ts"] < mid]["is_defect"].mean()
        delta = recent - earlier
    else:
        delta = 0

    if s.total_defects > 0:
        type_counts = df.loc[df["is_defect"] == 1, "defect_type"].value_counts()
        top_pct = type_counts.iloc[0] / s.total_defects if len(type_counts) > 0 else 0
    else:
        top_pct = 0

    return {
        "total_inspected": s.total_inspected,
        "defect_rate": round(s.overall_defect_rate, 4),
        "defect_rate_delta": round(float(delta), 4),
        "top_defect_type": s.dominant_defect_type,
        "top_defect_pct": round(float(top_pct), 4),
        "top_cause_name": "분석 필요",
        "top_cause_shap": 0,
        "active_alerts": len(timeline.alerts),
    }


# === 검사 결과 스트림 ===

@app.get("/inspect/stream")
def inspect_stream(
    offset: int = Query(0, ge=0),
    limit: int = Query(60, ge=1, le=240),
):
    df = _get_inspect_df()
    if len(df) == 0:
        return {"offset": offset, "limit": limit, "total": 0, "results": []}

    chunk = df.iloc[offset: offset + limit].copy()
    chunk = chunk.where(chunk.notna(), None)
    return {
        "offset": offset,
        "limit": limit,
        "total": len(df),
        "results": chunk.to_dict(orient="records"),
    }
