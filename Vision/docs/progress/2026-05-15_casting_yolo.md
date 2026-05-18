# 2026-05-15 — Phase 1 Day 1: Casting Defect YOLO v8n-cls 학습

## 목표
- Casting Defect 이진 분류 (양품 vs 불량) 학습
- 목표: **val top-1 accuracy 95%+**
- 최대 3회 시도, 최고 결과 채택

## 모델 선택 근거
- **YOLO v8n-cls** — Ultralytics classification 헤드, 분류 전용. detection 헤드보다 빠르고 가벼움.
- 이진 분류이므로 detection (bbox) 가 필요 없음 → cls가 정답.
- ImageNet pretrained backbone (1.4M params, 3.3 GFLOPs) → 7천 장 정도 데이터로도 빠르게 수렴.

## 하이퍼파라미터 근거

| 항목 | 값 | 이유 |
|------|----|----|
| imgsz | 224 | YOLO-cls 기본, ImageNet pretrained 일치, 추론 속도 |
| batch | 64 | RTX 3060 Ti 8GB에서 yolov8n은 64 여유 (실제 1.2GB 사용) |
| epochs | 30 (patience=10) | 작은 데이터 + pretrained → 빠르게 수렴 예상 |
| optimizer | AdamW | 작은 모델/데이터에서 SGD보다 안정적 |
| lr0 | 1e-3 | cosine schedule 기본값, 작은 모델에 적당 |
| weight_decay | 5e-4 | 과적합 방지 (이진 분류 + 7천 장은 과적합 위험) |
| cos_lr | True | LR cosine annealing, smoother convergence |
| HSV aug | h=0.015 s=0.7 v=0.4 | 조명/색조 변화 대비 (현장 조명 다양성) |
| fliplr | 0.5 | 좌우 대칭 (주조 제품은 좌우 대칭 형상) |
| erasing | 0.2 | Random Erasing 약하게 — 결함 일부 가려도 분류 가능하게 |

## 1차 시도 결과

```
configs[1] = imgsz=224, epochs=30, lr0=1e-3, wd=5e-4
```

**훈련 진행**:
- 학습 시작 ~ EarlyStopping(patience=10) 발동까지 25 epochs
- Best epoch: 15 — 이후 개선 없음
- 학습 시간: 0.073 hours ≈ **4분 24초**
- GPU memory: 1.21GB / 8GB (~15% 사용)

**최종 지표**:
- val top-1 accuracy: **1.0000 (100%)**
- val top-5 accuracy: 1.0000
- 추론 속도: **150 FPS** (224×224, RTX 3060 Ti, single image)

**혼동행렬** (val 715장):
```
                 pred_def    pred_ok
true_def_front    453         0
true_ok_front       0       262
```
- precision(def): 1.0000
- recall(def): 1.0000
- 양/불 모두 1건도 안 틀림

## 2/3차 시도 — 생략 결정

1차에서 **100% (천장)** 도달. 산술적으로 더 좋아질 수 없음.

생략 이유:
1. **headroom 0%** — accuracy 1.0이 상한, 추가 학습은 의미 없음
2. **overfitting 가속 우려** — 더 큰 imgsz/lr 조정은 train loss는 줄어들지만 val은 같거나 나빠질 가능성
3. **시간 절약** — 본선 D-6, 시간 자원 다른 곳에 투입이 합리적

→ **attempt 1 채택 확정**.

## 왜 100%가 나왔는가 (현실성 검토)

Casting Defect 데이터셋은 학계/Kaggle 사이에서 "비교적 쉬운 벤치마크"로 알려져 있다. 양/불 차이가 시각적으로 명확하고(블로우홀, 표면 균열 등 큰 결함), 조명/각도가 통일된 산업 카메라로 촬영됨.

**시연 시 주의**: 100% 라는 숫자를 그대로 보여주면 심사위원이 "현실성?" 의심할 수 있음. 발표 시:
- "본 벤치마크에서 100% 달성 — 다만 실제 현장은 조명/배경 변동성이 있어 augmentation 강화 필요" 라고 솔직하게 컨텍스트.
- 시연 데모에서는 "**신뢰도 게이지**" (0.99...) 로 보여주는 게 자연스러움.

## 산출물
- `results/casting/attempt1_baseline/weights/best.pt` (3.0MB)
- `results/casting/summary.json`
- 추후: ONNX export (5/21)

## 통합 인터페이스 (지민 파트 연결 메모)
- 이 모델 출력: `{"verdict": "OK"|"DEFECT", "confidence": float}` 형태로 wrap 예정 (5/18 FastAPI 작업 시)
- 라벨 매핑: `def_front → "DEFECT"`, `ok_front → "OK"`
- 5/17까지 결함 라벨 표준 (`defect_labels.json`) 작성, 그때 이 매핑도 명문화

## 다음 (5/16)
- NEU Surface Defect 6클래스 분류
- 데이터가 작음(1440 train) + 클래스 6개 → 100% 는 어려움
- 목표 val top-1 90%+, per-class precision 85%+
- 최대 3회 시도, 하이퍼파라미터 조정 (imgsz, lr, augmentation 강도)
