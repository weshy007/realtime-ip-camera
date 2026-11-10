"""
Idea: compare each frame with the previous one. Pixels that changed a lot = something moved.
"""
import cv2


class MotionDetector:
    def __init__(self, min_area=1500, ignore_box=None):
        self.min_area = min_area        # ignore tiny changes (noise); measured in pixels
        self.ignore_box = ignore_box    # (x, y, w, h) area to ignore, e.g. an app watermark
        self.previous = None            # the previous frame in grey

    def reset(self):
        """Forget the previous frame (use when detection is switched on again)."""
        self.previous = None

    def detect(self, frame):
        """Return a list of (x, y, w, h) boxes around the areas that moved."""
        # 1. Grey + blur: colour is not needed, and blur hides camera noise
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # First frame (or the size changed after a reconnect): nothing to compare with yet
        if self.previous is None or self.previous.shape != gray.shape:
            self.previous = gray
            return []

        # 2. Difference between this frame and the last one
        diff = cv2.absdiff(self.previous, gray)
        self.previous = gray

        # 3. Pixels that changed by more than 25 (out of 255) become white
        _, mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # Blank out the ignored area (the phone app's clock changes every second!)
        if self.ignore_box:
            x, y, w, h = self.ignore_box
            mask[y:y + h, x:x + w] = 0

        # 4. Grow the white blobs so nearby bits join into one object
        mask = cv2.dilate(mask, None, iterations=2)

        # 5. Find the outlines of the blobs and keep only the big ones
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) >= self.min_area]


def draw_motion(frame, boxes):
    """Draw a green rectangle around each moving area (BGR: green = (0, 255, 0))."""
    for x, y, w, h in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)