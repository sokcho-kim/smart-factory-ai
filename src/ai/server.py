"""PunchLine AI Server — 비전 검사 + 원인 분석 + 시계열 추적 API."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai.analysis.shap_analyzer import ShapAnalyzer
from ai.analysis.timeline import TimelineTracker

app = FastAPI(title="PunchLine AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 데이터 로드 (MVP: CSV 기반, Phase 2: PostgreSQL) ===
_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _ROOT / "data" / "sample"
MODEL_DIR = _ROOT / "models"

_process_df: pd.DataFrame | None = None
_inspect_df: pd.DataFrame | None = None
_analyzer: ShapAnalyzer | None = None
_tracker: TimelineTracker | None = None


def _load_data():
    global _process_df, _inspect_df, _analyzer, _tracker

    proc_path = DATA_DIR / "sim_process_params.csv"
    insp_path = DATA_DIR / "sim_inspection_results.csv"
    model_path = MODEL_DIR / "lgbm_sim.pkl"

    if proc_path.exists():
        _process_df = pd.read_csv(proc_path)
    if insp_path.exists():
        _inspect_df = pd.read_csv(insp_path)

    _analyzer = ShapAnalyzer()
    if model_path.exists():
        _analyzer.load_model(model_path)
    elif _process_df is not None and _inspect_df is not None:
        _analyzer.train(_process_df, _inspect_df, save_path=model_path)

    _tracker = TimelineTracker(alert_threshold=0.10, alert_window=20)


@app.on_event("startup")
def startup():
    _load_data()


# === Health ===

@app.get("/health")
def health():
    return {
        "status": "ok",
        "data_loaded": _inspect_df is not None,
        "model_loaded": _analyzer is not None and _analyzer.model is not None,
        "inspect_count": len(_inspect_df) if _inspect_df is not None else 0,
    }


# === 시계열 추적 ===

@app.get("/quality/timeline")
def quality_timeline(
    line_id: str = Query("A"),
    freq: str = Query("15min"),
):
    if _inspect_df is None or _tracker is None:
        raise HTTPException(status_code=503, detail="데이터 미로드")

    result = _tracker.aggregate(_inspect_df, line_id=line_id, freq=freq)
    return result.to_dict()


@app.get("/quality/hourly")
def quality_hourly(line_id: str = Query("A")):
    if _inspect_df is None or _tracker is None:
        raise HTTPException(status_code=503, detail="데이터 미로드")

    return _tracker.hourly_pattern(_inspect_df, line_id=line_id)


# === 원인 분석 ===

class RootCauseRequest(BaseModel):
    line_id: str = "A"
    time_start: str
    time_end: str


@app.post("/quality/root-cause")
def quality_root_cause(req: RootCauseRequest):
    if _process_df is None or _inspect_df is None or _analyzer is None:
        raise HTTPException(status_code=503, detail="데이터/모델 미로드")

    try:
        t_start = pd.Timestamp(req.time_start)
        t_end = pd.Timestamp(req.time_end)
    except Exception:
        raise HTTPException(status_code=400, detail="time_start/time_end 형식 오류 (ISO 8601)")

    # 시간 구간 필터
    proc = _process_df.copy()
    insp = _inspect_df.copy()
    proc["ts"] = pd.to_datetime(proc["recorded_at"])
    insp["ts"] = pd.to_datetime(insp["inspected_at"])

    proc_window = proc[(proc["ts"] >= t_start) & (proc["ts"] <= t_end)]
    insp_window = insp[(insp["ts"] >= t_start) & (insp["ts"] <= t_end)]

    if len(insp_window) == 0:
        raise HTTPException(status_code=404, detail="해당 시간 구간에 검사 데이터 없음")

    result = _analyzer.analyze(
        proc_window, insp_window, line_id=req.line_id, top_n=5
    )
    return result.to_dict()


# === KPI 요약 ===

@app.get("/quality/kpi")
def quality_kpi(line_id: str = Query("A")):
    if _inspect_df is None or _tracker is None:
        raise HTTPException(status_code=503, detail="데이터 미로드")

    timeline = _tracker.aggregate(_inspect_df, line_id=line_id, freq="15min")
    s = timeline.summary

    # 최근 1시간 vs 이전 1시간 비교 (시뮬레이션 기준)
    df = _inspect_df.copy()
    df["ts"] = pd.to_datetime(df["inspected_at"])
    df["is_defect"] = (df["verdict"] == "defect").astype(int)
    total_ts = df["ts"].max() - df["ts"].min()
    mid = df["ts"].min() + total_ts / 2
    recent = df[df["ts"] >= mid]["is_defect"].mean()
    earlier = df[df["ts"] < mid]["is_defect"].mean()
    delta = recent - earlier

    # 불량 유형 1위 비율
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


# === 검사 결과 스트림 (MVP: 시뮬레이션 데이터 순차 반환) ===

@app.get("/inspect/stream")
def inspect_stream(
    offset: int = Query(0, ge=0),
    limit: int = Query(60, ge=1, le=240),
):
    if _inspect_df is None:
        raise HTTPException(status_code=503, detail="데이터 미로드")

    chunk = _inspect_df.iloc[offset: offset + limit].copy()
    chunk = chunk.where(chunk.notna(), None)
    return {
        "offset": offset,
        "limit": limit,
        "total": len(_inspect_df),
        "results": chunk.to_dict(orient="records"),
    }
