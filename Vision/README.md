# Vision — PunchLine Vision Engine

> 담당: 원정환 (Vision & Detection Engine)
> 대회: 차세대융합기술연구원 메이커스페이스 해커톤 (본선 2026-05-22)

이 폴더는 PunchLine 프로젝트의 **Vision Engine** 전담 작업 공간입니다.
파이프라인의 첫 단계 — 카메라 이미지 → 양품/불량 판정 + 결함 유형 분류 + 결함 위치(bbox/heatmap) — 를 모두 담당합니다.

## 폴더 구조

```
Vision/
├── README.md                       # 이 파일
├── docs/
│   ├── 01_project_understanding.md     # 전체 프로젝트 이해
│   ├── 02_integration_with_jimin.md    # 지민 파트와의 결합 지점
│   ├── 03_enhancement_analysis.md      # 프로젝트 완성도를 위한 보강안
│   ├── 04_my_roadmap.md                # 정환 개인 로드맵 (전체 + α)
│   └── progress/
│       ├── 2026-05-13_phase0_env.md    # Phase 0 환경 세팅
│       ├── 2026-05-14_phase0_data.md   # Phase 0 데이터 확보
│       ├── 2026-05-15_casting_yolo.md  # Casting Defect YOLO 학습
│       └── 2026-05-16_neu_yolo.md      # NEU Surface Defect 분류
├── src/                            # 학습/추론/유틸 스크립트
├── data/
│   ├── raw/                        # 원본 데이터셋
│   └── processed/                  # YOLO 포맷 변환된 데이터
├── models/                         # 학습된 가중치 (best.pt)
├── results/                        # 학습 결과 (mAP, 혼동행렬, 샘플 추론)
└── notebooks/                      # EDA/실험용 노트북
```

## 진행 순서

1. `docs/01_project_understanding.md` 부터 순서대로 읽기
2. `docs/04_my_roadmap.md` — 오늘 무엇을 해야 하는지
3. `docs/progress/` — 실제 실행 로그
