"""Casting Defect 원본을 YOLO-cls 폴더 구조로 복사.

원본:  data/raw/casting_repo/Casting data/{train,test}/{def_front,ok_front}/*.jpeg
출력:  data/processed/casting_cls/{train,val}/{def_front,ok_front}/
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "casting_repo" / "Casting data"
DST = ROOT / "data" / "processed" / "casting_cls"


def main():
    if not SRC.exists():
        print(f"[ERROR] source missing: {SRC}", file=sys.stderr)
        sys.exit(1)

    if DST.exists():
        shutil.rmtree(DST)

    mapping = {"train": "train", "test": "val"}
    counts = {}
    for src_split, dst_split in mapping.items():
        for cls in ("def_front", "ok_front"):
            src_dir = SRC / src_split / cls
            dst_dir = DST / dst_split / cls
            dst_dir.mkdir(parents=True, exist_ok=True)
            files = [f for f in src_dir.iterdir() if f.suffix.lower() in (".jpeg", ".jpg", ".png")]
            for f in files:
                shutil.copy(f, dst_dir / f.name)
            counts[f"{dst_split}/{cls}"] = len(files)

    for k, v in counts.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
