"""
Everything about CONNECTING to the camera.
Checks the URL, checks the camera answers, opens the stream, reconnects.
"""


import time
from urllib.parse import urlparse

import cv2

import config
import requests

from config import CONNECTION_TIMEOUT



class CameraConnectionError(Exception):
    """One simple error type, so main.py can show a clean message (no traceback)."""


def validate_url(url):
    """Stop early if the URL is empty or malformed (e.g. 'htp://camera')."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https", "rtsp") or not parsed.hostname:
        raise CameraConnectionError(
            "Invalid camera URL. Expected something like http://192.168.1.23:8080/video "
            "- check CAMERA_URL in your .env file."
        )


def check_reachable(url):
    """
    Ask the camera 'are you there?' with a quick HTTP request BEFORE giving the URL
    to OpenCV. OpenCV can hang for a long time on a dead address; Requests has a
    timeout, so we fail fast with a clear message instead.
    """

    if url.startswith("rtsp"):
        # RTSP cameras don't answer HTTP requests, so we can't check them this way.
        return

    try:
        # stream=True: only fetch the headers, don't download an endless video
        response = requests.get(url, stream=True, timeout=CONNECTION_TIMEOUT)
        status = response.status_code
        response.close()  # don't leave the connection open

    except requests.exceptions.RequestException as e:
        raise CameraConnectionError(
            "Cannot reach the camera. Is it switched on, on the same Wi-Fi, "
            "and are the IP address and port correct?"
        ) from None


    if status in (401, 403):
        raise CameraConnectionError("The camera refused the login. Check the username/password in the URL.")
    if status >= 400:
        raise CameraConnectionError(f"The camera answered with an error (HTTP {status}). Check the URL path.")


def open_stream(url):
    """
    OpenCV can hang for a long time on a dead address, so we check the URL first.
    If it looks good, we return the URL to main.py, which will pass it to OpenCV.
    """
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        cap.release()  # free the resource, just in case
        raise CameraConnectionError(
            "OpenCV cannot open the camera stream. Check the URL and make sure the camera is on."
        )
    
    return cap


def open_camera(url):
    return open_stream(url)


 
def reconnect(cap, url):
    """
    Called when the stream drops. Try a LIMITED number of times, then give up.
    Returns a new, working capture or raises CameraError.
    """
    cap.release()  # throw away the broken connection first
    for attempt in range(1, config.MAX_RECONNECTS + 1):
        print(f"Connection lost. Reconnecting ({attempt}/{config.MAX_RECONNECTS})...")
        
        time.sleep(config.RECONNECT_DELAY)
        try:
            check_reachable(url)
            return open_camera(url)
        except CameraConnectionError:
            continue  # try again
    raise CameraConnectionError("Could not reconnect to the camera. Giving up.")
 