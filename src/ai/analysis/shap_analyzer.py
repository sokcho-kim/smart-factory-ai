"""SHAP 기반 불량 원인 추적 모듈.

시뮬레이션 또는 실제 공정 데이터에서 불량 발생 구간의
핵심 원인 변수를 SHAP으로 특정하고, 조치 가이드를 반환한다.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

PROCESS_PARAMS = [
    "mold_temp",
    "injection_pressure",
    "injection_speed",
    "cooling_time",
    "humidity",
    "ambient_temp",
]

PARAM_DISPLAY = {
    "mold_temp": "금형 온도 (°C)",
    "injection_pressure": "사출 압력 (MPa)",
    "injection_speed": "사출 속도 (mm/s)",
    "cooling_time": "냉각 시간 (s)",
    "humidity": "습도 (%)",
    "ambient_temp": "주변 온도 (°C)",
}

NORMAL_RANGES = {
    "mold_temp": (70.0, 80.0),
    "injection_pressure": (80.0, 100.0),
    "injection_speed": (50.0, 70.0),
    "cooling_time": (15.0, 25.0),
    "humidity": (40.0, 60.0),
    "ambient_temp": (20.0, 28.0),
}


@dataclass
class CauseVariable:
    name: str
    display_name: str
    shap_value: float
    current_value: float
    normal_range: tuple[float, float]
    is_abnormal: bool

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "shap_value": round(self.shap_value, 4),
            "current_value": round(self.current_value, 2),
            "normal_range": list(self.normal_range),
            "is_abnormal": self.is_abnormal,
        }


@dataclass
class RootCauseResult:
    analyzed_at: str
    line_id: str
    defect_count: int
    causes: list[CauseVariable]
    recommendation: str
    similar_cases: int = 0

    def to_dict(self) -> dict:
        return {
            "analyzed_at": self.analyzed_at,
            "line_id": self.line_id,
            "defect_count": self.defect_count,
            "causes": [c.to_dict() for c in self.causes],
            "recommendation": self.recommendation,
            "similar_cases": self.similar_cases,
        }


class ShapAnalyzer:
    """공정 파라미터 → 불량 원인 SHAP 분석기."""

    def __init__(self, model_path: str | Path | None = None):
        self.model = None
        self.explainer = None
        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    def train(
        self,
        process_df: pd.DataFrame,
        inspect_df: pd.DataFrame,
        save_path: str | Path | None = None,
    ) -> dict:
        """공정 데이터 + 검사 결과로 모델 학습."""
        import lightgbm as lgb

        # 시간 기반 조인 (가장 가까운 시간)
        merged = self._merge_by_time(process_df, inspect_df)
        X = merged[PROCESS_PARAMS]
        y = (merged["verdict"] == "defect").astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        n_pos = y_train.sum()
        n_neg = len(y_train) - n_pos
        scale = n_neg / max(n_pos, 1)

        self.model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=5,
            random_state=42,
            verbose=-1,
            scale_pos_weight=scale,
        )
        self.model.fit(X_train, y_train)

        # Explainer 초기화
        import shap
        self.explainer = shap.TreeExplainer(self.model)

        # 평가
        from sklearn.metrics import classification_report
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                pickle.dump({"model": self.model, "feature_names": PROCESS_PARAMS}, f)

        return {
            "train_size": len(X_train),
            "test_size": len(X_test),
            "defect_rate": float(y.mean()),
            "report": report,
        }

    def load_model(self, path: str | Path) -> None:
        """저장된 모델 로드."""
        import shap

        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.explainer = shap.TreeExplainer(self.model)

    def analyze(
        self,
        process_df: pd.DataFrame,
        inspect_df: pd.DataFrame,
        line_id: str = "A",
        top_n: int = 5,
    ) -> RootCauseResult:
        """시간 구간의 공정 데이터를 분석하여 원인 추적."""
        if self.model is None or self.explainer is None:
            raise RuntimeError("모델이 로드되지 않았습니다. train() 또는 load_model()을 먼저 실행하세요.")

        # 시간 조인
        merged = self._merge_by_time(process_df, inspect_df)
        defect_mask = merged["verdict"] == "defect"
        defect_count = defect_mask.sum()

        X = merged[PROCESS_PARAMS]

        # SHAP 계산
        shap_values = self.explainer.shap_values(X)
        sv = shap_values[1] if isinstance(shap_values, list) else shap_values
        mean_shap = np.abs(sv).mean(axis=0)

        # 불량 구간의 평균 파라미터 값
        if defect_count > 0:
            defect_means = merged.loc[defect_mask, PROCESS_PARAMS].mean()
        else:
            defect_means = merged[PROCESS_PARAMS].mean()

        # 원인 변수 Top N
        ranked_idx = np.argsort(mean_shap)[::-1][:top_n]
        causes = []
        for idx in ranked_idx:
            name = PROCESS_PARAMS[idx]
            val = float(defect_means[name])
            lo, hi = NORMAL_RANGES[name]
            causes.append(CauseVariable(
                name=name,
                display_name=PARAM_DISPLAY[name],
                shap_value=float(mean_shap[idx]),
                current_value=val,
                normal_range=(lo, hi),
                is_abnormal=val < lo or val > hi,
            ))

        # 조치 가이드 생성
        recommendation = self._build_recommendation(causes)

        return RootCauseResult(
            analyzed_at=datetime.now().isoformat(),
            line_id=line_id,
            defect_count=int(defect_count),
            causes=causes,
            recommendation=recommendation,
        )

    def _merge_by_time(
        self, process_df: pd.DataFrame, inspect_df: pd.DataFrame
    ) -> pd.DataFrame:
        """공정 데이터와 검사 결과를 시간 기준 병합."""
        proc = process_df.copy()
        insp = inspect_df.copy()

        proc["ts"] = pd.to_datetime(proc["recorded_at"])
        insp["ts"] = pd.to_datetime(insp["inspected_at"])

        proc = proc.sort_values("ts")
        insp = insp.sort_values("ts")

        merged = pd.merge_asof(
            insp, proc,
            on="ts",
            direction="nearest",
            tolerance=pd.Timedelta("30s"),
            suffixes=("_insp", "_proc"),
        )
        merged = merged.dropna(subset=PROCESS_PARAMS)
        return merged

    def _build_recommendation(self, causes: list[CauseVariable]) -> str:
        """원인 변수 기반 조치 가이드 생성."""
        abnormals = [c for c in causes if c.is_abnormal]
        if not abnormals:
            return "현재 모든 공정 파라미터가 정상 범위 내에 있습니다. 주기적 모니터링을 유지하세요."

        lines = []
        for c in abnormals:
            lo, hi = c.normal_range
            action = ACTIONS.get(c.name, {})
            if c.current_value > hi:
                direction = "높음"
                guide = action.get("high", f"{c.display_name}을(를) {hi} 이하로 조정하세요.")
            else:
                direction = "낮음"
                guide = action.get("low", f"{c.display_name}을(를) {lo} 이상으로 조정하세요.")

            lines.append(
                f"- {c.display_name}: {c.current_value:.1f} (정상: {lo}~{hi}, {direction}) → {guide}"
            )

        return "\n".join(lines)


# === 조치 가이드 지식 베이스 ===
ACTIONS = {
    "mold_temp": {
        "high": "금형 온도를 80°C 이하로 낮추세요. 냉각수 유량 점검, 금형 냉각 채널 막힘 확인.",
        "low": "금형 예열을 확인하세요. 히터 동작 상태 점검.",
    },
    "injection_pressure": {
        "high": "사출 압력을 100MPa 이하로 조정하세요. 노즐 막힘 여부 확인.",
        "low": "사출 압력을 80MPa 이상으로 올리세요. 유압 펌프 상태 점검, 체크밸브 확인.",
    },
    "injection_speed": {
        "high": "사출 속도를 70mm/s 이하로 낮추세요. 금형 배기(vent) 상태 확인.",
        "low": "사출 속도를 50mm/s 이상으로 올리세요. 스크류 마모 점검.",
    },
    "cooling_time": {
        "high": "냉각 시간 25초 초과는 생산성 저하 우려. 냉각수 온도 확인.",
        "low": "냉각 시간을 15초 이상으로 늘리세요. 수축/변형 불량 방지.",
    },
    "humidity": {
        "high": "습도 60% 초과 시 기포 불량 위험. 제습기 가동, 원재료 건조 상태 확인.",
        "low": "습도가 낮아도 정전기 이슈 가능. 가습기 점검.",
    },
    "ambient_temp": {
        "high": "작업장 온도 관리 확인. 환기 시스템 점검.",
        "low": "작업장 난방 상태 확인.",
    },
}


def run_demo():
    """시뮬레이션 데이터로 E2E 데모 실행."""
    data_dir = Path(__file__).resolve().parents[3] / "data" / "sample"
    model_dir = Path(__file__).resolve().parents[3] / "models"
    model_path = model_dir / "lgbm_sim.pkl"

    process_df = pd.read_csv(data_dir / "sim_process_params.csv")
    inspect_df = pd.read_csv(data_dir / "sim_inspection_results.csv")

    analyzer = ShapAnalyzer()

    # 전체 데이터로 학습
    print("=== 모델 학습 ===")
    metrics = analyzer.train(process_df, inspect_df, save_path=model_path)
    print(f"  학습: {metrics['train_size']}건, 테스트: {metrics['test_size']}건")
    print(f"  불량률: {metrics['defect_rate']:.1%}")
    print(f"  모델 저장: {model_path}")

    # 이벤트 1 구간 분석 (09:42~10:05 = index 168~260)
    print("\n=== 이벤트 1 분석: 금형 과열 (09:42~10:05) ===")
    evt1_proc = process_df.iloc[168:260]
    evt1_insp = inspect_df.iloc[168:260]
    result1 = analyzer.analyze(evt1_proc, evt1_insp, line_id="A", top_n=3)
    print(f"  불량 {result1.defect_count}건")
    for c in result1.causes:
        flag = " [이상]" if c.is_abnormal else ""
        print(f"  {c.display_name}: SHAP {c.shap_value:.4f}, 현재 {c.current_value:.1f} (정상 {c.normal_range}){flag}")
    print(f"  조치 가이드:\n{result1.recommendation}")

    # 이벤트 2 구간 분석 (11:20~11:50 = index 560~680)
    print("\n=== 이벤트 2 분석: 압력 저하 (11:20~11:50) ===")
    evt2_proc = process_df.iloc[560:680]
    evt2_insp = inspect_df.iloc[560:680]
    result2 = analyzer.analyze(evt2_proc, evt2_insp, line_id="A", top_n=3)
    print(f"  불량 {result2.defect_count}건")
    for c in result2.causes:
        flag = " [이상]" if c.is_abnormal else ""
        print(f"  {c.display_name}: SHAP {c.shap_value:.4f}, 현재 {c.current_value:.1f} (정상 {c.normal_range}){flag}")
    print(f"  조치 가이드:\n{result2.recommendation}")

    # 이벤트 3 구간 분석 (13:50~14:25 = index 1160~1300)
    print("\n=== 이벤트 3 분석: 복합 이상 (13:50~14:25) ===")
    evt3_proc = process_df.iloc[1160:1300]
    evt3_insp = inspect_df.iloc[1160:1300]
    result3 = analyzer.analyze(evt3_proc, evt3_insp, line_id="A", top_n=3)
    print(f"  불량 {result3.defect_count}건")
    for c in result3.causes:
        flag = " [이상]" if c.is_abnormal else ""
        print(f"  {c.display_name}: SHAP {c.shap_value:.4f}, 현재 {c.current_value:.1f} (정상 {c.normal_range}){flag}")
    print(f"  조치 가이드:\n{result3.recommendation}")

    # JSON 출력 예시
    print("\n=== API 응답 예시 (이벤트 1) ===")
    import json
    print(json.dumps(result1.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_demo()
