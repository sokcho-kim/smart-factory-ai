# PunchLine — 비전 검사 데이터셋 가이드

> 담당: 원정환 (Vision Engine)
> 작성일: 2026-05-13

## 목표

YOLO v8n 기반 제품 외관 결함 탐지 모델 학습에 필요한 데이터셋 확보.
MVP 기준: 양품/불량 판정 + 3종 이상 결함 유형 분류.

---

## Tier 1 — 반드시 확보 (MVP 핵심)

### 1. Casting Product Defect Dataset

- **출처**: Kaggle (ravirajsinh45)
- **URL**: https://www.kaggle.com/datasets/ravirajsinh45/real-life-industrial-dataset-of-casting-product
- **이미지**: 7,348장 (300x300 grayscale)
- **클래스**: 양품(ok) / 불량(defect) — 이진분류
- **크기**: ~100MB
- **로그인**: Kaggle 계정 필요
- **포맷**: 폴더 구조 (train/test, ok_front/def_front)
- **용도**: YOLO 첫 학습, 양품/불량 판정 정확도 확보
- **난이도**: 낮음 — 이진분류라 빠르게 결과 확인 가능

### 2. NEU Surface Defect Database

- **출처**: Kaggle (kaustubhdikshit) / Northeastern University
- **URL**: https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database
- **이미지**: 1,800장 (200x200 grayscale)
- **클래스**: 6종
  - Cr (크랙)
  - In (개재물)
  - Pa (패치)
  - PS (피팅)
  - RS (압연 스케일)
  - Sc (스크래치)
- **크기**: ~28MB
- **로그인**: Kaggle 계정 필요
- **포맷**: 클래스별 폴더 (각 300장)
- **용도**: 결함 유형 분류, 바운딩박스 탐지
- **난이도**: 중 — 6종 분류이지만 데이터 수가 적어 augmentation 필요

---

## Tier 2 — 차별화 (시간 여유 시)

### 3. CSDD (Casting Surface Defect Dataset, 2025)

- **출처**: IEEE Journal of Automation Sinica / GitHub
- **URL**: https://github.com/Kerio99/CSDD
- **이미지**: 2,100장 (고해상도)
- **어노테이션**: 56,356개 결함 인스턴스
- **클래스**: 주조 표면 결함 다종
- **용도**: 세밀한 결함 위치 특정, 세그멘테이션
- **특징**: 2025년 발표, YOLO 벤치마크 논문에서 직접 사용
- **참고 논문**: https://www.ieee-jas.net/article/doi/10.1109/JAS.2025.125228

### 4. Roboflow Universe — Manufacturing Defect

- **출처**: Roboflow Universe
- **URL**: https://universe.roboflow.com/search?q=class%3Adefect
- **장점**: YOLO 포맷(txt 라벨)으로 바로 다운로드 가능, augmentation 내장
- **추천 검색어**: "manufacturing defect", "casting defect", "metal surface"
- **용도**: 추가 학습 데이터, 다양한 도메인 결함 이미지 확보
- **주의**: 데이터셋마다 품질 편차가 큼, 미리보기로 확인 후 다운로드

---

## Tier 3 — 이상 탐지 전용

### 5. MVTec AD (Anomaly Detection)

- **출처**: MVTec / Kaggle
- **URL**: https://www.kaggle.com/datasets/ipythonx/mvtec-ad
- **이미지**: 5,354장 (고해상도 컬러)
- **카테고리**: 15종 산업 제품 (병, 케이블, 캡슐, 카펫, 그리드, 가죽, 금속너트, 나사, 타일, 나무 등)
- **크기**: ~5GB
- **로그인**: Kaggle 계정 필요
- **용도**: PatchCore / STFPM 이상 탐지 학습
- **특징**: 양품만 학습 → 불량 자동 탐지 (제품 도면 불필요)
- **담당**: 지민 또는 정환 (협의)

---

## YOLO 학습 순서 권장

```
Week 1 (5/14~16):
  1. Casting Defect → YOLO v8n 이진분류 (양품/불량)
     목표: mAP 85%+
     예상 소요: 학습 1~2시간, 검증 포함 반나절

  2. NEU Surface Defect → YOLO v8n 6종 분류
     목표: mAP 70%+
     예상 소요: augmentation 포함 하루

Week 1 후반 (5/17~18):
  3. 두 모델 통합 추론 파이프라인
     이미지 입력 → 불량 판정 → 유형 분류 → JSON 출력
  
  4. (여유시) CSDD 또는 Roboflow 추가 데이터로 fine-tune
```

---

## API 인터페이스 (지민-정환 합의용)

정환이 만드는 Vision Engine의 출력 형식:

```json
POST /inspect
Content-Type: multipart/form-data (이미지 파일)

Response:
{
  "verdict": "defect",
  "defect_type": "crack",
  "confidence": 0.94,
  "bbox": {
    "x": 120,
    "y": 85,
    "w": 60,
    "h": 45
  },
  "inspected_at": "2026-05-15T09:42:13Z"
}
```

verdict 값:
- `"ok"` — 양품
- `"defect"` — 불량

defect_type 값 (NEU 기준):
- `"crack"` — 크랙
- `"inclusion"` — 개재물
- `"patch"` — 패치
- `"pitting"` — 피팅
- `"rolled_scale"` — 압연 스케일
- `"scratch"` — 스크래치

verdict가 `"ok"`이면 defect_type, bbox는 null.

---

## 다운로드 체크리스트

- [ ] Casting Defect (Kaggle, ~100MB) → `data/raw/casting/`
- [ ] NEU Surface Defect (Kaggle, ~28MB) → `data/raw/neu/`
- [ ] MVTec AD (Kaggle, ~5GB) → `data/raw/mvtec_ad/` (담당 협의)
- [ ] (선택) CSDD (GitHub) → `data/raw/csdd/`
- [ ] (선택) Roboflow 추가 데이터 → `data/raw/roboflow/`
