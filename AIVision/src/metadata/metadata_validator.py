"""Metadata validation layer to check tracking, bbox size, quality, occlusion, and confidence thresholds.

Rejects unstable tracks and cleans up metadata field values with 'unknown' if they fail validation rules.
"""

import logging
from src.video.keyframe_selector import is_quality_acceptable

logger = logging.getLogger(__name__)


class MetadataValidator:
    def __init__(self, config: dict):
        self.config = config
        
        # Load thresholds
        track_cfg = self.config.get("tracking", {})
        self.min_observations = track_cfg.get("min_observations", 10)
        self.min_duration = track_cfg.get("min_track_duration_sec", 0.5)

        attr_cfg = self.config.get("attributes", {})
        self.min_crop_size = attr_cfg.get("min_crop_size", 20)

        conf_cfg = self.config.get("confidence", {})
        self.attr_conf_threshold = conf_cfg.get("attribute_threshold", 0.60)
        self.det_conf_threshold = conf_cfg.get("detection_threshold", 0.40)

    def is_track_stable(self, num_observations: int, duration_sec: float) -> bool:
        """Check if a track is stable enough to be recorded."""
        if num_observations < self.min_observations:
            return False
        if duration_sec < self.min_duration:
            return False
        return True

    def validate_record(self, record: dict, keyframe_metrics: dict = None) -> tuple:
        """Validate and clean a track's finalized metadata record.

        Args:
            record: the dict containing the track's finalized metadata.
            keyframe_metrics: dictionary containing quality metrics of the keyframe crop.

        Returns:
            (is_valid, validated_record)
            where is_valid is False if the track should be ignored/dropped entirely.
        """
        track_id = record["track_id"]
        class_name = record["class"]

        # 1. Reject unstable tracks
        if not self.is_track_stable(record["num_observations"], record["duration"]):
            logger.info("Validation: Rejecting unstable track %s (Obs: %d, Dur: %.1fs)",
                        track_id, record["num_observations"], record["duration"])
            return False, record

        # 2. Check Bbox Size / Crop size
        # If the last bounding box is too small, or if we have no crops
        bbox = record.get("last_bbox", [0, 0, 0, 0])
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        is_too_small = (w < self.min_crop_size) or (h < self.min_crop_size)

        # 3. Check Image Quality
        quality_fails = False
        if keyframe_metrics:
            is_acceptable = is_quality_acceptable(keyframe_metrics, self.config)
            if not is_acceptable:
                quality_fails = True
                logger.info("Validation: Keyframe quality fails for track %s. Brightness: %.1f, Sharpness: %.1f",
                            track_id, keyframe_metrics.get("brightness", 0.0), keyframe_metrics.get("sharpness", 0.0))

        # 4. Check Occlusion
        # We can calculate occlusion ratio using first/last frames seen vs actual frames observed
        first_frame = record.get("first_seen_frame", 0)
        last_frame = record.get("last_seen_frame", 0)
        span = last_frame - first_frame + 1
        occlusion_ratio = 0.0
        if span > 10:
            observed_ratio = record["num_observations"] / span
            occlusion_ratio = 1.0 - observed_ratio
        
        high_occlusion = occlusion_ratio > 0.60  # More than 60% of frames were occluded/lost

        # If bounding box is too small, keyframe quality fails, or high occlusion is detected,
        # we invalidate all appearance attributes by setting them to "unknown".
        appearance = record.get("appearance", {})
        confidence = record.get("confidence", {})

        if is_too_small or quality_fails or high_occlusion:
            reason = "too small bbox" if is_too_small else ("poor quality keyframe" if quality_fails else "high occlusion")
            logger.info("Validation: Invalidate appearance attributes for track %s due to %s", track_id, reason)
            for k in appearance.keys():
                # Helmet and cap are booleans. Set them to 'unknown'
                appearance[k] = "unknown"
                confidence[k] = 0.0
            
            # Invalidate new structures
            if record.get("upper_body"):
                record["upper_body"]["garment_type"] = "unknown"
                record["upper_body"]["color_name"] = "unknown"
                record["upper_body"]["color_hex"] = "unknown"
                record["upper_body"]["color_confidence"] = 0.0
            if record.get("lower_body"):
                record["lower_body"]["garment_type"] = "unknown"
                record["lower_body"]["color_name"] = "unknown"
                record["lower_body"]["color_hex"] = "unknown"
                record["lower_body"]["color_confidence"] = 0.0
            if record.get("vehicle"):
                record["vehicle"]["vehicle_type"] = "unknown"
                record["vehicle"]["color_name"] = "unknown"
                record["vehicle"]["color_hex"] = "unknown"
                record["vehicle"]["plate_partial"] = None
                record["vehicle"]["plate_confidence"] = 0.0
        else:
            # Enforce minimum attribute thresholds
            if class_name == "person":
                upper_body = record.get("upper_body")
                lower_body = record.get("lower_body")
                if upper_body:
                    if confidence.get("upper_garment_type", 0.0) < self.attr_conf_threshold:
                        upper_body["garment_type"] = "unknown"
                    if confidence.get("upper_color_name", 0.0) < self.attr_conf_threshold:
                        upper_body["color_name"] = "unknown"
                        upper_body["color_hex"] = "unknown"
                if lower_body:
                    if confidence.get("lower_garment_type", 0.0) < self.attr_conf_threshold:
                        lower_body["garment_type"] = "unknown"
                    if confidence.get("lower_color_name", 0.0) < self.attr_conf_threshold:
                        lower_body["color_name"] = "unknown"
                        lower_body["color_hex"] = "unknown"
            else:
                vehicle = record.get("vehicle")
                if vehicle:
                    if confidence.get("vehicle_type", 0.0) < self.attr_conf_threshold:
                        vehicle["vehicle_type"] = "unknown"
                    if confidence.get("vehicle_color_name", 0.0) < self.attr_conf_threshold:
                        vehicle["color_name"] = "unknown"
                        vehicle["color_hex"] = "unknown"
                    
                    # Validate plate OCR confidence with custom threshold
                    plate_val = vehicle.get("plate_partial")
                    plate_conf = vehicle.get("plate_confidence", 0.0)
                    ocr_cfg = self.config.get("attributes", {}).get("plate_ocr", {})
                    min_plate_conf = ocr_cfg.get("min_confidence", 0.4)
                    
                    if plate_val and plate_val != "unknown" and plate_val is not None:
                        if plate_conf < min_plate_conf:
                            vehicle["plate_partial"] = None
                            vehicle["plate_confidence"] = 0.0

        # 5. Clean duplicate events
        events = record.get("events", [])
        clean_events = []
        for e in events:
            if e not in clean_events:
                clean_events.append(e)
        record["events"] = clean_events

        return True, record
