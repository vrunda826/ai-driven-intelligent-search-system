"""Computes motion metadata from track trajectory histories, including acceleration,

stationary duration, movement confidence, and direction smoothing.
"""

import math
import numpy as np


class MotionAnalyzer:
    def __init__(self, speed_threshold_slow: float = 2.0,
                 speed_threshold_fast: float = 8.0,
                 fps: float = 30.0,
                 direction_smoothing_window: int = 7):
        self.speed_threshold_slow = speed_threshold_slow
        self.speed_threshold_fast = speed_threshold_fast
        self.fps = fps
        self.direction_smoothing_window = direction_smoothing_window

    def analyze(self, history: list) -> dict:
        """Analyze a list of trajectory points for motion metadata.

        history: list of tuples: (frame_idx, timestamp_str, (cx, cy), bbox)
        """
        if len(history) < 2:
            return {
                "speed": "stationary",
                "direction": "unknown",
                "distance": 0.0,
                "average_speed": 0.0,
                "status": "stationary",
                "acceleration": 0.0,
                "stationary_duration": 0.0,
                "movement_confidence": 0.0,
                "smoothed_direction": "unknown"
            }

        # Extract centroids
        centroids = [item[2] for item in history]
        pts = np.array(centroids)

        # 1. Cumulative Euclidean distance
        diffs = np.diff(pts, axis=0)
        step_distances = np.linalg.norm(diffs, axis=1)
        total_distance = float(np.sum(step_distances))

        # Frames elapsed
        start_frame = history[0][0]
        end_frame = history[-1][0]
        num_frames = end_frame - start_frame
        if num_frames <= 0:
            num_frames = len(history) - 1

        # Average speed (pixels per frame)
        avg_speed_px_frame = total_distance / max(1, num_frames)

        # Average speed in pixels per second
        avg_speed_px_sec = avg_speed_px_frame * self.fps

        # 2. Acceleration Calculation (average magnitude of acceleration in px/sec^2)
        velocities = []
        for idx in range(1, len(history)):
            dt = (history[idx][0] - history[idx-1][0]) / self.fps
            if dt > 0:
                dist = np.linalg.norm(np.array(centroids[idx]) - np.array(centroids[idx-1]))
                v = dist / dt
                velocities.append((v, dt))

        accelerations = []
        for idx in range(1, len(velocities)):
            dv = velocities[idx][0] - velocities[idx-1][0]
            dt = velocities[idx][1]
            if dt > 0:
                a = dv / dt
                accelerations.append(abs(a))
        
        avg_acceleration = float(np.mean(accelerations)) if accelerations else 0.0

        # 3. Stationary Duration: Max continuous duration speed < speed_threshold_slow
        max_stat_duration = 0.0
        current_stat_duration = 0.0
        for idx in range(1, len(history)):
            dt = (history[idx][0] - history[idx-1][0]) / self.fps
            dist = np.linalg.norm(np.array(centroids[idx]) - np.array(centroids[idx-1]))
            speed_px_frame = dist / max(1, history[idx][0] - history[idx-1][0])
            if speed_px_frame < self.speed_threshold_slow:
                current_stat_duration += dt
            else:
                max_stat_duration = max(max_stat_duration, current_stat_duration)
                current_stat_duration = 0.0
        max_stat_duration = max(max_stat_duration, current_stat_duration)

        # 4. Movement Confidence: Soft sigmoid based on displacement relative to noise jitter
        start_pt = pts[0]
        end_pt = pts[-1]
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        displacement = math.hypot(dx, dy)
        
        # Sigmoid centered around 15 pixels displacement
        movement_confidence = float(1.0 / (1.0 + np.exp(-(displacement - 15.0) / 5.0)))

        # 5. Direction & Smoothed Direction calculation
        direction = self._calculate_heading(start_pt, end_pt, displacement)

        # Compute smoothed centroids using moving average
        window = min(len(history), self.direction_smoothing_window)
        smoothed_centroids = []
        for i in range(len(history)):
            start_idx = max(0, i - window + 1)
            sub = centroids[start_idx : i + 1]
            cx_mean = np.mean([pt[0] for pt in sub])
            cy_mean = np.mean([pt[1] for pt in sub])
            smoothed_centroids.append((cx_mean, cy_mean))

        smoothed_start = smoothed_centroids[0]
        smoothed_end = smoothed_centroids[-1]
        sdx = smoothed_end[0] - smoothed_start[0]
        sdy = smoothed_end[1] - smoothed_start[1]
        smoothed_displacement = math.hypot(sdx, sdy)
        smoothed_direction = self._calculate_heading(smoothed_start, smoothed_end, smoothed_displacement)

        # Determine status and speed category
        if avg_speed_px_frame < 0.2 and displacement < 10.0:
            status = "stationary"
            speed_desc = "stationary"
        elif avg_speed_px_frame < self.speed_threshold_slow:
            status = "moving"
            speed_desc = "slow"
        elif avg_speed_px_frame < self.speed_threshold_fast:
            status = "moving"
            speed_desc = "medium"
        else:
            status = "moving"
            speed_desc = "fast"

        return {
            "speed": speed_desc,
            "direction": direction,
            "distance": round(total_distance, 1),
            "average_speed": round(avg_speed_px_sec, 1),  # px/sec
            "status": status,
            "acceleration": round(avg_acceleration, 2),
            "stationary_duration": round(max_stat_duration, 1),
            "movement_confidence": round(movement_confidence, 2),
            "smoothed_direction": smoothed_direction
        }

    @staticmethod
    def _calculate_heading(start_pt, end_pt, displacement) -> str:
        if displacement < 15.0:
            return "stationary"
        
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        
        angle_rad = math.atan2(-dy, dx)
        angle_deg = math.degrees(angle_rad) # range [-180, 180]
        
        if -22.5 <= angle_deg < 22.5:
            direction = "east"
        elif 22.5 <= angle_deg < 67.5:
            direction = "northeast"
        elif 67.5 <= angle_deg < 112.5:
            direction = "north"
        elif 112.5 <= angle_deg < 157.5:
            direction = "northwest"
        elif angle_deg >= 157.5 or angle_deg < -157.5:
            direction = "west"
        elif -157.5 <= angle_deg < -112.5:
            direction = "southwest"
        elif -112.5 <= angle_deg < -67.5:
            direction = "south"
        else: # -67.5 <= angle_deg < -22.5
            direction = "southeast"
            
        return direction
