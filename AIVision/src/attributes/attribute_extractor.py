"""Extracts human-readable attributes from a cropped detection.

Person -> shirt color, pant color, cap (heuristic), bag (placeholder hook)
Vehicle -> dominant color, vehicle type (from class id)

The cap/bag heuristics here are intentionally simple (region-based color and
edge-density checks) so the pipeline is runnable without extra training data.
They're clearly marked as the place to swap in a proper classifier later
(e.g. a small CNN trained on cropped head/torso regions) without touching the
rest of the pipeline.
"""

import cv2
import numpy as np

from src.attributes.color_utils import get_dominant_color

# COCO class ids relevant to this pipeline.
PERSON_CLASS_ID = 0
VEHICLE_CLASS_NAMES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


class AttributeExtractor:
    def __init__(self, color_k_clusters: int = 3, min_crop_size: int = 20):
        self.k = color_k_clusters
        self.min_crop_size = min_crop_size

    def extract(self, crop_bgr: np.ndarray, class_id: int) -> dict:
        """Return an attribute dict appropriate for the detected object's class."""
        h, w = crop_bgr.shape[:2] if crop_bgr is not None else (0, 0)
        if crop_bgr is None or h < self.min_crop_size or w < self.min_crop_size:
            return {}

        if class_id == PERSON_CLASS_ID:
            return self._extract_person_attributes(crop_bgr)
        elif class_id in VEHICLE_CLASS_NAMES:
            return self._extract_vehicle_attributes(crop_bgr, class_id)
        return {}

    def _extract_person_attributes(self, crop_bgr: np.ndarray) -> dict:
        h, w = crop_bgr.shape[:2]

        # Rough body-region split. Assumes a fairly tight upright person bbox,
        # which is what YOLO + tracking typically produce for CCTV footage.
        head_region = crop_bgr[0:int(h * 0.15), :]
        shirt_region = crop_bgr[int(h * 0.20):int(h * 0.55), :]
        pant_region = crop_bgr[int(h * 0.55):int(h * 0.95), :]

        shirt_color = get_dominant_color(shirt_region, self.k)
        pant_color = get_dominant_color(pant_region, self.k)
        cap = self._has_cap(head_region)
        bag = self._has_bag_placeholder()

        return {
            "object_type": "person",
            "shirt_color": shirt_color,
            "pant_color": pant_color,
            "cap": cap,
            "bag": bag,
        }

    def _extract_vehicle_attributes(self, crop_bgr: np.ndarray, class_id: int) -> dict:
        color = get_dominant_color(crop_bgr, self.k)
        return {
            "object_type": "vehicle",
            "vehicle_type": VEHICLE_CLASS_NAMES.get(class_id, "unknown"),
            "color": color,
        }

    @staticmethod
    def _has_cap(head_region: np.ndarray) -> bool:
        """Heuristic: a cap tends to make the very top strip of the head region
        saturated and uniform, unlike hair/skin tones. This is a coarse proxy,
        not a trained classifier — swap in a real cap/no-cap classifier for
        production accuracy.
        """
        if head_region.size == 0:
            return False
        hsv = cv2.cvtColor(head_region, cv2.COLOR_BGR2HSV)
        top_strip = hsv[0:max(1, hsv.shape[0] // 2), :]
        mean_saturation = float(np.mean(top_strip[:, :, 1]))
        std_hue = float(np.std(top_strip[:, :, 0]))
        # High, uniform saturation with low hue variance suggests a solid-color
        # cap fabric rather than varied hair/skin texture.
        return mean_saturation > 80 and std_hue < 25

    @staticmethod
    def _has_bag_placeholder() -> bool:
        """Placeholder for bag detection.

        Reliable bag detection needs either (a) a secondary object detector
        trained on bags/backpacks run on the torso+lower-body region, or
        (b) a multi-label attribute classifier (e.g. a small ResNet fine-tuned
        on a pedestrian-attribute dataset like PA-100K or PETA). Returning
        False by default keeps the schema stable for Member 2/3 until that
        model is plugged in here.
        """
        return False
