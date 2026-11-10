"""
media.py - saving things: screenshots and video recordings.
"""
import os
import time
import math
from datetime import datetime

import cv2


def safe_fps(fps):
    """Use a playable FPS when measurement is unavailable or outside codec limits."""
    fps = float(fps)
    if not math.isfinite(fps) or fps < 5:
        return 20.0
    return float(min(round(fps), 60))


def timestamp():
    """e.g. 20261109_143005_123 - includes milliseconds so files never overwrite each other."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]


def save_screenshot(frame, folder):
    os.makedirs(folder, exist_ok=True)               # create the folder if missing
    path = os.path.join(folder, f"screenshot_{timestamp()}.png")
    cv2.imwrite(path, frame)
    return path


class Recorder:
    """Wraps cv2.VideoWriter. VideoWriter needs: filename, codec, FPS and frame size."""

    def __init__(self, folder):
        self.folder = folder
        self.writer = None
        self.size = None            # (width, height) declared when recording starts
        self.start_time = 0.0

    @property
    def is_recording(self):
        return self.writer is not None

    def start(self, frame, fps):
        os.makedirs(self.folder, exist_ok=True)
        fps = safe_fps(fps)
        height, width = frame.shape[:2]
        self.size = (width, height)
        path = os.path.join(self.folder, f"recording_{timestamp()}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")     # codec for .mp4 files
        self.writer = cv2.VideoWriter(path, fourcc, fps, self.size)
        if not self.writer.isOpened():
            self.writer = None
            raise RuntimeError("Could not start the recording.")
        self.start_time = time.time()
        return path

    def write(self, frame):
        if self.writer is None:
            return
        # A frame with a different size than declared would be silently dropped
        # (broken video), so we resize it to match.
        if (frame.shape[1], frame.shape[0]) != self.size:
            frame = cv2.resize(frame, self.size)
        self.writer.write(frame)

    def elapsed(self):
        return int(time.time() - self.start_time) if self.is_recording else 0

    def stop(self):
        """release() finishes the file. Without it the video can be corrupt/unplayable."""
        if self.writer is not None:
            self.writer.release()
            self.writer = None