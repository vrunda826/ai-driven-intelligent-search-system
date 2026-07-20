"""Draws detection/tracking results onto frames and writes the annotated video."""

import cv2
import supervision as sv


class Annotator:
    def __init__(self):
        self.box_annotator = sv.BoxAnnotator(thickness=2)
        self.label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)

    def annotate(self, frame, detections: sv.Detections, labels: list):
        """Return a copy of `frame` with boxes and labels drawn on it."""
        annotated = self.box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated = self.label_annotator.annotate(scene=annotated, detections=detections, labels=labels)
        return annotated

    @staticmethod
    def build_labels(detections: sv.Detections, class_names: dict) -> list:
        """Build "ClassName #track_id (conf)" labels for each detection."""
        labels = []
        for class_id, tracker_id, confidence in zip(
            detections.class_id, detections.tracker_id, detections.confidence
        ):
            name = class_names.get(int(class_id), str(class_id))
            tid = f"#{int(tracker_id)}" if tracker_id is not None else ""
            labels.append(f"{name} {tid} {confidence:.2f}")
        return labels


class VideoWriter:
    """Thin wrapper around cv2.VideoWriter for writing the annotated output video."""

    def __init__(self, output_path: str, fps: float, width: int, height: int):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        self.writer.release()
