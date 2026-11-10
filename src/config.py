"""
All settings live here, NOT hard-coded in the other files.
 
Values come from environment variables or from a local ".env" file
(which is in .gitignore, so your camera address/password never reach GitHub).
"""

from decouple import config

CAMERA_URL = config("CAMERA_URL", "")
CAMERA_NAME = config("CAMERA_NAME", "Camera 1")
DISPLAY_WIDTH = int(config("DISPLAY_WIDTH", "960"))


# Error-handling limits
CONNECTION_TIMEOUT = 5                                # seconds to wait for the camera to answer
MAX_RECONNECTS = int(config("MAX_RECONNECTS", "5"))
RECONNECT_DELAY = 2                                # seconds between reconnect attempts


# Motion detection
MOTION_MIN_AREA = config("MOTION_MIN_AREA", "1500")   # smaller = more sensitive
QUIET_SECONDS = int(config("QUIET_SECONDS", "5"))          # no motion this long -> stop auto-recording

def _parse_box(text):
    """'0,0,320,200' -> (0, 0, 320, 200). Empty/invalid -> None (nothing ignored)."""
    try:
        x, y, w, h = [int(v) for v in text.split(",")]
        return (x, y, w, h)
    except ValueError:
        return None

# Area (x,y,w,h) where motion is ignored. Default covers the IP Camera Lite watermark (top-left).
MOTION_IGNORE = _parse_box(config("MOTION_IGNORE", "0,0,320,200"))

 
# Output folders
SCREENSHOT_DIR = "screenshots"
RECORDING_DIR = "recordings"
 