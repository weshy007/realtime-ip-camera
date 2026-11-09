"""
EVERY frame: resize, FPS estimate, text overlay.
Remember: OpenCV frames are NumPy arrays with shape (height, width, 3) in BGR colour order.
"""
import time
from datetime import datetime

import cv2


def resize_to_width(frame, width):
    """Resize to a fixed width, keeping the aspect ratio (nothing stretched)."""
    h, w = frame.shape[:2]          # shape is (height, width, channels)
    scale = width / w               # e.g. 960 / 1920 = 0.5
    new_height = int(h * scale)     # e.g. 1080 * 0.5 = 540
    return cv2.resize(frame, (width, new_height))   # NOTE: cv2.resize wants (width, height)


class FPSCounter:
    """
    FPS = 1 / (time between two frames). One frame's timing is jumpy, so we
    smooth it: keep 90% of the old value and mix in 10% of the new one.
    """
    def __init__(self, smoothing=0.9):
        self.last_time = time.time()
        self.fps = 0.0
        self.smoothing = smoothing

    def tick(self):
        now = time.time()
        delta = now - self.last_time
        self.last_time = now
        if delta > 0:
            current = 1.0 / delta
            self.fps = current if self.fps == 0 else (
                self.smoothing * self.fps + (1 - self.smoothing) * current
            )
        return self.fps


def put_text(frame, text, pos, color=(255, 255, 255), scale=0.6):
    """Draw text with a black outline so it is readable on any background.
    Colours are BGR: (0, 0, 255) is RED, (0, 255, 0) is GREEN."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, text, pos, font, scale, (0, 0, 0), 3, cv2.LINE_AA)   # outline
    cv2.putText(frame, text, pos, font, scale, color, 1, cv2.LINE_AA)       # text


def draw_overlay(frame, camera_name, fps):
    h, w = frame.shape[:2]
    lines = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        camera_name,
        f"{w}x{h}",
        f"FPS: {fps:.1f}",
    ]
    margin, y = 10, 25
    for line in lines:
        # getTextSize gives the text width, so we can align it to the right edge
        (text_w, _), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        put_text(frame, line, (w - text_w - margin, y))
        y += 25   # next line goes lower