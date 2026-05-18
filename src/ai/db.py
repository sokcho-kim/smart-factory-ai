"""PunchLine DB 연결 — PostgreSQL에서 데이터를 읽어 DataFrame으로 반환."""
from __future__ import annotations

import os

import pandas as pd
import psycopg2

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://punchline:punchline123@localhost:5433/punchline",
)


def get_conn():
    return psycopg2.connect(DB_URL)


def read_inspections() -> pd.DataFrame:
    """inspection_results 테이블 전체를 DataFrame으로 반환."""
    conn = get_conn()
    try:
        df = pd.read_sql(
            "SELECT inspected_at, line_id, verdict, defect_type, confidence "
            "FROM inspection_results ORDER BY inspected_at",
            conn,
        )
        df["inspected_at"] = df["inspected_at"].astype(str)
        return df
    finally:
        conn.close()


def read_process_params() -> pd.DataFrame:
    """process_params 테이블 전체를 DataFrame으로 반환."""
    conn = get_conn()
    try:
        df = pd.read_sql(
            "SELECT recorded_at, line_id, mold_temp, injection_pressure, "
            "injection_speed, cooling_time, humidity, ambient_temp "
            "FROM process_params ORDER BY recorded_at",
            conn,
        )
        df["recorded_at"] = df["recorded_at"].astype(str)
        return df
    finally:
        conn.close()


def count_inspections() -> int:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM inspection_results")
        return cur.fetchone()[0]
    finally:
        conn.close()
