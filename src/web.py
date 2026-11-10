"""
Watch the stream in a browser using Flask.
Run with:  python src/web_app.py   then open http://127.0.0.1:5000
"""
import cv2
from flask import Flask, Response

import config
from camera import check_reachable, open_stream, validate_url
from processing import FPSCounter, draw_overlay, resize_to_width

app = Flask(__name__)


def generate_frames():
    """A generator: each 'yield' sends one JPEG frame to the browser (MJPEG)."""
    validate_url(config.CAMERA_URL)
    check_reachable(config.CAMERA_URL)
    cap = open_stream(config.CAMERA_URL)
    fps_counter = FPSCounter()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = resize_to_width(frame, config.DISPLAY_WIDTH)
            draw_overlay(frame, config.CAMERA_NAME, fps_counter.tick())
            ok, jpeg = cv2.imencode(".jpg", frame)   # frame -> JPEG bytes
            if ok:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + jpeg.tobytes() + b"\r\n")
    finally:
        cap.release()


@app.route("/")
def index():
    return "<h2>Camera dashboard</h2><img src='/video' style='max-width:100%'>"


@app.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    # 127.0.0.1 = only this computer can open it (safer for a camera feed)
    app.run(host="127.0.0.1", port=5000, threaded=True)