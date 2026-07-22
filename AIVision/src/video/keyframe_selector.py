"""Module for image quality assessment and multi-keyframe selection."""

import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


def calculate_quality_metrics(crop_bgr: np.ndarray) -> dict:
    """Calculate blur, brightness, and sharpness metrics for a BGR crop.

    Returns a dict with:
        brightness (float): 0-255 scale
        sharpness (float): Laplacian variance score
        blur (float): inverse/related measure (lower is more blurry, same as sharpness)
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return {"brightness": 0.0, "sharpness": 0.0, "blur": 0.0}

    # Convert to grayscale
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)

    # Brightness is the average gray level
    brightness = float(np.mean(gray))

    # Sharpness is calculated using Laplacian variance
    # A higher variance means more high-frequency content (edges), hence sharper.
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Blur is inversely proportional, but for simple schemas we can map it to sharpness
    blur = sharpness

    return {
        "brightness": brightness,
        "sharpness": sharpness,
        "blur": blur
    }


def is_quality_acceptable(metrics: dict, config: dict) -> bool:
    """Check if the crop quality is within acceptable bounds from config.yaml."""
    q_cfg = config.get("quality", {})
    min_bright = q_cfg.get("min_brightness", 40.0)
    max_bright = q_cfg.get("max_brightness", 220.0)
    min_sharp = q_cfg.get("min_sharpness", 80.0)

    brightness = metrics["brightness"]
    sharpness = metrics["sharpness"]

    if brightness < min_bright or brightness > max_bright:
        return False
    if sharpness < min_sharp:
        return False

    return True


class KeyframeSelector:
    """Tracks and selects candidate keyframes for a track based on spatial features,

    chronology, and image quality metrics.
    """
    def __init__(self, config: dict):
        self.config = config
        # track_key -> dict of candidate crops:
        # {
        #   "all_crops": [(frame_idx, timestamp, crop_img, area, metrics, is_valid), ...],
        # }
        self.track_data = {}

    def add_frame_candidate(self, track_key: str, frame_idx: int, timestamp: str,
                             crop_bgr: np.ndarray, bbox_xyxy) -> None:
        """Evaluate an incoming frame crop and store it as a potential keyframe candidate."""
        if crop_bgr is None or crop_bgr.size == 0:
            return

        if track_key not in self.track_data:
            self.track_data[track_key] = {"all_crops": []}

        # Calculate metrics
        metrics = calculate_quality_metrics(crop_bgr)
        is_valid = is_quality_acceptable(metrics, self.config)

        x1, y1, x2, y2 = bbox_xyxy
        area = float((x2 - x1) * (y2 - y1))

        # To prevent memory bloat, we downsample the candidates.
        # We always keep the first, the latest, and any frames with high quality or area.
        # But we also sample periodically (e.g. every 5 frames) to get a good middle frame candidate.
        candidates = self.track_data[track_key]["all_crops"]
        
        # Determine if we should store it
        should_store = (
            len(candidates) == 0  # always store the first frame
            or frame_idx % 5 == 0  # sample every 5 frames for chronological coverage
            or is_valid  # store valid candidates
        )

        if should_store:
            # We copy the crop to avoid reference issues if the source frame is modified
            crop_copy = crop_bgr.copy()
            candidates.append((frame_idx, timestamp, crop_copy, area, metrics, is_valid))

            # Limit total crops per track in memory to 30 to avoid memory leak
            if len(candidates) > 30:
                # Keep first, keep last, and sort middle ones by area/quality
                first = candidates[0]
                last = candidates[-1]
                mid_candidates = candidates[1:-1]
                # Keep 28 best by quality score (sharpness)
                mid_candidates.sort(key=lambda x: x[4]["sharpness"], reverse=True)
                candidates = [first] + sorted(mid_candidates[:28], key=lambda x: x[0]) + [last]
                self.track_data[track_key]["all_crops"] = candidates

    def select_keyframes(self, track_key: str) -> dict:
        """Select 5 keyframes for a track:

        - first
        - middle
        - largest_bbox
        - last
        - highest_quality
        
        Returns a dict of keyframe_type -> {"frame_idx": int, "timestamp": str, "crop": np.ndarray, "metrics": dict, "quality_score": float}
        """
        if track_key not in self.track_data or not self.track_data[track_key]["all_crops"]:
            return {}

        candidates = self.track_data[track_key]["all_crops"]
        
        # Separate valid and invalid candidates
        valid_candidates = [c for c in candidates if c[5]]
        
        # Fallback to all candidates if no single frame passes quality rules
        pool = valid_candidates if valid_candidates else candidates

        # 1. First frame
        first_frame = pool[0]

        # 2. Last frame
        last_frame = pool[-1]

        # 3. Largest Bounding Box
        largest_frame = max(pool, key=lambda x: x[3])

        # 4. Highest Quality (Sharpness)
        highest_quality_frame = max(pool, key=lambda x: x[4]["sharpness"])

        # 5. Middle Frame
        # Find chronological middle of the pool
        mid_idx = len(pool) // 2
        middle_frame = pool[mid_idx]

        results = {
            "first": self._format_keyframe(first_frame),
            "middle": self._format_keyframe(middle_frame),
            "largest_bbox": self._format_keyframe(largest_frame),
            "last": self._format_keyframe(last_frame),
            "highest_quality": self._format_keyframe(highest_quality_frame)
        }

        logger.info("Track %s: Selected keyframes (First F#: %d, Mid F#: %d, Largest F#: %d, Last F#: %d, BestQ F#: %d)",
                    track_key, results["first"]["frame_idx"], results["middle"]["frame_idx"],
                    results["largest_bbox"]["frame_idx"], results["last"]["frame_idx"],
                    results["highest_quality"]["frame_idx"])

        return results

    def _format_keyframe(self, candidate_tuple) -> dict:
        frame_idx, timestamp, crop, area, metrics, is_valid = candidate_tuple
        return {
            "frame_idx": frame_idx,
            "timestamp": timestamp,
            "crop": crop,
            "metrics": metrics,
            "quality_score": metrics["sharpness"]
        }
