"""Extracts detailed appearance attributes for persons and vehicles.

Uses a combination of region-specific color clustering, edge-density analysis
(Canny edge detection), and geometric aspect ratio heuristics to classify
attributes with confidence-based predictions.
"""

import cv2
import numpy as np
import logging
from src.attributes.color_utils import get_dominant_color

logger = logging.getLogger(__name__)

# COCO Class IDs
PERSON_CLASS_ID = 0
VEHICLE_CLASS_NAMES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


class DeepAttributeExtractor:
    def __init__(self, config: dict = None):
        self.config = config or {}
        # Read parameters from config
        self.k = self.config.get("attributes", {}).get("color_k_clusters", 3)
        self.min_crop_size = self.config.get("attributes", {}).get("min_crop_size", 20)
        self.conf_threshold = self.config.get("confidence", {}).get("attribute_threshold", 0.6)
        
        # Initialize EasyOCR reader if enabled in config
        ocr_cfg = self.config.get("attributes", {}).get("plate_ocr", {})
        self.ocr_enabled = ocr_cfg.get("enabled", True)
        self.ocr_reader = None
        
        if self.ocr_enabled:
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning("Failed to initialize EasyOCR: %s", e)

    def _wrap_value(self, val, conf):
        """Helper to enforce confidence thresholds, mapping low confidence to 'unknown'."""
        if conf < self.conf_threshold:
            return {"value": "unknown", "confidence": float(conf)}
        return {"value": val, "confidence": float(conf)}

    def extract(self, crop_bgr: np.ndarray, class_id: int, detection_confidence: float = 1.0) -> dict:
        """Extract rich attributes for either a person or vehicle crop, with confidence scores."""
        h, w = crop_bgr.shape[:2] if crop_bgr is not None else (0, 0)
        if crop_bgr is None or h < self.min_crop_size or w < self.min_crop_size:
            return {}

        if class_id == PERSON_CLASS_ID:
            return self._extract_person_attributes(crop_bgr)
        elif class_id in VEHICLE_CLASS_NAMES:
            return self._extract_vehicle_attributes(crop_bgr, class_id, detection_confidence)
        return {}

    def _extract_person_attributes(self, crop_bgr: np.ndarray) -> dict:
        h, w = crop_bgr.shape[:2]

        # Slicing regions (center 50% width to avoid background)
        w_start = int(w * 0.25)
        w_end = int(w * 0.75)
        head_region = crop_bgr[0:int(h * 0.15), w_start:w_end]
        shirt_region = crop_bgr[int(h * 0.18):int(h * 0.55), w_start:w_end]
        pant_region = crop_bgr[int(h * 0.55):int(h * 0.90), w_start:w_end]
        shoe_region = crop_bgr[int(h * 0.90):h, int(w * 0.3):int(w * 0.7)]

        # 1. Color Extraction with Confidence and Hex
        ((shirt_color, shirt_hex), shirt_conf) = get_dominant_color(shirt_region, self.k, return_confidence=True, return_hex=True)
        ((pant_color, pant_hex), pant_conf) = get_dominant_color(pant_region, self.k, return_confidence=True, return_hex=True)
        shoe_color, shoe_conf = get_dominant_color(shoe_region, self.k, return_confidence=True)

        # 2. Cap Detection Heuristic with Soft Sigmoid Confidence
        cap_val, cap_conf = self._has_cap_with_confidence(head_region)

        # 3. Helmet Detection Heuristic with Soft Sigmoid Confidence
        helmet_val, helmet_conf = self._has_helmet_with_confidence(head_region)

        # Cap & Helmet mutual exclusion rule
        if helmet_val and helmet_conf > cap_conf:
            cap_val = False

        # 4. Bag / Backpack detection with Soft Sigmoid Confidence
        bag_val, bag_conf = self._has_bag_with_confidence(shirt_region)

        # 5. Clothing type heuristic with Soft Sigmoid Confidence
        aspect_ratio = h / w
        clothing_val, clothing_conf = self._clothing_type_with_confidence(aspect_ratio)

        # 6. Garment type classification
        shirt_type, shirt_type_conf = self._classify_upper_garment(shirt_region)
        pant_type, pant_type_conf = self._classify_lower_garment(pant_region)

        return {
            # Legacy fields (for safety/compatibility)
            "shirt": self._wrap_value(shirt_color, shirt_conf),
            "pants": self._wrap_value(pant_color, pant_conf),
            "shoe_color": self._wrap_value(shoe_color, shoe_conf),
            "cap": self._wrap_value(cap_val, cap_conf),
            "helmet": self._wrap_value(helmet_val, helmet_conf),
            "bag": self._wrap_value(bag_val, bag_conf),
            "clothing_type": self._wrap_value(clothing_val, clothing_conf),
            
            # New fields
            "upper_garment_type": self._wrap_value(shirt_type, shirt_type_conf),
            "upper_color_name": self._wrap_value(shirt_color, shirt_conf),
            "upper_color_hex": self._wrap_value(shirt_hex, shirt_conf),
            "lower_garment_type": self._wrap_value(pant_type, pant_type_conf),
            "lower_color_name": self._wrap_value(pant_color, pant_conf),
            "lower_color_hex": self._wrap_value(pant_hex, pant_conf)
        }

    def _extract_vehicle_attributes(self, crop_bgr: np.ndarray, class_id: int, detection_confidence: float) -> dict:
        h, w = crop_bgr.shape[:2]
        
        # 1. Dominant vehicle color
        ((color, color_hex), color_conf) = get_dominant_color(crop_bgr, self.k, return_confidence=True, return_hex=True)
        vtype = VEHICLE_CLASS_NAMES.get(class_id, "car")
        vtype_conf = detection_confidence

        # Refine vehicle type based on aspect ratio
        aspect_ratio = w / h if h > 0 else 1.0
        if class_id == 2:  # Car
            if aspect_ratio < 0.9:
                vtype = "auto rickshaw"
                vtype_conf = 0.75
            elif aspect_ratio < 1.1:
                vtype = "van"
                vtype_conf = 0.70
            else:
                vtype = "car"
        elif class_id == 3:  # Motorcycle
            vtype = "bike/scooter"
            if aspect_ratio > 1.2:
                vtype = "e-rickshaw"
                vtype_conf = 0.65
        elif class_id == 7:  # Truck
            if aspect_ratio > 2.0:
                vtype = "truck"
            else:
                vtype = "van"

        # 2. Body type based on aspect ratio
        if class_id == 2:  # Car
            body_val, body_conf = self._body_type_with_confidence(aspect_ratio)
        elif class_id == 3:
            body_val, body_conf = "motorcycle", 1.0
        elif class_id == 5:
            body_val, body_conf = "bus", 1.0
        else:
            body_val, body_conf = "truck", 1.0

        # 3. Roof rack check: edge density in top 18% of vehicle crop
        roof_region = crop_bgr[0:int(h * 0.18), :]
        roof_val, roof_conf = self._has_roof_rack_with_confidence(roof_region)

        # 4. Plate OCR
        plate_partial = None
        plate_confidence = 0.0
        
        if self.ocr_enabled and self.ocr_reader is not None:
            try:
                # Crop lower middle region of vehicle
                plate_region = crop_bgr[int(h * 0.55):int(h * 0.95), int(w * 0.1):int(w * 0.9)]
                if plate_region.size > 0:
                    ocr_results = self.ocr_reader.readtext(plate_region)
                    legible_texts = []
                    conf_scores = []
                    for bbox, text, conf in ocr_results:
                        cleaned_text = "".join([c for c in text if c.isalnum() or c in "*- "])
                        if cleaned_text.strip():
                            legible_texts.append(cleaned_text.strip())
                            conf_scores.append(conf)
                    
                    if legible_texts:
                        plate_partial = " ".join(legible_texts)
                        plate_confidence = float(np.mean(conf_scores))
            except Exception as e:
                logger.warning("OCR processing error: %s", e)

        return {
            # Legacy fields (for safety/compatibility)
            "vehicle_type": self._wrap_value(vtype, vtype_conf),
            "color": self._wrap_value(color, color_conf),
            "make": self._wrap_value("unknown", 1.0),
            "body_type": self._wrap_value(body_val, body_conf),
            "roof_rack": self._wrap_value(roof_val, roof_conf),
            
            # New fields
            "vehicle_color_name": self._wrap_value(color, color_conf),
            "vehicle_color_hex": self._wrap_value(color_hex, color_conf),
            "plate_partial": {"value": plate_partial, "confidence": plate_confidence} if plate_partial else {"value": None, "confidence": 0.0},
            "plate_confidence": {"value": plate_confidence, "confidence": 1.0}
        }

    def _has_cap_with_confidence(self, head_region: np.ndarray) -> tuple:
        if head_region.size == 0:
            return False, 0.0
        try:
            hsv = cv2.cvtColor(head_region, cv2.COLOR_BGR2HSV)
            top_strip = hsv[0:max(1, hsv.shape[0] // 2), :]
            mean_saturation = float(np.mean(top_strip[:, :, 1]))
            std_hue = float(np.std(top_strip[:, :, 0]))

            # Sigmoid mappings around thresholds (mean_saturation = 80, std_hue = 25)
            # Higher saturation increases cap probability, higher std_hue decreases it
            sat_factor = 1.0 / (1.0 + np.exp(-(mean_saturation - 80.0) / 10.0))
            hue_factor = 1.0 / (1.0 + np.exp(-(25.0 - std_hue) / 5.0))
            prob = float(sat_factor * hue_factor)
            
            is_cap = prob > 0.5
            conf = prob if is_cap else (1.0 - prob)
            return is_cap, round(conf, 2)
        except Exception as e:
            logger.error("Error in cap confidence detection: %s", e)
            return False, 0.0

    def _has_helmet_with_confidence(self, head_region: np.ndarray) -> tuple:
        if head_region.size == 0:
            return False, 0.0
        try:
            h, w = head_region.shape[:2]
            gray = cv2.cvtColor(head_region, cv2.COLOR_BGR2GRAY)
            std_gray = float(np.std(gray))
            
            edges = cv2.Canny(gray, 50, 150)
            edge_density = float(np.sum(edges > 0)) / (h * w) if (h * w) > 0 else 0.0

            # Heuristic standard: std_gray < 35 and 0.05 < edge_density < 0.25
            unif_factor = 1.0 / (1.0 + np.exp(-(35.0 - std_gray) / 5.0))
            # Bell curve for edge density centered at 0.15
            edge_factor = float(np.exp(-((edge_density - 0.15) / 0.10)**2))
            
            prob = float(unif_factor * edge_factor)
            is_helmet = prob > 0.5
            conf = prob if is_helmet else (1.0 - prob)
            return is_helmet, round(conf, 2)
        except Exception as e:
            logger.error("Error in helmet confidence detection: %s", e)
            return False, 0.0

    def _has_bag_with_confidence(self, torso_region: np.ndarray) -> tuple:
        if torso_region.size == 0:
            return False, 0.0
        try:
            h, w = torso_region.shape[:2]
            gray = cv2.cvtColor(torso_region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            left_strip = edges[:, 0:int(w * 0.25)]
            right_strip = edges[:, int(w * 0.75):w]
            
            lateral_edge_density = float(np.sum(left_strip > 0) + np.sum(right_strip > 0)) / (h * w) if (h * w) > 0 else 0.0

            # Heuristic standard: lateral_edge_density > 0.08
            prob = float(1.0 / (1.0 + np.exp(-(lateral_edge_density - 0.08) / 0.02)))
            is_bag = prob > 0.5
            conf = prob if is_bag else (1.0 - prob)
            return is_bag, round(conf, 2)
        except Exception as e:
            logger.error("Error in bag confidence detection: %s", e)
            return False, 0.0

    def _clothing_type_with_confidence(self, aspect_ratio: float) -> tuple:
        # Heuristic: aspect_ratio > 2.5 full_body, else short_sleeves
        prob = float(1.0 / (1.0 + np.exp(-(aspect_ratio - 2.5) / 0.3)))
        is_full = prob > 0.5
        val = "full_body" if is_full else "short_sleeves"
        conf = prob if is_full else (1.0 - prob)
        return val, round(conf, 2)

    def _body_type_with_confidence(self, aspect_ratio: float) -> tuple:
        # Heuristic: sedan if aspect_ratio > 1.8 else suv
        prob = float(1.0 / (1.0 + np.exp(-(aspect_ratio - 1.8) / 0.2)))
        is_sedan = prob > 0.5
        val = "sedan" if is_sedan else "suv"
        conf = prob if is_sedan else (1.0 - prob)
        return val, round(conf, 2)

    def _has_roof_rack_with_confidence(self, roof_region: np.ndarray) -> tuple:
        if roof_region.size == 0:
            return False, 0.0
        try:
            h, w = roof_region.shape[:2]
            gray = cv2.cvtColor(roof_region, cv2.COLOR_BGR2GRAY)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            horizontal_edges = np.abs(sobely) > 40
            density = float(np.sum(horizontal_edges)) / (h * w) if (h * w) > 0 else 0.0

            # Heuristic standard: density > 0.12
            prob = float(1.0 / (1.0 + np.exp(-(density - 0.12) / 0.03)))
            is_rack = prob > 0.5
            conf = prob if is_rack else (1.0 - prob)
            return is_rack, round(conf, 2)
        except Exception as e:
            logger.error("Error in roof rack confidence detection: %s", e)
            return False, 0.0

    def _classify_upper_garment(self, region: np.ndarray) -> tuple:
        if region is None or region.size == 0:
            return "unknown", 0.0
        h, w = region.shape[:2]
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        std_gray = float(np.std(gray))
        edges = cv2.Canny(region, 50, 150)
        edge_density = float(np.sum(edges > 0)) / (h * w) if (h * w) > 0 else 0.0
        
        # Aspect ratio of the crop
        aspect = h / w if w > 0 else 1.0
        
        # Heuristic rules to assign upper garment types
        if edge_density > 0.15:
            val = "jacket"
            prob = min(0.95, 0.5 + edge_density)
        elif edge_density > 0.10:
            val = "hoodie" if aspect > 1.2 else "shirt"
            prob = 0.7
        elif std_gray > 40:
            val = "kurta" if aspect > 1.4 else "suit"
            prob = 0.65
        else:
            val = "t-shirt" if aspect < 1.0 else "top"
            prob = 0.8
        
        return val, round(prob, 2)

    def _classify_lower_garment(self, region: np.ndarray) -> tuple:
        if region is None or region.size == 0:
            return "unknown", 0.0
        h, w = region.shape[:2]
        
        # Check skin tone ratio in lower region
        ycrcb = cv2.cvtColor(region, cv2.COLOR_BGR2YCrCb)
        cr = ycrcb[:, :, 1]
        cb = ycrcb[:, :, 2]
        
        skin_cr_min = self.config.get("attributes", {}).get("skin_cr_min", 133)
        skin_cr_max = self.config.get("attributes", {}).get("skin_cr_max", 173)
        skin_cb_min = self.config.get("attributes", {}).get("skin_cb_min", 77)
        skin_cb_max = self.config.get("attributes", {}).get("skin_cb_max", 127)
        
        skin_mask = (cr >= skin_cr_min) & (cr <= skin_cr_max) & (cb >= skin_cb_min) & (cb <= skin_cb_max)
        skin_ratio = float(np.sum(skin_mask)) / region.size if region.size > 0 else 0.0
        
        # Check blue/saturation for jeans
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        h_ch = hsv[:, :, 0]
        s_ch = hsv[:, :, 1]
        # Blue hue is around 90-130 in OpenCV
        blue_pixels = (h_ch >= 90) & (h_ch <= 130) & (s_ch >= 40)
        blue_ratio = float(np.sum(blue_pixels)) / region.size if region.size > 0 else 0.0
        
        aspect = h / w if w > 0 else 1.0
        
        if skin_ratio > 0.15:
            val = "shorts" if aspect > 1.2 else "skirt"
            prob = 0.5 + skin_ratio
        elif blue_ratio > 0.15:
            val = "jeans"
            prob = 0.6 + blue_ratio
        elif aspect > 1.8:
            val = "saree"
            prob = 0.75
        elif aspect > 1.4:
            val = "trousers"
            prob = 0.7
        else:
            val = "track pants"
            prob = 0.65
            
        return val, round(min(0.99, prob), 2)
