"""Prepares raw frames for detection: resize + light denoising.

Detection runs on the resized/denoised frame for speed, but crops for attribute
extraction are taken from the original full-resolution frame for quality. This
module returns the scale factors needed to map detection boxes back to
original-frame coordinates.
"""

import cv2


class FramePreprocessor:
    def __init__(self, resize_width: int, resize_height: int, denoise: bool = True):
        self.resize_width = resize_width
        self.resize_height = resize_height
        self.denoise = denoise

    def process(self, frame):
        """Returns (processed_frame, scale_x, scale_y) where scale_* map processed
        coordinates back to the original frame: original_coord = processed_coord * scale.
        """
        orig_h, orig_w = frame.shape[:2]

        resized = cv2.resize(frame, (self.resize_width, self.resize_height), interpolation=cv2.INTER_AREA)

        if self.denoise:
            # Bilateral filter smooths noise while keeping edges reasonably sharp,
            # and is much cheaper than fastNlMeansDenoisingColored for real-time use.
            resized = cv2.bilateralFilter(resized, d=5, sigmaColor=50, sigmaSpace=50)

        scale_x = orig_w / self.resize_width
        scale_y = orig_h / self.resize_height

        return resized, scale_x, scale_y

    @staticmethod
    def scale_boxes(xyxy, scale_x: float, scale_y: float):
        """Rescale an array of [x1, y1, x2, y2] boxes from processed-frame space
        back to original-frame space, in place semantics (returns new array)."""
        scaled = xyxy.copy()
        scaled[:, [0, 2]] *= scale_x
        scaled[:, [1, 3]] *= scale_y
        return scaled
