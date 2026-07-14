"""Debug why a specific crop's attributes came out wrong.

Draws the head/shirt/pant sample regions directly onto the crop and prints
the raw dominant RGB *before* it gets snapped to a named color — this
separates two very different bugs:
  - if the drawn regions don't line up with the actual shirt/pants in the
    image -> the bbox/region-ratio assumptions are wrong for this footage
  - if the regions look right but the RGB is still off -> background bleed,
    low light, or the color palette itself needs adjusting

Usage:
    python debug_attributes.py output/crops/cam_01_00214_000210.jpg
"""

import sys

import cv2

from src.attributes.color_utils import get_dominant_color


def debug_crop(crop_path: str, k: int = 3) -> None:
    crop = cv2.imread(crop_path)
    if crop is None:
        print(f"Could not read image: {crop_path}")
        return

    h, w = crop.shape[:2]
    print(f"\nCrop size: {w}x{h} px")
    if h < 40 or w < 20:
        print("⚠ This crop is very small — dominant-color clustering gets unreliable "
              "below roughly 40x20px. Consider raising min_crop_size or filtering out "
              "distant/small detections before attribute extraction.")

    regions = {
        "head (cap check)": (crop[0:int(h * 0.15), :], (0, 165, 255)),      # orange box
        "shirt": (crop[int(h * 0.20):int(h * 0.55), :], (0, 255, 0)),        # green box
        "pant": (crop[int(h * 0.55):int(h * 0.95), :], (255, 0, 0)),         # blue box
    }

    annotated = crop.copy()
    y_bounds = {
        "head (cap check)": (0, int(h * 0.15)),
        "shirt": (int(h * 0.20), int(h * 0.55)),
        "pant": (int(h * 0.55), int(h * 0.95)),
    }

    print("\nSampled regions vs. what they picked:")
    for label, (region, color) in regions.items():
        name, rgb = get_dominant_color(region, k=k, return_rgb=True)
        print(f"  {label:20s} -> dominant RGB {rgb} -> labeled '{name}'")

        y0, y1 = y_bounds[label]
        cv2.rectangle(annotated, (0, y0), (w - 1, y1), color, 2)
        cv2.putText(annotated, label, (2, y0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)

    out_path = crop_path.rsplit(".", 1)[0] + "_debug.jpg"
    cv2.imwrite(out_path, annotated)
    print(f"\nSaved region overlay to {out_path} — open it and check the boxes actually "
          f"cover the shirt/pants/head, not background or the wrong body part.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_attributes.py <path_to_crop.jpg>")
        sys.exit(1)
    debug_crop(sys.argv[1])
