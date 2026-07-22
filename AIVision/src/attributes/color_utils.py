"""Dominant color extraction from an image patch, mapped to a human-readable color name.

Uses k-means clustering in RGB space to find the dominant color, then snaps it
to the closest entry in a small reference palette so downstream search/filtering
deals with clean labels ("red", "navy blue") instead of raw RGB triples.
"""

import cv2
import numpy as np
import logging
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, deltaE_ciede2000
import yaml
import os

logger = logging.getLogger(__name__)

def _load_ciede_sigma():
    try:
        config_path = "configs/config.yaml"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                cfg = yaml.safe_load(f)
            return float(cfg.get("confidence", {}).get("color_ciede_sigma", 15.0))
    except Exception:
        pass
    return 15.0

_CIEDE_SIGMA = _load_ciede_sigma()

def _load_skin_thresholds():
    try:
        config_path = "configs/config.yaml"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                cfg = yaml.safe_load(f)
            attr_cfg = cfg.get("attributes", {})
            return (
                int(attr_cfg.get("skin_cr_min", 133)),
                int(attr_cfg.get("skin_cr_max", 173)),
                int(attr_cfg.get("skin_cb_min", 77)),
                int(attr_cfg.get("skin_cb_max", 127))
            )
    except Exception:
        pass
    return 133, 173, 77, 127

_SKIN_CR_MIN, _SKIN_CR_MAX, _SKIN_CB_MIN, _SKIN_CB_MAX = _load_skin_thresholds()

# Reference palette: name -> approximate RGB. Expanded to 50 named colors.
_COLOR_REFERENCE = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "light gray": (211, 211, 211),
    "dark gray": (64, 64, 64),
    "charcoal": (54, 69, 79),
    "silver": (192, 192, 192),
    "red": (200, 30, 30),
    "crimson": (220, 20, 60),
    "brick red": (203, 65, 84),
    "maroon": (128, 0, 0),
    "burgundy": (128, 0, 32),
    "orange": (230, 126, 34),
    "coral": (255, 127, 80),
    "peach": (255, 218, 185),
    "apricot": (251, 206, 177),
    "rust": (183, 65, 14),
    "bronze": (205, 127, 50),
    "yellow": (230, 210, 40),
    "mustard": (227, 180, 72),
    "gold": (255, 215, 0),
    "green": (40, 140, 60),
    "lime": (0, 255, 0),
    "neon green": (57, 255, 20),
    "emerald": (80, 200, 120),
    "forest green": (34, 139, 34),
    "mint": (189, 252, 201),
    "olive": (110, 110, 40),
    "olive green": (85, 107, 47),
    "teal": (20, 130, 130),
    "turquoise": (64, 224, 208),
    "cyan": (0, 255, 255),
    "blue": (40, 90, 200),
    "light blue": (173, 216, 230),
    "sky blue": (135, 206, 235),
    "navy": (0, 0, 128),
    "navy blue": (20, 30, 90),
    "royal blue": (65, 105, 225),
    "indigo": (75, 0, 130),
    "purple": (120, 50, 150),
    "violet": (238, 130, 238),
    "lavender": (230, 230, 250),
    "plum": (221, 160, 221),
    "pink": (230, 130, 180),
    "salmon": (250, 128, 114),
    "magenta": (255, 0, 255),
    "brown": (110, 70, 40),
    "beige": (220, 200, 170),
    "tan": (210, 180, 140),
    "cream": (255, 253, 208),
}

# Collapse mapping to basic color buckets
_BASE_COLLAPSE = {
    "black": "black",
    "white": "white",
    "cream": "white",
    "gray": "gray",
    "light gray": "gray",
    "dark gray": "gray",
    "charcoal": "gray",
    "silver": "gray",
    "red": "red",
    "crimson": "red",
    "brick red": "red",
    "maroon": "red",
    "burgundy": "red",
    "orange": "orange",
    "coral": "orange",
    "peach": "orange",
    "apricot": "orange",
    "rust": "orange",
    "bronze": "orange",
    "yellow": "yellow",
    "mustard": "yellow",
    "gold": "yellow",
    "green": "green",
    "lime": "green",
    "neon green": "green",
    "emerald": "green",
    "forest green": "green",
    "mint": "green",
    "olive": "green",
    "olive green": "green",
    "teal": "blue",
    "turquoise": "blue",
    "cyan": "blue",
    "blue": "blue",
    "light blue": "blue",
    "sky blue": "blue",
    "navy": "blue",
    "navy blue": "blue",
    "royal blue": "blue",
    "indigo": "blue",
    "purple": "purple",
    "violet": "purple",
    "lavender": "purple",
    "plum": "purple",
    "pink": "pink",
    "salmon": "pink",
    "magenta": "pink",
    "brown": "brown",
    "beige": "brown",
    "tan": "brown",
}

def _load_sharpness_threshold():
    try:
        config_path = "configs/config.yaml"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                cfg = yaml.safe_load(f)
            return float(cfg.get("quality", {}).get("sharpness_min_for_finegrained", 120.0))
    except Exception:
        pass
    return 120.0

_SHARPNESS_MIN_FOR_FINEGRAINED = _load_sharpness_threshold()

# Precompute standard LAB values for the reference palette
_COLOR_REFERENCE_LAB = {}
for name, rgb in _COLOR_REFERENCE.items():
    rgb_arr = np.array([[[rgb[0], rgb[1], rgb[2]]]], dtype=np.uint8)
    _COLOR_REFERENCE_LAB[name] = rgb2lab(rgb_arr)[0, 0]

def _closest_color_name_with_distance(rgb) -> tuple:
    # Convert rgb to standard LAB
    rgb_arr = np.array([[[rgb[0], rgb[1], rgb[2]]]], dtype=np.uint8)
    dom_lab = rgb2lab(rgb_arr)[0, 0]

    best_name, best_dist = "unknown", float("inf")
    for name, ref_lab in _COLOR_REFERENCE_LAB.items():
        dist = float(deltaE_ciede2000(dom_lab, ref_lab))
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return best_name, best_dist


def _closest_color_name(rgb) -> str:
    name, _ = _closest_color_name_with_distance(rgb)
    return name


def get_dominant_color(image_patch_bgr: np.ndarray, k: int = 3, return_rgb: bool = False, return_confidence: bool = False, return_hex: bool = False):
    """Return the closest named color for the dominant cluster in a BGR image patch.

    Args:
        image_patch_bgr: crop as a BGR numpy array (as produced by OpenCV).
        k: number of k-means clusters to fit before picking the largest one.
        return_rgb: if True, return (name, (r, g, b)) instead of just name.
        return_confidence: if True, return (name, confidence) or (name, (r,g,b), confidence).

    Returns:
        A color name string, e.g. "red", "navy blue", or "unknown" if the
        patch is empty / too small to analyze.
    """
    if image_patch_bgr is None or image_patch_bgr.size == 0:
        if return_confidence:
            val = ("unknown", (0, 0, 0)) if return_rgb else "unknown"
            return val, 0.0
        return ("unknown", (0, 0, 0)) if return_rgb else "unknown"

    # Downsample for speed — color clustering doesn't need full resolution.
    small = image_patch_bgr
    h, w = small.shape[:2]
    if h * w > 2500:
        scale = (2500 / (h * w)) ** 0.5
        small = cv2.resize(small, (max(1, int(w * scale)), max(1, int(h * scale))))

    # 1. Normalize lighting using CLAHE on the Value/Brightness channel in HSV
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    h_ch, s_ch, v_ch = cv2.split(hsv)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    v_eq = clahe.apply(v_ch)
    hsv_eq = cv2.merge([h_ch, s_ch, v_eq])
    small_eq = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2BGR)

    # 2. Ignore background pixels (crop to middle 70% width, 80% height)
    h_c, w_c = small_eq.shape[:2]
    w_start = int(w_c * 0.15)
    w_end = int(w_c * 0.85)
    h_start = int(h_c * 0.1)
    h_end = int(h_c * 0.9)
    center_patch = small_eq[h_start:h_end, w_start:w_end]

    if center_patch.size == 0:
        center_patch = small_eq

    # --- Convert masked crop region to LAB color space before KMeans ---
    center_patch_lab = cv2.cvtColor(center_patch, cv2.COLOR_BGR2LAB)

    # 3. Ignore shadows, specular highlights, and skin tones
    # Convert center patch to HSV to mask out extremely dark (V < 15) or extremely light (V > 250)
    hsv_center = cv2.cvtColor(center_patch, cv2.COLOR_BGR2HSV)
    s_center = hsv_center[:, :, 1]
    v_center = hsv_center[:, :, 2]
    # Keep pixels with V >= 15. Only reject V > 250 if saturation S >= 35 (to avoid discarding white paint)
    brightness_mask = (v_center >= 15) & ((v_center <= 250) | (s_center < 35))

    # Convert to YCrCb to exclude skin-tones
    ycrcb_center = cv2.cvtColor(center_patch, cv2.COLOR_BGR2YCrCb)
    cr_center = ycrcb_center[:, :, 1]
    cb_center = ycrcb_center[:, :, 2]
    skin_mask = (cr_center >= _SKIN_CR_MIN) & (cr_center <= _SKIN_CR_MAX) & (cb_center >= _SKIN_CB_MIN) & (cb_center <= _SKIN_CB_MAX)

    # Combine masks: valid = brightness_mask AND NOT skin_mask
    valid_mask = brightness_mask & (~skin_mask)

    # Apply mask on LAB pixels
    pixels = center_patch_lab[valid_mask].astype(np.float32)

    fallback_used = False
    # Fallback to all pixels in the patch if the mask filters out everything
    if len(pixels) < k:
        pixels = center_patch_lab.reshape(-1, 3).astype(np.float32)
        valid_mask = np.ones(center_patch.shape[:2], dtype=bool)
        fallback_used = True

    if len(pixels) < k:
        k = max(1, len(pixels))

    # Run KMeans clustering in LAB space
    kmeans = KMeans(n_clusters=k, n_init=3, random_state=0).fit(pixels)
    
    # Choose dominant cluster using spatially contiguous regions logic (cv2.connectedComponents)
    label_map = np.full(center_patch.shape[:2], -1, dtype=np.int32)
    label_map[valid_mask] = kmeans.labels_

    max_contiguous_areas = []
    for c in range(k):
        cluster_mask = (label_map == c).astype(np.uint8)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cluster_mask)
        if num_labels > 1:
            max_area = np.max(stats[1:, cv2.CC_STAT_AREA])
        else:
            max_area = 0
        max_contiguous_areas.append(max_area)

    dominant_cluster_idx = np.argmax(max_contiguous_areas)
    dominant_lab = kmeans.cluster_centers_[dominant_cluster_idx]

    # Convert dominant_lab (in OpenCV uint8 LAB space) back to standard BGR/RGB
    dominant_lab_img = np.array([[dominant_lab]], dtype=np.uint8)
    dominant_bgr_img = cv2.cvtColor(dominant_lab_img, cv2.COLOR_LAB2BGR)
    dominant_bgr = dominant_bgr_img[0, 0]
    dominant_rgb = (int(dominant_bgr[2]), int(dominant_bgr[1]), int(dominant_bgr[0]))

    # Now use CIEDE2000 perceptual distance lookup
    name, ciede_dist = _closest_color_name_with_distance(dominant_rgb)

    # Check original patch brightness and saturation before CLAHE equalization
    hsv_orig = cv2.cvtColor(small[h_start:h_end, w_start:w_end], cv2.COLOR_BGR2HSV)
    if valid_mask.any():
        s_mean = float(np.mean(hsv_orig[valid_mask, 1]))
        v_mean = float(np.mean(hsv_orig[valid_mask, 2]))
    else:
        s_mean = float(np.mean(hsv_orig[:, :, 1]))
        v_mean = float(np.mean(hsv_orig[:, :, 2]))

    # If original patch was bright neutral (white), prevent CLAHE equalization from pulling it to gray
    if s_mean < 35 and v_mean > 175 and name in ("gray", "light gray", "dark gray"):
        name = "white"

    # Calculate sharpness (Laplacian variance) on the input patch
    gray_patch = cv2.cvtColor(image_patch_bgr, cv2.COLOR_BGR2GRAY)
    sharpness = float(cv2.Laplacian(gray_patch, cv2.CV_64F).var())

    # Collapse to base color bucket if crop is blurry
    if sharpness < _SHARPNESS_MIN_FOR_FINEGRAINED:
        name = _BASE_COLLAPSE.get(name, name)

    # Format dominant color to hex
    hex_color = f"#{dominant_rgb[0]:02X}{dominant_rgb[1]:02X}{dominant_rgb[2]:02X}"

    # 4. Compute Confidence Score using CIEDE2000
    proximity_factor = float(np.exp(-ciede_dist / _CIEDE_SIGMA))
    confidence = round(proximity_factor, 2)

    # Ensure confidence stays in [0.0, 1.0]
    confidence = max(0.0, min(1.0, confidence))

    if return_hex:
        if return_confidence:
            return (name, hex_color), confidence
        return name, hex_color

    if return_confidence:
        if return_rgb:
            return (name, dominant_rgb), confidence
        return name, confidence

    return (name, dominant_rgb) if return_rgb else name
