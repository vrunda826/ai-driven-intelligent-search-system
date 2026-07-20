"""Reads frames from a CCTV video file, with optional frame skipping."""

import cv2


class FrameExtractor:
    """Wraps cv2.VideoCapture and yields (frame_index, timestamp_sec, frame) tuples."""

    def __init__(self, video_path: str, frame_skip: int = 1):
        self.video_path = video_path
        self.frame_skip = max(1, frame_skip)

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Could not open video file: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def frames(self):
        """Generator yielding every Nth frame as (frame_index, timestamp_sec, frame_bgr)."""
        frame_idx = 0
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break

            if frame_idx % self.frame_skip == 0:
                timestamp_sec = frame_idx / self.fps if self.fps > 0 else 0.0
                yield frame_idx, timestamp_sec, frame

            frame_idx += 1

        self.cap.release()

    def close(self):
        if self.cap.isOpened():
            self.cap.release()
