"""Multi-object tracking using ByteTrack (via the `supervision` library).

Takes per-frame detections from ObjectDetector and assigns persistent
tracker_id values so the same physical person/vehicle keeps one identity
across frames, even through brief occlusion.
"""

import supervision as sv


class ObjectTracker:
    def __init__(self, track_activation_threshold: float = 0.25,
                 lost_track_buffer: int = 30,
                 minimum_matching_threshold: float = 0.8,
                 frame_rate: int = 30):
        self.tracker = sv.ByteTrack(
            track_activation_threshold=track_activation_threshold,
            lost_track_buffer=lost_track_buffer,
            minimum_matching_threshold=minimum_matching_threshold,
            frame_rate=frame_rate,
        )

    def update(self, detections: sv.Detections) -> sv.Detections:
        """Feed one frame's detections in, get back detections with `tracker_id` set.

        Detections that ByteTrack hasn't confirmed as a stable track yet may be
        dropped from the output on early frames — this is expected behavior.
        """
        return self.tracker.update_with_detections(detections)

    def reset(self):
        """Clear all track state, e.g. between separate video files."""
        self.tracker.reset()
