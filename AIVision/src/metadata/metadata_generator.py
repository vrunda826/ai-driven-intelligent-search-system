"""Aggregates per-frame detections into track-level metadata records.

Implements multi-frame attribute fusion, temporal smoothing, validation integration,
and a rich metadata schema.
"""

import csv
import json
import os
import numpy as np
import logging
from collections import Counter, defaultdict
from src.metadata.metadata_validator import MetadataValidator

logger = logging.getLogger(__name__)


class MetadataGenerator:
    def __init__(self, camera_id: str, config: dict = None):
        self.camera_id = camera_id
        self.config = config or {}
        # track_key -> accumulated record
        self._tracks = {}
        # track_key -> Counter of attribute value per attribute name (majority vote fallback)
        self._attribute_votes = defaultdict(lambda: defaultdict(Counter))
        
        self.validator = MetadataValidator(self.config) if self.config else None

    def update(self, track_key: str, frame_idx: int, timestamp: str,
               class_id: int, class_name: str, bbox_xyxy, confidence: float,
               attributes: dict, crop_path: str = None) -> None:
        """Register one frame's observation of a tracked object."""
        if track_key not in self._tracks:
            self._tracks[track_key] = {
                "track_id": track_key,
                "camera_id": self.camera_id,
                "class_id": int(class_id),
                "class_name": class_name,
                "first_seen_frame": frame_idx,
                "first_seen_time": timestamp,
                "last_seen_frame": frame_idx,
                "last_seen_time": timestamp,
                "num_observations": 0,
                "max_confidence": 0.0,
                "last_bbox": None,
                "crop_paths": [],
            }

        record = self._tracks[track_key]
        record["last_seen_frame"] = frame_idx
        record["last_seen_time"] = timestamp
        record["num_observations"] += 1
        record["max_confidence"] = max(record["max_confidence"], float(confidence))
        record["last_bbox"] = [float(v) for v in bbox_xyxy]

        if crop_path:
            record["crop_paths"].append(crop_path)

        for attr_name, attr_value in attributes.items():
            if attr_name in ("object_type",):
                continue
            self._attribute_votes[track_key][attr_name][attr_value] += 1

    def _fuse_attributes(self, keyframe_attrs: dict, kf_quality: dict = None) -> tuple:
        """Fuse attributes from multiple keyframes using confidence-weighted voting.

        keyframe_attrs: dict of keyframe_name -> attribute_dict
                        where attribute_dict is attr_name -> {"value": val, "confidence": conf}
        kf_quality: dict of keyframe_name -> keyframe_info dict containing sharpness score

        Returns:
            fused_values (dict): attr_name -> val
            fused_confidences (dict): attr_name -> conf
        """
        fused_values = {}
        fused_confidences = {}

        # Define quality weights for different keyframe types
        kf_weights = {
            "highest_quality": 3.0,
            "largest_bbox": 2.0,
            "first": 1.0,
            "middle": 1.0,
            "last": 1.0
        }

        # Calculate max sharpness score in this track across all keyframes in kf_quality
        max_sharpness = 1.0
        if kf_quality:
            sharpness_scores = [
                info.get("metrics", {}).get("sharpness", 1.0)
                for info in kf_quality.values()
                if isinstance(info, dict)
            ]
            if sharpness_scores:
                max_sharpness = max(sharpness_scores)
        if max_sharpness <= 0:
            max_sharpness = 1.0

        # Collect all attribute names
        all_attr_names = set()
        for kf_name, attrs in keyframe_attrs.items():
            if attrs:
                all_attr_names.update(attrs.keys())

        for attr in all_attr_names:
            # Group by value and calculate weighted sums
            val_conf_sums = defaultdict(float)
            val_confs = defaultdict(list)
            has_preds = False

            for kf_name, attrs in keyframe_attrs.items():
                if attrs and attr in attrs:
                    pred = attrs[attr]
                    # Format check: ensure pred is a dict with value and confidence
                    if isinstance(pred, dict) and "value" in pred and "confidence" in pred:
                        base_type_weight = kf_weights.get(kf_name, 1.0)
                        val = pred["value"]
                        conf = pred["confidence"]
                        
                        # Calculate sharpness-based modifier
                        sharpness_score = 1.0
                        if kf_quality and kf_name in kf_quality:
                            sharpness_score = kf_quality[kf_name].get("metrics", {}).get("sharpness", 1.0)
                        
                        # Apply formula: weight = base_type_weight * (sharpness_score / max_sharpness) * conf
                        weight = base_type_weight * (sharpness_score / max_sharpness) * conf
                        
                        val_conf_sums[val] += conf * weight
                        val_confs[val].append(conf)
                        has_preds = True

            if not has_preds:
                fused_values[attr] = "unknown"
                fused_confidences[attr] = 0.0
                continue

            # Select value with highest confidence sum (majority voting + confidence weighting)
            best_val = max(val_conf_sums, key=val_conf_sums.get)
            best_conf = float(np.mean(val_confs[best_val]))

            fused_values[attr] = best_val
            fused_confidences[attr] = round(best_conf, 2)

        return fused_values, fused_confidences

    def finalize(self, trajectory_tracker=None, motion_analyzer=None,
                 zone_analyzer=None, event_detector=None,
                 relationship_analyzer=None, embeddings_dict=None,
                 deep_attributes_dict=None, keyframe_quality_dict=None, fps: float = 30.0) -> list:
        """Resolve all analytics metadata per track and build the final

        exportable list of rich track metadata dicts.
        """
        results = []
        
        # Pre-calculate relationship metadata
        relations = {}
        if relationship_analyzer:
            relations = relationship_analyzer.finalize()

        for track_key, record in list(self._tracks.items()):
            class_name = record["class_name"]
            
            # 1. Identity & Duration
            total_frames = record["last_seen_frame"] - record["first_seen_frame"]
            duration_sec = total_frames / fps if fps > 0 else 0.0
            duration_sec = round(max(0.1, duration_sec), 1)

            # 2. Appearance Attributes Fusion & Confidence
            appearance = {}
            confidence_record = {}

            # Perform multi-frame attribute fusion if multi-keyframe dict is provided
            if deep_attributes_dict and track_key in deep_attributes_dict:
                keyframe_attrs = deep_attributes_dict[track_key]
                # keyframe_attrs is a dict of keyframe_name -> attributes
                kf_quality = keyframe_quality_dict.get(track_key) if keyframe_quality_dict else None
                appearance, confidence_record = self._fuse_attributes(keyframe_attrs, kf_quality)
                logger.info("Track %s appearance fusion complete: %s", track_key, appearance)
            else:
                # Fallback to single frame/majority vote if no keyframe dict provided
                # Convert Counters to flat attributes and confidence placeholders
                for attr_name, votes in self._attribute_votes[track_key].items():
                    val, count = votes.most_common(1)[0]
                    appearance[attr_name] = val
                    confidence_record[attr_name] = round(count / sum(votes.values()), 2)

            # Normalize keys to match schemas
            upper_body_obj = {}
            lower_body_obj = {}
            vehicle_obj = {}

            if class_name == "person":
                appearance_normalized = {
                    "shirt": appearance.get("shirt_color", appearance.get("shirt", appearance.get("upper_color_name", "unknown"))),
                    "pants": appearance.get("pant_color", appearance.get("pants", appearance.get("lower_color_name", "unknown"))),
                    "bag": appearance.get("bag", "unknown"),
                    "cap": appearance.get("cap", "unknown"),
                    "helmet": appearance.get("helmet", "unknown"),
                    "shoe_color": appearance.get("shoe_color", "unknown"),
                    "clothing_type": appearance.get("clothing_type", "unknown")
                }
                
                # Construct new fine-grained upper/lower body structures
                upper_body_obj = {
                    "garment_type": appearance.get("upper_garment_type", "unknown"),
                    "color_name": appearance.get("upper_color_name", "unknown"),
                    "color_hex": appearance.get("upper_color_hex", "unknown"),
                    "color_confidence": confidence_record.get("upper_color_name", 0.0)
                }
                lower_body_obj = {
                    "garment_type": appearance.get("lower_garment_type", "unknown"),
                    "color_name": appearance.get("lower_color_name", "unknown"),
                    "color_hex": appearance.get("lower_color_hex", "unknown"),
                    "color_confidence": confidence_record.get("lower_color_name", 0.0)
                }
                
                # Expose specific confidence scores
                confidence_record["upper_garment_type"] = confidence_record.get("upper_garment_type", 0.0)
                confidence_record["lower_garment_type"] = confidence_record.get("lower_garment_type", 0.0)
                confidence_record["upper_color_name"] = confidence_record.get("upper_color_name", 0.0)
                confidence_record["lower_color_name"] = confidence_record.get("lower_color_name", 0.0)
            else:
                appearance_normalized = {
                    "vehicle_type": appearance.get("vehicle_type", class_name),
                    "color": appearance.get("color", appearance.get("vehicle_color_name", "unknown")),
                    "make": appearance.get("make", "unknown"),
                    "body_type": appearance.get("body_type", "unknown"),
                    "roof_rack": appearance.get("roof_rack", "unknown")
                }
                
                # Extract best effort plate values
                plate_val = appearance.get("plate_partial")
                plate_conf = appearance.get("plate_confidence", 0.0)
                
                # Construct vehicle structure
                vehicle_obj = {
                    "vehicle_type": appearance.get("vehicle_type", class_name),
                    "color_name": appearance.get("vehicle_color_name", "unknown"),
                    "color_hex": appearance.get("vehicle_color_hex", "unknown"),
                    "plate_partial": plate_val if (plate_val != "unknown" and plate_val is not None) else None,
                    "plate_confidence": float(plate_conf) if (plate_val != "unknown" and plate_val is not None) else 0.0
                }
                
                confidence_record["vehicle_color_name"] = confidence_record.get("vehicle_color_name", 0.0)
                confidence_record["vehicle_type"] = confidence_record.get("vehicle_type", 1.0)
                confidence_record["plate_partial"] = float(plate_conf) if (plate_val != "unknown" and plate_val is not None) else 0.0

            appearance = appearance_normalized

            # Map individual attribute confidences
            for k in appearance.keys():
                if k not in confidence_record:
                    confidence_record[k] = 1.0

            # 3. Motion Metadata
            motion = {
                "speed": "unknown",
                "direction": "unknown",
                "distance": 0.0,
                "average_speed": 0.0,
                "status": "unknown",
                "acceleration": 0.0,
                "stationary_duration": 0.0,
                "movement_confidence": 0.0,
                "smoothed_direction": "unknown"
            }
            if motion_analyzer and trajectory_tracker:
                history = trajectory_tracker.get_history(track_key)
                motion = motion_analyzer.analyze(history)

            # Add motion confidence to confidence record
            confidence_record["motion"] = motion.get("movement_confidence", 0.0)

            # 4. Spatial & Zone Metadata
            location = {"zone": "outside"}
            spatial_meta = {
                "current_zone": "outside",
                "entered_zone": None,
                "exited_zone": None,
                "previous_zone": None,
                "entry_timestamp": None,
                "exit_timestamp": None,
                "total_dwell_time": 0.0,
                "zone_history": []
            }
            if zone_analyzer and trajectory_tracker:
                history = trajectory_tracker.get_history(track_key)
                spatial_meta = zone_analyzer.analyze_trajectory(history)
                location = {"zone": spatial_meta["current_zone"]}

            # 5. Relationship Metadata
            relationships = relations.get(track_key, {
                "near_vehicle": None,
                "near_vehicle_duration": 0.0,
                "group_size": 1,
                "interaction_duration": 0.0,
                "nearest_object": None,
                "nearest_vehicle": None,
                "group_confidence": 0.0
            })
            confidence_record["relationships"] = relationships.get("group_confidence", 0.0)

            # 6. Events Metadata
            events = ["entered"]
            if event_detector:
                events = event_detector.detect(class_name, duration_sec, motion, spatial_meta, relationships)

            # 7. Embeddings Metadata
            embeddings = {"clip": None, "reid": None}
            if embeddings_dict and track_key in embeddings_dict:
                embeddings = embeddings_dict[track_key]

            # 8. Keyframe quality scoring
            keyframe_quality_record = {}
            if keyframe_quality_dict and track_key in keyframe_quality_dict:
                # Store structural metrics for all 5 keyframes
                for kf_name, info in keyframe_quality_dict[track_key].items():
                    keyframe_quality_record[kf_name] = {
                        "frame_idx": info["frame_idx"],
                        "quality_score": info["quality_score"],
                        "metrics": info["metrics"]
                    }

            # Assemble preliminary track metadata dict
            final_record = {
                # Legacy fields
                "track_id": track_key,
                "camera_id": record["camera_id"],
                "class": class_name,
                "first_seen": record["first_seen_time"],
                "last_seen": record["last_seen_time"],
                "duration": duration_sec,
                "num_observations": record["num_observations"],
                "max_confidence": record["max_confidence"],
                
                # New fields for fine-grained attributes and vehicles
                "upper_body": upper_body_obj if class_name == "person" else None,
                "lower_body": lower_body_obj if class_name == "person" else None,
                "vehicle": vehicle_obj if class_name != "person" else None,
                
                "appearance": appearance,
                "motion": motion,
                "location": location,
                "events": events,
                "relationships": relationships,
                "embeddings": embeddings,
                "description": "",  # compose after validation
                "crop_paths": record["crop_paths"],
                
                # Internal helper fields needed for validator
                "first_seen_frame": record["first_seen_frame"],
                "last_seen_frame": record["last_seen_frame"],
                "last_bbox": record["last_bbox"],
                
                # New fields for schema upgrades
                "spatial": spatial_meta,
                "quality": keyframe_quality_record,
                "confidence": confidence_record
            }

            # 9. Validation Layer Check
            if self.validator:
                best_metrics = None
                if keyframe_quality_dict and track_key in keyframe_quality_dict:
                    # Retrieve highest quality frame's metrics for assessment
                    best_metrics = keyframe_quality_dict[track_key].get("highest_quality", {}).get("metrics")
                
                is_valid, validated_record = self.validator.validate_record(final_record, best_metrics)
                if not is_valid:
                    # Ignore track completely (unstable/rejected)
                    continue
                final_record = validated_record

            # 10. Description Generation (using strictly validated attributes)
            final_record["description"] = self._build_rich_description(
                class_name, final_record, final_record["motion"],
                final_record["location"], final_record["spatial"],
                final_record["events"], final_record["relationships"], duration_sec
            )

            # Cleanup internal helpers before returning
            final_record.pop("first_seen_frame", None)
            final_record.pop("last_seen_frame", None)
            final_record.pop("last_bbox", None)

            results.append(final_record)

        return results

    @staticmethod
    def _build_rich_description(class_name: str, record: dict, motion: dict,
                                location: dict, spatial_meta: dict, events: list,
                                relationships: dict, duration: float) -> str:
        """Compose a plain-English rich narrative from validated structured metadata."""
        entered_z = spatial_meta.get("entered_zone")
        curr_z = location.get("zone", "outside")
        direction = motion.get("direction", "unknown")
        speed = motion.get("speed", "slow")

        # Support both record being appearance dict or full record dict
        appearance = record.get("appearance", {}) if "appearance" in record else record
        upper_body = record.get("upper_body", {}) if isinstance(record, dict) and record.get("upper_body") else {}
        lower_body = record.get("lower_body", {}) if isinstance(record, dict) and record.get("lower_body") else {}
        vehicle = record.get("vehicle", {}) if isinstance(record, dict) and record.get("vehicle") else {}

        if class_name == "person":
            shirt = upper_body.get("color_name", appearance.get("shirt", "unknown"))
            pants = lower_body.get("color_name", appearance.get("pants", "unknown"))
            garment_upper = upper_body.get("garment_type", "unknown")
            garment_lower = lower_body.get("garment_type", "unknown")
            
            bag = appearance.get("bag", "unknown")
            cap = appearance.get("cap", "unknown")
            helmet = appearance.get("helmet", "unknown")
            
            desc = "A person"
            attrs = []
            if shirt != "unknown":
                if garment_upper != "unknown":
                    attrs.append(f"a {shirt} {garment_upper}")
                else:
                    attrs.append(f"a {shirt} shirt")
            if pants != "unknown":
                if garment_lower != "unknown":
                    attrs.append(f"{pants} {garment_lower}")
                else:
                    attrs.append(f"{pants} pants")
            
            if attrs:
                desc += " wearing " + " and ".join(attrs)
            
            acc = []
            # Check for strict boolean values (avoid matching string 'unknown')
            if bag is True or str(bag).lower() == "true":
                acc.append("carrying a bag")
            if cap is True or str(cap).lower() == "true":
                acc.append("wearing a cap")
            if helmet is True or str(helmet).lower() == "true":
                acc.append("wearing a helmet")
            
            if acc:
                desc += " and " + ", ".join(acc) if len(attrs) > 0 else " " + ", ".join(acc)
            
            desc += f" entered from {entered_z}" if (entered_z and entered_z != "outside") else " appeared in the area"
            
            if direction not in ("stationary", "unknown"):
                desc += f", walking {speed} towards the {direction}"
            
            if curr_z not in ("outside", entered_z):
                desc += f" into the {curr_z}"
                
            near_v = relationships.get("near_vehicle")
            g_size = relationships.get("group_size", 1)
            
            if g_size > 1:
                desc += f" moving in a group of {g_size}"
            
            if near_v:
                desc += f", remaining near vehicle {near_v} for {relationships.get('near_vehicle_duration')} seconds"

            if "suspicious_loitering" in events:
                desc += f", suspiciously loitering in the zone for {duration} seconds"
            elif "loitering" in events:
                desc += f", loitering in the zone for {duration} seconds"
            else:
                desc += f", staying in view for {duration} seconds"

            desc += "."
            return desc.replace("  ", " ").replace(" ,", ",")

        else:  # Vehicle (car, motorcycle, bus, truck)
            color = vehicle.get("color_name", appearance.get("color", "unknown"))
            vtype = vehicle.get("vehicle_type", appearance.get("vehicle_type", class_name))
            plate = vehicle.get("plate_partial")
            make = appearance.get("make")
            
            desc = "A"
            if color != "unknown":
                desc += f" {color}"
            if make and make != "unknown":
                desc += f" {make}"
            desc += f" {vtype}"
            
            desc += f" entered from {entered_z}" if (entered_z and entered_z != "outside") else " appeared in the area"
            
            if direction not in ("stationary", "unknown"):
                desc += f", traveling {speed} towards the {direction}"
                
            if curr_z not in ("outside", entered_z):
                desc += f" near the {curr_z}"
                
            if "wrong_direction" in events:
                desc += f", moving in the WRONG DIRECTION of traffic"
                
            if plate:
                desc += f" with plate partial {plate}"
                
            desc += f" for a total duration of {duration} seconds."
            return desc.replace("  ", " ").replace(" ,", ",")

    def save_json(self, output_path: str, finalized_records: list = None) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        records = finalized_records if finalized_records is not None else self.finalize()
        with open(output_path, "w") as f:
            json.dump(records, f, indent=2)

    def save_csv(self, output_path: str, finalized_records: list = None) -> None:
        records = finalized_records if finalized_records is not None else self.finalize()
        if not records:
            return
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        fieldnames = [
            "track_id", "camera_id", "class", "vehicle_type", "vehicle_number", "color",
            "upper_body", "lower_body", "first_seen", "last_seen",
            "duration", "zone", "events", "group_size", "near_vehicle", "description",
        ]
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in records:
                upper = r.get("upper_body") or {}
                lower = r.get("lower_body") or {}
                vehicle = r.get("vehicle") or {}

                upper_parts = [p for p in [upper.get("color_name"), upper.get("garment_type")] if p and p != "unknown"]
                lower_parts = [p for p in [lower.get("color_name"), lower.get("garment_type")] if p and p != "unknown"]
                upper_str = " ".join(upper_parts) if upper_parts else "unknown"
                lower_str = " ".join(lower_parts) if lower_parts else "unknown"

                v_num = vehicle.get("plate_partial") or ""
                v_type = vehicle.get("vehicle_type") or r["class"]
                color_name = vehicle.get("color_name") or upper.get("color_name") or r.get("appearance", {}).get("color", "unknown")

                flat_row = {
                    "track_id": r["track_id"],
                    "camera_id": r["camera_id"],
                    "class": r["class"],
                    "vehicle_type": v_type if r["class"] != "person" else "",
                    "vehicle_number": v_num,
                    "color": color_name,
                    "upper_body": upper_str,
                    "lower_body": lower_str,
                    "first_seen": r["first_seen"],
                    "last_seen": r["last_seen"],
                    "duration": r["duration"],
                    "zone": r["location"]["zone"],
                    "events": ",".join(r["events"]),
                    "group_size": r["relationships"]["group_size"],
                    "near_vehicle": r["relationships"]["near_vehicle"],
                    "description": r["description"],
                }
                writer.writerow(flat_row)
