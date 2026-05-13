"""금형 기반 성형 공정 시뮬레이션 데이터 생성.

6시간 가동 (09:00~15:00), 15초 간격 촬영, 1,440건.
3개 이벤트로 불량 급증 → 원인 추적 → 조치 → 복귀 스토리 구현.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

np.random.seed(42)

# === 설정 ===
START = datetime(2026, 5, 22, 9, 0, 0)  # 본선 당일 기준
INTERVAL_SEC = 15
N_SAMPLES = 1440  # 6시간 = 1440 * 15초
LINE_ID = "A"

# 정상 범위
NORMAL = {
    "mold_temp": (75.0, 2.0),       # 평균 75°C, 표준편차 2
    "injection_pressure": (90.0, 3.0),  # 평균 90MPa
    "injection_speed": (60.0, 3.0),     # 평균 60mm/s
    "cooling_time": (20.0, 1.5),        # 평균 20s
    "humidity": (50.0, 3.0),            # 평균 50%
    "ambient_temp": (24.0, 1.0),        # 평균 24°C
}

# 불량 확률 (정상 상태)
BASE_DEFECT_RATE = 0.025  # 2.5%

# === 이벤트 정의 ===
EVENTS = [
    {
        "name": "금형 과열",
        "start_min": 42,    # 09:42
        "peak_min": 48,     # 09:48
        "fix_min": 50,      # 09:50 조치
        "recover_min": 65,  # 10:05 정상 복귀
        "param": "mold_temp",
        "peak_value": 92.0,
        "defect_type": "crack",
        "peak_defect_rate": 0.30,
    },
    {
        "name": "압력 저하",
        "start_min": 140,   # 11:20
        "peak_min": 150,    # 11:30
        "fix_min": 155,     # 11:35 조치
        "recover_min": 170, # 11:50 정상 복귀
        "param": "injection_pressure",
        "peak_value": 62.0,
        "defect_type": "bubble",
        "peak_defect_rate": 0.18,
    },
    {
        "name": "복합 이상 (온도+압력)",
        "start_min": 290,   # 13:50
        "peak_min": 300,    # 14:00
        "fix_min": 305,     # 14:05 조치
        "recover_min": 325, # 14:25 정상 복귀
        "param": "mold_temp+injection_pressure",
        "peak_value": (89.0, 65.0),
        "defect_type": "crack+bubble",
        "peak_defect_rate": 0.35,
    },
]

DEFECT_TYPES = ["crack", "bubble", "scratch"]


def generate_param_value(param_name: str, minute: float) -> float:
    """정상 값 + 이벤트 영향 반영."""
    mean, std = NORMAL[param_name]
    base = np.random.normal(mean, std)

    for evt in EVENTS:
        if "+" in evt.get("param", ""):
            params = evt["param"].split("+")
            if param_name in params:
                idx = params.index(param_name)
                peak = evt["peak_value"][idx]
                base = _apply_event(base, mean, peak, minute, evt)
        elif evt["param"] == param_name:
            peak = evt["peak_value"]
            base = _apply_event(base, mean, peak, minute, evt)

    return round(base, 2)


def _apply_event(base: float, normal_mean: float, peak: float,
                 minute: float, evt: dict) -> float:
    """이벤트 구간에서 파라미터 값을 변형."""
    s, p, f, r = evt["start_min"], evt["peak_min"], evt["fix_min"], evt["recover_min"]

    if minute < s or minute > r:
        return base

    # 상승 구간
    if s <= minute <= p:
        t = (minute - s) / max(p - s, 1)
        return normal_mean + (peak - normal_mean) * t + np.random.normal(0, 1)

    # 유지 구간 (peak ~ fix)
    if p < minute <= f:
        return peak + np.random.normal(0, 1.5)

    # 하강 구간 (fix ~ recover)
    if f < minute <= r:
        t = (minute - f) / max(r - f, 1)
        return peak + (normal_mean - peak) * t + np.random.normal(0, 1)

    return base


def get_defect_rate(minute: float) -> float:
    """현재 시점의 불량 확률."""
    rate = BASE_DEFECT_RATE

    for evt in EVENTS:
        s, p, f, r = evt["start_min"], evt["peak_min"], evt["fix_min"], evt["recover_min"]
        peak_rate = evt["peak_defect_rate"]

        if s <= minute <= p:
            t = (minute - s) / max(p - s, 1)
            rate = max(rate, BASE_DEFECT_RATE + (peak_rate - BASE_DEFECT_RATE) * t)
        elif p < minute <= f:
            rate = max(rate, peak_rate)
        elif f < minute <= r:
            t = (minute - f) / max(r - f, 1)
            rate = max(rate, peak_rate + (BASE_DEFECT_RATE - peak_rate) * t)

    return rate


def get_defect_type(minute: float) -> str:
    """현재 시점의 불량 유형 결정."""
    for evt in EVENTS:
        s, r = evt["start_min"], evt["recover_min"]
        if s <= minute <= r:
            dt = evt["defect_type"]
            if "+" in dt:
                return np.random.choice(dt.split("+"))
            return dt

    # 정상 구간: 랜덤 스크래치
    return "scratch"


def main():
    records_process = []
    records_inspect = []

    for i in range(N_SAMPLES):
        ts = START + timedelta(seconds=i * INTERVAL_SEC)
        minute = i * INTERVAL_SEC / 60.0

        # 공정 파라미터
        process = {
            "recorded_at": ts.isoformat(),
            "line_id": LINE_ID,
            "mold_temp": generate_param_value("mold_temp", minute),
            "injection_pressure": generate_param_value("injection_pressure", minute),
            "injection_speed": generate_param_value("injection_speed", minute),
            "cooling_time": generate_param_value("cooling_time", minute),
            "humidity": generate_param_value("humidity", minute),
            "ambient_temp": generate_param_value("ambient_temp", minute),
        }
        records_process.append(process)

        # 검사 결과
        defect_rate = get_defect_rate(minute)
        is_defect = np.random.random() < defect_rate

        inspect = {
            "inspected_at": ts.isoformat(),
            "line_id": LINE_ID,
            "verdict": "defect" if is_defect else "ok",
            "defect_type": get_defect_type(minute) if is_defect else None,
            "confidence": round(np.random.uniform(0.85, 0.99), 3) if is_defect else round(np.random.uniform(0.92, 0.99), 3),
        }
        records_inspect.append(inspect)

    df_process = pd.DataFrame(records_process)
    df_inspect = pd.DataFrame(records_inspect)

    # 저장
    out = Path(__file__).resolve().parents[3] / "data" / "sample"
    out.mkdir(parents=True, exist_ok=True)

    df_process.to_csv(out / "sim_process_params.csv", index=False)
    df_inspect.to_csv(out / "sim_inspection_results.csv", index=False)

    # 통계
    total = len(df_inspect)
    defects = (df_inspect["verdict"] == "defect").sum()
    print(f"생성 완료: {total}건")
    print(f"불량: {defects}건 ({defects/total:.1%})")
    print(f"  crack: {(df_inspect['defect_type']=='crack').sum()}건")
    print(f"  bubble: {(df_inspect['defect_type']=='bubble').sum()}건")
    print(f"  scratch: {(df_inspect['defect_type']=='scratch').sum()}건")
    print()

    # 이벤트 구간 불량률
    df_inspect["minute"] = [(pd.Timestamp(t) - pd.Timestamp(START)).total_seconds() / 60
                            for t in df_inspect["inspected_at"]]
    for evt in EVENTS:
        mask = (df_inspect["minute"] >= evt["start_min"]) & (df_inspect["minute"] <= evt["recover_min"])
        subset = df_inspect[mask]
        evt_defects = (subset["verdict"] == "defect").sum()
        print(f"이벤트 '{evt['name']}' ({evt['start_min']}~{evt['recover_min']}분):")
        print(f"  {len(subset)}건 중 불량 {evt_defects}건 ({evt_defects/max(len(subset),1):.1%})")

    print(f"\n저장 위치: {out}")
    print(f"  sim_process_params.csv ({df_process.shape})")
    print(f"  sim_inspection_results.csv ({df_inspect.shape})")


if __name__ == "__main__":
    main()
