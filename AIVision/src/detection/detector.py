"""YOLO object detection wrapper (Ultralytics YOLOv11/YOLOv12-compatible weights).

Returns detections as a supervision.Detections object so downstream tracking
and visualization modules stay decoupled from the specific detector used.
"""

import supervision as sv
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.4,
                 iou_threshold: float = 0.5, classes: list = None):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.classes = classes  # None = detect all classes the model knows

    def detect(self, frame) -> sv.Detections:
        """Run detection on a single frame (BGR numpy array).

        Returns a supervision.Detections instance with .xyxy, .confidence,
        .class_id populated, already filtered to `self.classes`.
        """
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            classes=self.classes,
            verbose=False,
        )[0]

        detections = sv.Detections.from_ultralytics(results)
        return detections

    @property
    def class_names(self) -> dict:
        """Mapping of class_id -> class name, e.g. {0: 'person', 2: 'car', ...}."""
        return self.model.names
