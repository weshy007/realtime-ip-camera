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

 
# Output folders
SCREENSHOT_DIR = "screenshots"
RECORDING_DIR = "recordings"
 