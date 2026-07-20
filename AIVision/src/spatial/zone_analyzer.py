"""Checks spatial positions against polygonal zones using OpenCV.

Traces detailed zone entry, exit, and dwell times.
"""

import cv2
import numpy as np


class ZoneAnalyzer:
    def __init__(self, zones_config: list = None, fps: float = 30.0):
        """zones_config: list of dicts, e.g. [{"name": "Entrance Gate", "polygon": [[x1, y1], ...]}]"""
        self.zones = []
        self.fps = fps
        if zones_config:
            for zone in zones_config:
                name = zone["name"]
                poly = np.array(zone["polygon"], dtype=np.int32).reshape((-1, 1, 2))
                self.zones.append({
                    "name": name,
                    "contour": poly
                })

    def get_zone(self, centroid) -> str:
        """Determine which zone a centroid point (x, y) resides in.

        Returns the zone name, or "outside" if not in any defined zone.
        """
        if not self.zones:
            return "outside"
        
        pt = (float(centroid[0]), float(centroid[1]))
        for zone in self.zones:
            # pointPolygonTest returns >= 0 if inside or on edge
            if cv2.pointPolygonTest(zone["contour"], pt, False) >= 0:
                return zone["name"]
        return "outside"

    def analyze_trajectory(self, history: list, fps: float = None) -> dict:
        """Trace zone traversal history of a trajectory.

        history: list of tuples: (frame_idx, timestamp_str, (cx, cy), bbox)
        """
        effective_fps = fps or self.fps or 30.0

        if not history:
            return {
                "current_zone": "outside",
                "entered_zone": None,
                "exited_zone": None,
                "zones_visited": [],
                "previous_zone": None,
                "entry_timestamp": None,
                "exit_timestamp": None,
                "total_dwell_time": 0.0,
                "zone_history": []
            }

        # Determine zone runs with entry and exit frames
        zone_runs = []
        for item in history:
            f_idx, ts, centroid, bbox = item
            z = self.get_zone(centroid)
            if not zone_runs or zone_runs[-1]["zone"] != z:
                zone_runs.append({
                    "zone": z,
                    "entry_frame": f_idx,
                    "exit_frame": f_idx,
                    "entry_timestamp": ts,
                    "exit_timestamp": ts
                })
            else:
                zone_runs[-1]["exit_frame"] = f_idx
                zone_runs[-1]["exit_timestamp"] = ts

        # Process details for zone history
        zone_history = []
        total_dwell_time = 0.0
        for r in zone_runs:
            dwell = (r["exit_frame"] - r["entry_frame"]) / effective_fps if effective_fps > 0 else 0.0
            dwell = round(max(0.1, dwell), 1)
            
            # Sum dwell time for actual zones, excluding "outside"
            if r["zone"] != "outside":
                total_dwell_time += dwell
                
            zone_history.append({
                "zone": r["zone"],
                "entry_timestamp": r["entry_timestamp"],
                "exit_timestamp": r["exit_timestamp"],
                "dwell_time": dwell
            })

        # Compress consecutive duplicate zones for compatibility
        compressed_zones = [r["zone"] for r in zone_runs]
        actual_zones = [z for z in compressed_zones if z != "outside"]

        current_zone = compressed_zones[-1] if compressed_zones else "outside"
        previous_zone = compressed_zones[-2] if len(compressed_zones) >= 2 else None
        
        entered_zone = actual_zones[0] if actual_zones else None
        
        exited_zone = None
        if len(actual_zones) > 1:
            exited_zone = actual_zones[-1]
        elif len(actual_zones) == 1 and current_zone == "outside":
            exited_zone = actual_zones[0]

        entry_timestamp = zone_history[-1]["entry_timestamp"] if zone_history else None
        exit_timestamp = zone_history[-1]["exit_timestamp"] if zone_history else None

        return {
            # Legacy fields
            "current_zone": current_zone,
            "entered_zone": entered_zone,
            "exited_zone": exited_zone,
            "zones_visited": actual_zones,
            # Upgraded fields
            "previous_zone": previous_zone,
            "entry_timestamp": entry_timestamp,
            "exit_timestamp": exit_timestamp,
            "total_dwell_time": round(total_dwell_time, 1),
            "zone_history": zone_history
        }
