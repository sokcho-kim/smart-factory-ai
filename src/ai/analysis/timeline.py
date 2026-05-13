"""시계열 품질 추적 모듈.

검사 결과 데이터를 시간 단위로 집계하여
불량률 추이, 불량 유형 분포, 이상 구간 탐지를 제공한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import pandas as pd


@dataclass
class TimelineEntry:
    timestamp: str
    line_id: str
    total: int
    defects: int
    defect_rate: float
    top_defect_type: str | None
    by_type: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "line_id": self.line_id,
            "total": self.total,
            "defects": self.defects,
            "defect_rate": round(self.defect_rate, 4),
            "top_defect_type": self.top_defect_type,
            "by_type": self.by_type,
        }


@dataclass
class TimelineSummary:
    total_inspected: int
    total_defects: int
    overall_defect_rate: float
    peak_time: str | None
    peak_defect_rate: float
    dominant_defect_type: str | None

    def to_dict(self) -> dict:
        return {
            "total_inspected": self.total_inspected,
            "total_defects": self.total_defects,
            "overall_defect_rate": round(self.overall_defect_rate, 4),
            "peak_time": self.peak_time,
            "peak_defect_rate": round(self.peak_defect_rate, 4),
            "dominant_defect_type": self.dominant_defect_type,
        }


@dataclass
class AnomalyAlert:
    timestamp: str
    line_id: str
    defect_rate: float
    window_defects: int
    window_total: int
    message: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "line_id": self.line_id,
            "defect_rate": round(self.defect_rate, 4),
            "window_defects": self.window_defects,
            "window_total": self.window_total,
            "message": self.message,
        }


@dataclass
class TimelineData:
    entries: list[TimelineEntry]
    summary: TimelineSummary
    alerts: list[AnomalyAlert] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "summary": self.summary.to_dict(),
            "alerts": [a.to_dict() for a in self.alerts],
        }


class TimelineTracker:
    """검사 결과를 시간 단위로 집계하는 품질 추적기."""

    def __init__(self, alert_threshold: float = 0.10, alert_window: int = 10):
        """
        Args:
            alert_threshold: 이 불량률 초과 시 알림 (기본 10%)
            alert_window: 알림 판단 윈도우 크기 (건수)
        """
        self.alert_threshold = alert_threshold
        self.alert_window = alert_window

    def aggregate(
        self,
        inspect_df: pd.DataFrame,
        line_id: str = "A",
        freq: str = "15min",
    ) -> TimelineData:
        """검사 결과를 시간 구간별로 집계."""
        df = inspect_df.copy()
        df["ts"] = pd.to_datetime(df["inspected_at"])
        df["is_defect"] = (df["verdict"] == "defect").astype(int)

        if line_id:
            df = df[df["line_id"] == line_id]

        df = df.set_index("ts").sort_index()

        # 시간 구간별 집계
        grouped = df.resample(freq)
        entries = []

        for ts, group in grouped:
            if len(group) == 0:
                continue

            total = len(group)
            defects = group["is_defect"].sum()
            rate = defects / total if total > 0 else 0.0

            # 불량 유형별 건수
            by_type = {}
            if defects > 0:
                type_counts = group.loc[group["is_defect"] == 1, "defect_type"].value_counts()
                by_type = type_counts.to_dict()

            top_type = max(by_type, key=by_type.get) if by_type else None

            entries.append(TimelineEntry(
                timestamp=ts.isoformat(),
                line_id=line_id,
                total=int(total),
                defects=int(defects),
                defect_rate=float(rate),
                top_defect_type=top_type,
                by_type={k: int(v) for k, v in by_type.items()},
            ))

        # 전체 요약
        total_all = int(df["is_defect"].count())
        defects_all = int(df["is_defect"].sum())
        rate_all = defects_all / total_all if total_all > 0 else 0.0

        peak_entry = max(entries, key=lambda e: e.defect_rate) if entries else None

        # 전체 불량 유형 1위
        if defects_all > 0:
            all_types = df.loc[df["is_defect"] == 1, "defect_type"].value_counts()
            dominant = all_types.index[0] if len(all_types) > 0 else None
        else:
            dominant = None

        summary = TimelineSummary(
            total_inspected=total_all,
            total_defects=defects_all,
            overall_defect_rate=rate_all,
            peak_time=peak_entry.timestamp if peak_entry else None,
            peak_defect_rate=peak_entry.defect_rate if peak_entry else 0.0,
            dominant_defect_type=dominant,
        )

        # 알림 탐지
        alerts = self._detect_alerts(df, line_id)

        return TimelineData(entries=entries, summary=summary, alerts=alerts)

    def shift_comparison(
        self,
        inspect_df: pd.DataFrame,
        line_id: str = "A",
        shift_hours: tuple[tuple[int, int], ...] = ((6, 14), (14, 22), (22, 6)),
        shift_names: tuple[str, ...] = ("주간조", "야간조", "심야조"),
    ) -> list[dict]:
        """교대조별 품질 비교."""
        df = inspect_df.copy()
        df["ts"] = pd.to_datetime(df["inspected_at"])
        df["hour"] = df["ts"].dt.hour
        df["is_defect"] = (df["verdict"] == "defect").astype(int)

        if line_id:
            df = df[df["line_id"] == line_id]

        results = []
        for (start, end), name in zip(shift_hours, shift_names):
            if start < end:
                mask = (df["hour"] >= start) & (df["hour"] < end)
            else:
                mask = (df["hour"] >= start) | (df["hour"] < end)

            subset = df[mask]
            total = len(subset)
            defects = subset["is_defect"].sum()

            results.append({
                "shift": name,
                "hours": f"{start:02d}:00~{end:02d}:00",
                "total": int(total),
                "defects": int(defects),
                "defect_rate": round(defects / total, 4) if total > 0 else 0.0,
            })

        return results

    def hourly_pattern(
        self,
        inspect_df: pd.DataFrame,
        line_id: str = "A",
    ) -> list[dict]:
        """시간대별(hour) 불량률 패턴."""
        df = inspect_df.copy()
        df["ts"] = pd.to_datetime(df["inspected_at"])
        df["hour"] = df["ts"].dt.hour
        df["is_defect"] = (df["verdict"] == "defect").astype(int)

        if line_id:
            df = df[df["line_id"] == line_id]

        hourly = df.groupby("hour").agg(
            total=("is_defect", "count"),
            defects=("is_defect", "sum"),
        )
        hourly["defect_rate"] = hourly["defects"] / hourly["total"]

        return [
            {
                "hour": int(h),
                "total": int(row["total"]),
                "defects": int(row["defects"]),
                "defect_rate": round(float(row["defect_rate"]), 4),
            }
            for h, row in hourly.iterrows()
        ]

    def _detect_alerts(
        self, df: pd.DataFrame, line_id: str
    ) -> list[AnomalyAlert]:
        """슬라이딩 윈도우로 불량률 급증 구간 탐지."""
        alerts = []
        values = df["is_defect"].values
        timestamps = df.index

        w = self.alert_window
        in_alert = False

        for i in range(w, len(values)):
            window = values[i - w: i]
            window_defects = int(window.sum())
            window_rate = window_defects / w

            if window_rate > self.alert_threshold and not in_alert:
                in_alert = True
                ts = timestamps[i]
                alerts.append(AnomalyAlert(
                    timestamp=ts.isoformat(),
                    line_id=line_id,
                    defect_rate=float(window_rate),
                    window_defects=window_defects,
                    window_total=w,
                    message=f"불량률 급증: 최근 {w}건 중 {window_defects}건 불량 ({window_rate:.0%})",
                ))
            elif window_rate <= self.alert_threshold:
                in_alert = False

        return alerts


def run_demo():
    """시뮬레이션 데이터로 데모."""
    from pathlib import Path
    import json

    data_dir = Path(__file__).resolve().parents[3] / "data" / "sample"
    inspect_df = pd.read_csv(data_dir / "sim_inspection_results.csv")

    tracker = TimelineTracker(alert_threshold=0.10, alert_window=20)

    # 15분 단위 집계
    timeline = tracker.aggregate(inspect_df, line_id="A", freq="15min")

    print("=== 전체 요약 ===")
    s = timeline.summary
    print(f"  검사: {s.total_inspected}건, 불량: {s.total_defects}건 ({s.overall_defect_rate:.1%})")
    print(f"  피크: {s.peak_time} ({s.peak_defect_rate:.1%})")
    print(f"  주 불량 유형: {s.dominant_defect_type}")

    print(f"\n=== 시간 구간별 ({len(timeline.entries)}개) ===")
    for e in timeline.entries:
        bar = "#" * int(e.defect_rate * 50)
        ts_short = e.timestamp[11:16]
        flag = " !!!" if e.defect_rate > 0.10 else ""
        print(f"  {ts_short}  {e.defect_rate:5.1%} [{bar:25s}] {e.defects}/{e.total}{flag}")

    print(f"\n=== 알림 ({len(timeline.alerts)}건) ===")
    for a in timeline.alerts:
        print(f"  {a.timestamp[11:19]}  {a.message}")

    # 시간대별 패턴
    print("\n=== 시간대별 불량률 ===")
    hourly = tracker.hourly_pattern(inspect_df)
    for h in hourly:
        bar = "#" * int(h["defect_rate"] * 50)
        print(f"  {h['hour']:02d}시  {h['defect_rate']:5.1%} [{bar:25s}] {h['defects']}/{h['total']}")

    # JSON 출력 예시
    print("\n=== API 응답 크기 ===")
    payload = json.dumps(timeline.to_dict(), ensure_ascii=False)
    print(f"  {len(payload):,} bytes, {len(timeline.entries)} entries, {len(timeline.alerts)} alerts")


if __name__ == "__main__":
    run_demo()
