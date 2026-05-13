"""PunchLine AI Server — 비전 검사 + 원인 분석 API."""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PunchLine AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# TODO Phase 1: POST /inspect — 이미지 업로드 → YOLO 검사 → 판정 결과
# TODO Phase 1: POST /analyze/root-cause — 시간 구간 → SHAP 분석 → 원인 Top3
# TODO Phase 2: GET /quality/timeline — 시간대별 불량률 집계
# TODO Phase 2: GET /quality/report — 일일 품질 리포트
