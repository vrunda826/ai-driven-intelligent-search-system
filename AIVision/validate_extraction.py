"""Visual + statistical QA for the ai-vision pipeline's output.

Run this after main.py to sanity-check that detection/tracking/attribute
extraction actually did the right thing, without opening dozens of files by hand.

What it does:
1. Prints summary stats (track counts per class, attribute distributions,
   suspiciously short/long tracks) to the console.
2. Builds a contact-sheet image: one thumbnail per sampled track, with its
   extracted attributes overlaid as text, so you can visually confirm
   "yes, that crop is actually a red shirt" at a glance.

Usage:
    python validate_extraction.py --config configs/config.yaml --sample 24
"""

import argparse
import json
import os
from collections import Counter

import cv2
import numpy as np

from src.utils.helpers import load_config


def load_metadata(metadata_dir: str) -> list:
    path = os.path.join(metadata_dir, "metadata.json")
    with open(path, "r") as f:
        return json.load(f)


def print_summary(records: list) -> None:
    print(f"\n=== Extraction summary ({len(records)} tracks) ===")

    class_counts = Counter(r.get("class", r.get("class_name")) for r in records)
    print("Tracks per class:", dict(class_counts))

    for attr_name in ("shirt", "pants", "shirt_color", "pant_color", "color", "vehicle_type"):
        values = []
        for r in records:
            attrs = r.get("appearance", r.get("attributes", {}))
            if attr_name in attrs and attrs[attr_name] != "unknown":
                values.append(attrs[attr_name])
        if values:
            print(f"  {attr_name} distribution:", dict(Counter(values)))

    cap_true = sum(1 for r in records if r.get("appearance", r.get("attributes", {})).get("cap") is True)
    bag_true = sum(1 for r in records if r.get("appearance", r.get("attributes", {})).get("bag") is True)
    print(f"  cap=True: {cap_true} / bag=True: {bag_true}")

    # Flag likely-noise tracks
    short_tracks = [r["track_id"] for r in records if r.get("num_observations", 5) < 3]
    if short_tracks:
        print(f"\n  [WARNING] {len(short_tracks)} tracks have <3 observations (possible false positives):")
        print("   ", short_tracks[:10], "..." if len(short_tracks) > 10 else "")

    no_crop_tracks = [r["track_id"] for r in records if not r.get("crop_paths")]
    if no_crop_tracks:
        print(f"  [WARNING] {len(no_crop_tracks)} tracks have no saved crop (can't be visually verified):")
        print("   ", no_crop_tracks[:10], "..." if len(no_crop_tracks) > 10 else "")


def build_contact_sheet(records: list, sample_size: int, thumb_size: int = 160,
                         cols: int = 6, output_path: str = "output/metadata/qa_contact_sheet.jpg") -> None:
    """Lay out sampled tracks' crops in a grid, each labeled with its attributes,
    so mismatches (e.g. a blue shirt labeled "red") are obvious on sight.
    """
    candidates = [r for r in records if r.get("crop_paths")]
    if not candidates:
        print("\nNo tracks with saved crops — nothing to build a contact sheet from.")
        return

    sample = candidates[:sample_size]
    rows = (len(sample) + cols - 1) // cols

    label_height = 40
    cell_h = thumb_size + label_height
    sheet = np.full((rows * cell_h, cols * thumb_size, 3), 255, dtype=np.uint8)

    for idx, record in enumerate(sample):
        crop_path = record["crop_paths"][0]
        if not os.path.exists(crop_path):
            continue
        crop = cv2.imread(crop_path)
        if crop is None:
            continue

        thumb = cv2.resize(crop, (thumb_size, thumb_size))
        row, col = divmod(idx, cols)
        y0, x0 = row * cell_h, col * thumb_size
        sheet[y0:y0 + thumb_size, x0:x0 + thumb_size] = thumb

        attrs = record.get("appearance", record.get("attributes", {}))
        line1 = record["track_id"]
        # extract up to 2 attributes
        line2 = ", ".join(f"{k}={v}" for k, v in list(attrs.items())[:2] if v != "unknown")
        cv2.putText(sheet, line1, (x0 + 4, y0 + thumb_size + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(sheet, line2, (x0 + 4, y0 + thumb_size + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1, cv2.LINE_AA)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, sheet)
    print(f"\nContact sheet saved to {output_path} — open it and check each label against its thumbnail.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA check for ai-vision extraction output.")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--sample", type=int, default=24, help="Number of tracks to include in the contact sheet")
    args = parser.parse_args()

    cfg = load_config(args.config)
    records = load_metadata(cfg["output"]["metadata_dir"])

    print_summary(records)
    build_contact_sheet(records, sample_size=args.sample,
                         output_path=os.path.join(cfg["output"]["metadata_dir"], "qa_contact_sheet.jpg"))
