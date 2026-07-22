"""Analyzes spatiotemporal relationships (proximity, groups) between tracks over time.

Computes interaction duration, nearest objects, nearest vehicles, and group confidence.
"""

from collections import defaultdict
import numpy as np


class RelationshipAnalyzer:
    def __init__(self, proximity_threshold: float = 150.0, fps: float = 30.0, frame_skip: int = 2):
        self.proximity_threshold = proximity_threshold
        # Adjusted FPS to account for frame skipping in the main loop
        self.effective_fps = fps / frame_skip
        
        # Track pairs close frame counts: (track_key_1, track_key_2) -> int count
        self.close_frames = defaultdict(int)
        # Track pairs total overlapping active frames: (track_key_1, track_key_2) -> int count
        self.overlap_frames = defaultdict(int)
        
        # Track pairs distance list over time to compute average proximity
        self.pair_distances = defaultdict(list)
        
        # Track frames in which they interacted with ANY other object
        self.track_active_frames_close = defaultdict(set)
        
        # Track key -> class_name (to filter person vs vehicle)
        self.track_classes = {}

    def update(self, frame_idx: int, active_tracks: dict) -> None:
        """Update relationships with the tracks active in the current frame.

        active_tracks: dict of track_key -> {"class_name": str, "centroid": (cx, cy)}
        """
        # Save classes for final analysis
        for k, info in active_tracks.items():
            self.track_classes[k] = info["class_name"]

        keys = list(active_tracks.keys())
        n = len(keys)
        for i in range(n):
            k1 = keys[i]
            p1 = np.array(active_tracks[k1]["centroid"])
            for j in range(i + 1, n):
                k2 = keys[j]
                p2 = np.array(active_tracks[k2]["centroid"])
                
                # Maintain lexicographical sorting for keys in dict
                pair = (k1, k2) if k1 < k2 else (k2, k1)
                
                self.overlap_frames[pair] += 1
                dist = float(np.linalg.norm(p1 - p2))
                self.pair_distances[pair].append(dist)
                
                if dist <= self.proximity_threshold:
                    self.close_frames[pair] += 1
                    self.track_active_frames_close[k1].add(frame_idx)
                    self.track_active_frames_close[k2].add(frame_idx)

    def finalize(self) -> dict:
        """Compile relationship metadata for all tracks.

        Returns:
            dict of track_key -> {
                "near_vehicle": str or None,
                "near_vehicle_duration": float,
                "group_size": int,
                "interaction_duration": float,
                "nearest_object": str or None,
                "nearest_vehicle": str or None,
                "group_confidence": float
            }
        """
        persons = [k for k, c in self.track_classes.items() if c == "person"]
        vehicles = [k for k, c in self.track_classes.items() if c in ("car", "motorcycle", "bus", "truck")]
        all_tracks = list(self.track_classes.keys())

        # Initialize results for all tracks
        results = {
            k: {
                "near_vehicle": None,
                "near_vehicle_duration": 0.0,
                "group_size": 1,
                "interaction_duration": 0.0,
                "nearest_object": None,
                "nearest_vehicle": None,
                "group_confidence": 0.0
            }
            for k in all_tracks
        }

        # 1. Compute 'near_vehicle' relationships and nearest objects
        min_close_frames = 2.0 * self.effective_fps

        for t1 in all_tracks:
            # Interaction Duration (total seconds spent close to any other object)
            close_frames_set = self.track_active_frames_close.get(t1, set())
            results[t1]["interaction_duration"] = round(len(close_frames_set) / self.effective_fps, 1)

            # Nearest Object and Nearest Vehicle Search
            best_obj, best_veh = None, None
            min_avg_dist_obj, min_avg_dist_veh = float('inf'), float('inf')

            for t2 in all_tracks:
                if t1 == t2:
                    continue
                pair = (t1, t2) if t1 < t2 else (t2, t1)
                if pair in self.pair_distances:
                    avg_dist = float(np.mean(self.pair_distances[pair]))
                    
                    if avg_dist < min_avg_dist_obj:
                        min_avg_dist_obj = avg_dist
                        best_obj = t2
                        
                    if self.track_classes[t2] in ("car", "motorcycle", "bus", "truck"):
                        if avg_dist < min_avg_dist_veh:
                            min_avg_dist_veh = avg_dist
                            best_veh = t2

            results[t1]["nearest_object"] = best_obj
            results[t1]["nearest_vehicle"] = best_veh

            # Legacy 'near_vehicle' logic for pedestrians
            if self.track_classes[t1] == "person":
                best_near_veh = None
                max_close = 0
                for v in vehicles:
                    pair = (t1, v) if t1 < v else (v, t1)
                    close_cnt = self.close_frames.get(pair, 0)
                    if close_cnt >= min_close_frames and close_cnt > max_close:
                        max_close = close_cnt
                        best_near_veh = v
                
                if best_near_veh:
                    duration_sec = max_close / self.effective_fps
                    results[t1]["near_vehicle"] = best_near_veh
                    results[t1]["near_vehicle_duration"] = round(duration_sec, 1)

        # 2. Compute group sizes and group confidence for persons
        adj = defaultdict(set)
        for i in range(len(persons)):
            p1 = persons[i]
            for j in range(i + 1, len(persons)):
                p2 = persons[j]
                pair = (p1, p2) if p1 < p2 else (p2, p1)
                
                close_cnt = self.close_frames.get(pair, 0)
                overlap_cnt = self.overlap_frames.get(pair, 0)
                
                # Close for at least 1.5 seconds AND close for at least 40% of co-existence
                if overlap_cnt > 0:
                    pct_close = close_cnt / overlap_cnt
                    if close_cnt >= (1.5 * self.effective_fps) and pct_close >= 0.4:
                        adj[p1].add(p2)
                        adj[p2].add(p1)

        # Find connected components (groups)
        visited = set()
        for p in persons:
            if p not in visited:
                comp = []
                queue = [p]
                visited.add(p)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                group_size = len(comp)
                for member in comp:
                    results[member]["group_size"] = group_size
                    
                    if group_size > 1:
                        # Group confidence: average overlap proximity ratio with other members
                        ratios = []
                        for other in comp:
                            if member == other:
                                continue
                            pair = (member, other) if member < other else (other, member)
                            c_cnt = self.close_frames.get(pair, 0)
                            o_cnt = self.overlap_frames.get(pair, 0)
                            if o_cnt > 0:
                                ratios.append(c_cnt / o_cnt)
                        avg_ratio = float(np.mean(ratios)) if ratios else 0.0
                        results[member]["group_confidence"] = round(avg_ratio, 2)
                    else:
                        results[member]["group_confidence"] = 0.0

        return results
