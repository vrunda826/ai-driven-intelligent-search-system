"""Maintains trajectory histories (centroids, frame indices, and timestamps) for active tracks."""

from collections import defaultdict


class TrajectoryTracker:
    def __init__(self):
        # track_key -> list of tuples: (frame_idx, timestamp_str, (x_center, y_center), bbox)
        self.histories = defaultdict(list)

    def add_point(self, track_key: str, frame_idx: int, timestamp: str, bbox_xyxy) -> None:
        """Record the position of a tracked object at a specific frame."""
        x1, y1, x2, y2 = bbox_xyxy
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        self.histories[track_key].append((frame_idx, timestamp, (cx, cy), tuple(bbox_xyxy)))

    def get_history(self, track_key: str) -> list:
        """Get the complete history list for a track."""
        return self.histories.get(track_key, [])

    def get_centroids(self, track_key: str) -> list:
        """Get a list of (x, y) centroids for the track."""
        return [item[2] for item in self.histories.get(track_key, [])]

    def get_last_centroid(self, track_key: str):
        """Get the most recent (x, y) centroid of the track."""
        history = self.histories.get(track_key)
        if history:
            return history[-1][2]
        return None

    def get_last_bbox(self, track_key: str):
        """Get the most recent bbox of the track."""
        history = self.histories.get(track_key)
        if history:
            return history[-1][3]
        return None

    def clear(self) -> None:
        """Clear all stored trajectories."""
        self.histories.clear()
