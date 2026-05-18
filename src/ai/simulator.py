"""
PunchLine 실시간 시뮬레이터
CSV 데이터를 DB에 한 건씩 INSERT하여 공장 가동을 시뮬레이션한다.

사용법:
    python -m ai.simulator                  # 기본 1초 간격
    python -m ai.simulator --interval 0.5   # 0.5초 간격
    python -m ai.simulator --batch 10       # 10건씩 배치
    python -m ai.simulator --speed 10       # 10배속 (0.1초 간격)
"""
from __future__ import annotations

import argparse
import csv
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2

DB_URL = "postgresql://punchline:punchline123@localhost:5433/punchline"
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sample"


def parse_args():
    p = argparse.ArgumentParser(description="PunchLine 실시간 시뮬레이터")
    p.add_argument("--interval", type=float, default=1.0, help="INSERT 간격 (초)")
    p.add_argument("--speed", type=float, default=None, help="배속 (interval 대신 사용)")
    p.add_argument("--batch", type=int, default=1, help="한 번에 INSERT할 건수")
    p.add_argument("--reset", action="store_true", help="기존 데이터 삭제 후 시작")
    p.add_argument("--offset", type=int, default=0, help="CSV 시작 행 (이어하기)")
    return p.parse_args()


def load_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def remap_timestamp(original: str, base_original: str, base_now: datetime) -> datetime:
    """CSV 원본 타임스탬프를 현재 시각 기준으로 재매핑."""
    orig = datetime.fromisoformat(original)
    base = datetime.fromisoformat(base_original)
    delta = orig - base
    return base_now + delta


def insert_inspection(cur, row: dict, ts: datetime):
    cur.execute(
        """INSERT INTO inspection_results
           (inspected_at, line_id, verdict, defect_type, confidence)
           VALUES (%s, %s, %s, %s, %s)""",
        (
            ts,
            row["line_id"],
            row["verdict"],
            row.get("defect_type") or None,
            float(row["confidence"]),
        ),
    )


def insert_process(cur, row: dict, ts: datetime):
    cur.execute(
        """INSERT INTO process_params
           (recorded_at, line_id, mold_temp, injection_pressure,
            injection_speed, cooling_time, humidity, ambient_temp)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            ts,
            row["line_id"],
            float(row["mold_temp"]),
            float(row["injection_pressure"]),
            float(row["injection_speed"]),
            float(row["cooling_time"]),
            float(row["humidity"]),
            float(row["ambient_temp"]),
        ),
    )


def main():
    args = parse_args()
    interval = (1.0 / args.speed) if args.speed else args.interval

    insp_rows = load_csv(DATA_DIR / "sim_inspection_results.csv")
    proc_rows = load_csv(DATA_DIR / "sim_process_params.csv")

    if not insp_rows:
        print("CSV 데이터 없음")
        sys.exit(1)

    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()

    if args.reset:
        cur.execute("TRUNCATE inspection_results, process_params RESTART IDENTITY")
        print("[RESET] tables truncated")

    base_original = insp_rows[0]["inspected_at"]
    base_now = datetime.now()
    total = len(insp_rows)

    print(f"[SIM] start: {total} rows, interval={interval:.2f}s, batch={args.batch}")
    print(f"[SIM] original={base_original} -> now={base_now.isoformat(timespec='seconds')}")

    idx = args.offset
    inserted = 0

    try:
        while idx < total:
            batch_end = min(idx + args.batch, total)

            for i in range(idx, batch_end):
                ts = remap_timestamp(insp_rows[i]["inspected_at"], base_original, base_now)
                insert_inspection(cur, insp_rows[i], ts)

                if i < len(proc_rows):
                    proc_ts = remap_timestamp(proc_rows[i]["recorded_at"], base_original, base_now)
                    insert_process(cur, proc_rows[i], proc_ts)

                inserted += 1

            verdict_summary = insp_rows[batch_end - 1]["verdict"]
            defect_info = f" [{insp_rows[batch_end - 1].get('defect_type', '')}]" if verdict_summary == "defect" else ""

            print(
                f"  [{inserted:>4}/{total}] "
                f"{ts.strftime('%H:%M:%S')} "
                f"{verdict_summary.upper()}{defect_info} "
                f"(conf: {float(insp_rows[batch_end - 1]['confidence']):.3f})",
                flush=True,
            )

            idx = batch_end
            if idx < total:
                time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n[SIM] stopped: {inserted} rows inserted (resume with --offset {idx})")
    finally:
        cur.close()
        conn.close()

    print(f"[SIM] done: {inserted} rows inserted")


if __name__ == "__main__":
    main()
