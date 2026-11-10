"""Small fake things the tests share (no real camera needed)."""
import time

import cv2
import numpy as np


def static_frame(n=0, width=640, height=360):
    """A plain grey frame. Nothing moves between frames."""
    return np.full((height, width, 3), 80, np.uint8)


def moving_frame(n, width=640, height=360):
    """A white square that jumps left/right every frame, so motion detection sees movement."""
    frame = static_frame(n, width, height)
    x = 40 if n % 2 == 0 else 360
    cv2.rectangle(frame, (x, 120), (x + 120, 240), (255, 255, 255), -1)
    return frame


class FakeCapture:
    """Pretends to be cv2.VideoCapture.
    frame_fn  - function(n) that returns frame number n
    delay     - seconds each read() takes (like a real camera)
    fail_at   - set of read numbers that fail once
    fail_from - every read from this number on fails (a dead connection)
    """

    def __init__(self, frame_fn=static_frame, delay=0.0, fail_at=(), fail_from=None):
        self.frame_fn = frame_fn
        self.delay = delay
        self.fail_at = set(fail_at)
        self.fail_from = fail_from
        self.n = 0
        self.released = False

    def isOpened(self):
        return not self.released

    def read(self):
        self.n += 1
        if self.delay:
            time.sleep(self.delay)
        if self.n in self.fail_at or (self.fail_from and self.n >= self.fail_from):
            return False, None
        return True, self.frame_fn(self.n)

    def release(self):
        self.released = True


def video_frame_count(path):
    """How many frames a saved video really contains (proves it can be played)."""
    cap = cv2.VideoCapture(str(path))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return count
