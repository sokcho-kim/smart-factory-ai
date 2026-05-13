"""PunchLine API — 검사 결과 수신 + 품질 조회."""
from fastapi import FastAPI

app = FastAPI(title="PunchLine API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


# TODO Phase 1: POST /inspect — 비전 검사 결과 수신
# TODO Phase 2: GET /quality/timeline — 시계열 불량률
# TODO Phase 2: GET /quality/root-cause — 원인 분석 결과
