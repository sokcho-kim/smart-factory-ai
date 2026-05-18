# 04. 정환 개인 로드맵 (전체 로드맵 + α)

## 큰 방향성

- **전체 로드맵을 절대 어기지 않는다.** 날짜별 체크포인트(5/18 모듈 독립, 5/20 E2E, 5/21 리허설)는 동일.
- 각 날짜 **안에서** 기존 작업 + α(보강 작업)를 끼워 넣는다.
- 시연 임팩트(35) + AI 정확도(25) 합 60점을 직접 책임진다는 자각으로 작업.

## 색상 범례

- 🟦 **[기존]** — MILESTONES에 명시된 작업
- 🟩 **[+α]** — 03_enhancement_analysis 기반 추가
- ⚡ **[크리티컬]** — 빠지면 시연 부서짐

---

## Phase 0: 환경 + 데이터 (5/13~14)

### 5/13 (수) — 환경 세팅
- 🟦 GitHub 레포 정리 (브랜치: main / dev / feat/vision)
- 🟦 Docker Compose 뼈대 (FastAPI + Streamlit + PostgreSQL)
- 🟩 Python venv + 패키지 고정 (`requirements.txt`)
- 🟩 GPU 확인 (RTX 3060 Ti, CUDA 동작) + Ultralytics smoke test

### 5/14 (목) — 데이터 확보
- 🟦 MVTec AD 다운로드 (`data/raw/mvtec_ad/`)
- 🟦 Casting Defect 다운로드 (`data/raw/casting/`)
- 🟦 NEU Surface Defect 다운로드 (`data/raw/neu/`)
- 🟦 YOLO v8n 학습 환경 smoke test (샘플 1 epoch)
- 🟩 데이터셋별 EDA — 클래스 분포 / 해상도 / 결함 면적 통계

**체크포인트 (5/14 저녁)**: GPU 동작 + 데이터 로컬 적재 + Ultralytics 1 epoch 동작 확인.

---

## Phase 1: 핵심 모델 (5/15~18)

### 5/15 (금) — Casting Defect YOLO ⚡
- 🟦 Casting Defect 학습 (양품/불량 이진)
  - 모델: YOLO v8n-cls (분류 헤드)
  - 입력: 300×300
  - epochs: 50, batch: 64, optimizer: AdamW, lr0: 0.001
  - 데이터 증강: HSV, fliplr 0.5, mosaic 1.0
  - **목표 mAP 80%+ / val accuracy 90%+**
- 🟦 최대 3회 재학습, 최고 결과 채택
- 🟩 혼동행렬 + ROC 저장 (`results/casting/`)
- 🟩 sample inference 20장 캡처 (시연용 후보)

### 5/16 (토) — NEU Surface Defect 분류 ⚡ ← **오늘**
- 🟦 NEU 6종 결함 분류 학습
  - 모델: YOLO v8n-cls
  - 입력: 200×200 (NEU 원본 해상도)
  - epochs: 30, batch: 64, optimizer: AdamW, lr0: 0.001
  - **목표 val accuracy 90%+ / per-class precision 85%+**
- 🟦 최대 3회 재학습, 최고 결과 채택
- 🟩 라벨 표준화 매핑 작성 (`Cr→crack`, `In→inclusion` 등)
- 🟩 혼동행렬 + per-class 리포트 저장

### 5/17 (일) — PatchCore + α
- 🟦 PatchCore on MVTec AD (`bottle` 단일 클래스)
  - 양품 학습 → 불량 탐지 + heatmap
  - **목표 AUROC 95%+**
- 🟩 결함 유형 라벨 표준 (`defect_labels.json`) 확정 → 지민에게 전달
- 🟩 조치 가이드 텍스트 초안 8종 작성 → 지민에게 전달

### 5/18 (월) — FastAPI 추론 API ⚡
- 🟦 `POST /inspect` 엔드포인트
  - YOLO 분류 + PatchCore 이상 점수 통합
  - 응답 JSON 스키마 (02 문서)
- 🟦 응답 시간 < 200ms / 장
- 🟩 Mock 추론 결과 100건 생성 → 지민에게 전달
- 🟩 OpenAPI 문서 자동 생성 확인

**체크포인트 (5/18 저녁)**: 이미지 1장 → JSON 결과 + heatmap 풀체인 동작.

---

## Phase 2: 통합 + 대시보드 (5/19~20)

### 5/19 (화) — Streamlit 대시보드 (검사 화면 + 시계열)
- 🟦 좌상 패널: 실시간 검사 화면 (이미지 + bbox + verdict)
- 🟦 우상 패널: 시계열 불량률 차트 (Plotly)
- 🟩 Grad-CAM/Heatmap 오버레이 토글
- 🟩 신뢰도 게이지 + 결함 누적 미니맵
- 🟩 "누적 검사 N건 / 사람 입력 0건" 카운터 (KPI 스토리)
- 🟦 `st.session_state` 키 네임스페이스 `vision_*` 만 사용

### 5/20 (수) — E2E 통합 ⚡
- 🟦 시연 이미지 시퀀스 준비 (양품 50 → 불량 30 → 양품 50)
- 🟦 지민 패널 컴포넌트 머지 (좌하/우하)
- 🟦 E2E 1회 시연 성공 (이미지 → 판정 → 기록 → 원인 → 가이드)
- 🟩 시연 시퀀스와 시뮬 공정 데이터 시각 정합 검증

**체크포인트 (5/20 저녁)**: E2E 시연 1회 끊김 없이 완주.

---

## Phase 3: 안정화 + 리허설 (5/21)

### 5/21 (목) — 시연 안정화 ⚡
- 🟩 ONNX export + CPU 추론 30 FPS 검증 (본선 환경 헷지)
- 🟦 Docker Compose 클린 빌드 + 클린 환경 실행 테스트
- 🟦 시연 이미지 시퀀스 최종 확정
- 🟩 라이브 웹캠 1샷 데모 (선택)
- 🟦 리허설 2회 (시연 8분 + 발표 5분)
- 🟦 오프라인 모드 확인 (인터넷 끊고 동작)

**체크포인트 (5/21 밤)**: Docker 이미지 동결, 발표 대본 동결, 시연 시퀀스 동결.

---

## D-Day 5/22 — 본선

| 시간 | 작업 |
|------|------|
| 09:30 | Docker compose up 1발, 프로젝터 연결 |
| 10:00~12:00 | 마지막 통합 + 버그 수정 (정환은 비전 모듈 안정성 확인) |
| 13:00~15:00 | 리허설 + 시연 안정화 |
| 15:00~17:00 | 1차/2차 평가 |

---

## 정환이 양보해도 되는 / 양보 못 하는 작업

**양보 가능** (시간 부족 시 컷):
- Grad-CAM 오버레이
- 결함 누적 미니맵
- 라이브 웹캠 1샷 데모

**양보 불가** (이게 빠지면 본선 못 감):
- Casting + NEU 학습 결과 (5/15~16)
- FastAPI /inspect (5/18)
- 검사 화면 + 시계열 차트 (5/19)
- E2E 시연 1회 성공 (5/20)
- Docker 클린 빌드 (5/21)

---

## 진행 기록 규칙

매일 작업 끝나면 `docs/progress/YYYY-MM-DD_*.md` 에 다음을 기록:
- 실행 명령 (재현 가능하게)
- 시도한 파라미터 (3회 시도 모두)
- 결과 지표 (mAP, accuracy, AUROC, 추론 속도)
- 채택 결정 + 이유
- 다음 날 이어갈 포인트
