"""Casting Defect YOLO v8n-cls 학습.

목표: val accuracy 95%+ (이진 분류는 NEU 6클래스보다 쉬움)
최대 3회 시도, 각 시도마다 하이퍼파라미터 조정. 최고 결과 채택.

근거:
- 입력 224×224: ImageNet pretrained와 일치, 추론 속도 vs 정확도 균형. 원본 300×300이지만
  YOLO-cls 기본이 224라 첫 시도는 224. 미달 시 320으로 키움.
- batch 64: RTX 3060 Ti 8GB에서 yolov8n-cls는 64까지 여유.
- AdamW + cosine LR: 작은 모델 + 작은 데이터에서 SGD보다 안정적.
- HSV augmentation: 조명 변화에 강건 (현장 조명 다양성 대비).
- mosaic 0.0 (cls 모드 기본): 분류에서 mosaic은 의미 약함.
- patience 10: 적절히 짧게.
"""
from pathlib import Path
import argparse
import json
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "casting_cls"
WEIGHTS = ROOT / "models" / "yolov8n-cls.pt"
RUNS = ROOT / "results" / "casting"


def train(run_name: str, imgsz: int, epochs: int, lr0: float, weight_decay: float):
    model = YOLO(str(WEIGHTS))
    results = model.train(
        data=str(DATA),
        imgsz=imgsz,
        epochs=epochs,
        batch=64,
        optimizer="AdamW",
        lr0=lr0,
        lrf=0.01,            # cosine final LR ratio
        weight_decay=weight_decay,
        cos_lr=True,
        patience=10,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        fliplr=0.5, flipud=0.0,
        erasing=0.2,         # cls-specific aug
        project=str(RUNS),
        name=run_name,
        exist_ok=True,
        device=0,
        workers=4,
        seed=42,
        verbose=True,
    )
    # final val metrics
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

    configs = {
        1: dict(run_name="attempt1_baseline", imgsz=224, epochs=30, lr0=1e-3, weight_decay=5e-4),
        2: dict(run_name="attempt2_imgsz320", imgsz=320, epochs=40, lr0=1e-3, weight_decay=5e-4),
        3: dict(run_name="attempt3_lowerLR",  imgsz=320, epochs=50, lr0=5e-4, weight_decay=1e-3),
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
