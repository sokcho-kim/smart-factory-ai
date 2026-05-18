"""NEU Surface Defect YOLO v8n-cls 6클래스 학습.

목표: val top-1 90%+, per-class precision 85%+
최대 3회 시도, 하이퍼파라미터 조정 후 최고 결과 채택.

근거:
- 입력 200×200 원본 → 224×224로 약간 업스케일 (YOLO-cls 기본). 텍스처가 핵심이라 더 키워도 정보가 늘진 않음.
  → 시도 2/3은 더 큰 imgsz를 시도해 텍스처 디테일 보존 효과 비교.
- batch 64: 동일.
- AdamW + cosine: 동일.
- HSV는 약하게 — 회색 스케일 텍스처라 색조 변동이 의미 약함. v(value)만 살짝.
- fliplr 0.5, flipud 0.5 — 강판 결함은 상하/좌우 대칭이 자연스러움.
- erasing 0.2 — 결함 일부 가려도 분류 가능하게.
- mixup 0.1 — 시도 2/3에서 추가, 클래스 경계 모호한 케이스(crazing vs rolled-in_scale) 보강.

시도 전략:
  attempt 1: 224×224 baseline
  attempt 2: 320×320 + mixup 0.1  (텍스처 디테일 + augmentation 강화)
  attempt 3: 320×320 + lr 5e-4 + label_smoothing 0.1  (수렴 안정성)
"""
from pathlib import Path
import argparse
import json
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "neu_cls"
WEIGHTS = ROOT / "models" / "yolov8n-cls.pt"
RUNS = ROOT / "results" / "neu"


def train(run_name: str, imgsz: int, epochs: int, lr0: float, weight_decay: float,
          mixup: float = 0.0, label_smoothing: float = 0.0,
          degrees: float = 10.0, hsv_v: float = 0.3, erasing: float = 0.2,
          translate: float = 0.1, scale: float = 0.5):
    model = YOLO(str(WEIGHTS))
    results = model.train(
        data=str(DATA),
        imgsz=imgsz,
        epochs=epochs,
        batch=64,
        optimizer="AdamW",
        lr0=lr0,
        lrf=0.01,
        weight_decay=weight_decay,
        cos_lr=True,
        patience=15,
        hsv_h=0.0, hsv_s=0.0, hsv_v=hsv_v,
        fliplr=0.5, flipud=0.5,
        degrees=degrees,
        translate=translate,
        scale=scale,
        erasing=erasing,
        mixup=mixup,
        label_smoothing=label_smoothing,
        project=str(RUNS),
        name=run_name,
        exist_ok=True,
        device=0,
        workers=4,
        seed=42,
        verbose=True,
    )
    metrics = model.val(data=str(DATA), imgsz=imgsz, batch=64, project=str(RUNS), name=run_name + "_val", exist_ok=True, device=0)
    return {
        "top1": float(metrics.top1),
        "top5": float(metrics.top5),
        "fitness": float(metrics.fitness),
        "best_weights": str(Path(results.save_dir) / "weights" / "best.pt"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt", type=int, required=True, choices=[1, 2, 3])
    args = ap.parse_args()

    # attempt 1: clean baseline 100% but fragile (medium aug acc = 70%)
    # attempt 2: aggressive augmentation to improve robustness under rotation/brightness/blur
    # attempt 3: even stronger + label smoothing for confidence calibration
    configs = {
        1: dict(run_name="attempt1_baseline",        imgsz=224, epochs=40, lr0=1e-3, weight_decay=5e-4),
        2: dict(run_name="attempt2_strong_aug",      imgsz=320, epochs=60, lr0=1e-3, weight_decay=5e-4,
                mixup=0.15, degrees=25.0, hsv_v=0.5, erasing=0.4, translate=0.2, scale=0.7),
        3: dict(run_name="attempt3_strong_aug_smooth", imgsz=320, epochs=80, lr0=5e-4, weight_decay=1e-3,
                mixup=0.2, degrees=30.0, hsv_v=0.5, erasing=0.4, translate=0.2, scale=0.7,
                label_smoothing=0.1),
    }
    cfg = configs[args.attempt]
    print(f"[attempt {args.attempt}] {cfg}")
    out = train(**cfg)
    print(json.dumps(out, indent=2))

    summary = RUNS / "summary.json"
    history = json.loads(summary.read_text()) if summary.exists() else {}
    history[f"attempt{args.attempt}"] = {"config": cfg, "result": out}
    summary.write_text(json.dumps(history, indent=2))


if __name__ == "__main__":
    main()
