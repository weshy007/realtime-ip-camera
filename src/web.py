"""
Watch the stream in a browser using Flask.
Run with:  python src/web_app.py   then open http://127.0.0.1:5000
"""
import sys
import time
import threading

import config
import cv2

from flask import Flask, Response, jsonify


from camera import CameraConnectionError, check_reachable, validate_url, open_camera, reconnect
from media import Recorder, save_screenshot
from motion import MotionDetector, draw_motion
from processing import FPSCounter, draw_overlay, resize_to_width, put_text



app = Flask(__name__)
worker = None   # the camera thread (created in main)


class CameraWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.lock = threading.Lock()   # the thread and the button routes share data, so we lock
        self.running = True
        self.frame = None              # newest frame (used by screenshot / record)
        self.jpeg = None               # newest picture for the browser
        self.fps = 0.0
        self.recorder = Recorder(config.RECORDING_DIR)
        self.detector = MotionDetector(config.MOTION_MIN_AREA, config.MOTION_IGNORE)
        self.motion_on = False
 
    # ---- called by the buttons ----
    def take_screenshot(self):
        with self.lock:
            if self.frame is None:
                return "No video yet"
            return f"Saved {save_screenshot(self.frame, config.SCREENSHOT_DIR)}"
 
    def toggle_recording(self):
        with self.lock:
            if self.recorder.is_recording:
                self.recorder.stop()
                return "Recording saved"
            if self.frame is None:
                return "No video yet"
            try:
                path = self.recorder.start(self.frame, self.fps if self.fps >= 5 else 20.0)
            except RuntimeError as error:
                return str(error)
            return f"Recording to {path}"
 
    def toggle_motion(self):
        with self.lock:
            self.motion_on = not self.motion_on
            self.detector.reset()
            return f"Motion detection {'on' if self.motion_on else 'off'}"
 
    # ---- the camera loop (runs in its own thread) ----
    def run(self):
        cap = None
        fps_counter = FPSCounter()
        try:
            cap = open_camera(config.CAMERA_URL)
            while self.running:
                ok, frame = cap.read()
                if not ok:
                    cap = reconnect(cap, config.CAMERA_URL)
                    continue
 
                frame = resize_to_width(frame, config.DISPLAY_WIDTH)
                self.fps = fps_counter.tick()
                boxes = self.detector.detect(frame) if self.motion_on else []
                draw_overlay(frame, config.CAMERA_NAME, self.fps)
 
                with self.lock:
                    self.frame = frame
                    if self.recorder.is_recording:
                        self.recorder.write(frame)
                    recording, secs = self.recorder.is_recording, self.recorder.elapsed()
 
                display = frame.copy()
                h, w = display.shape[:2]
                draw_motion(display, boxes)
                if recording:
                    cv2.circle(display, (w - 100, h - 20), 8, (0, 0, 255), -1)
                    put_text(display, f"REC {secs // 60:02d}:{secs % 60:02d}", (w - 85, h - 14), (0, 0, 255))
 
                ok, jpeg = cv2.imencode(".jpg", display)     # frame -> JPEG bytes
                if ok:
                    with self.lock:
                        self.jpeg = jpeg.tobytes()
        except CameraConnectionError as error:
            print(f"Error: {error}")
        finally:
            with self.lock:
                self.recorder.stop()     # always finish the recording file
            if cap is not None:
                cap.release()
 
 
PAGE = """
<h2>Camera dashboard</h2>
<img src="/video" style="max-width:100%"><br><br>
<button onclick="act('/screenshot')">Screenshot</button>
<button onclick="act('/record')">Start / stop recording</button>
<button onclick="act('/motion')">Motion detection on / off</button>
<p id="msg"></p>
<script>
function act(path) {
  fetch(path, {method: 'POST'}).then(r => r.json())
    .then(d => document.getElementById('msg').textContent = d.message);
}
</script>
"""
 
 
@app.route("/")
def index():
    return PAGE
 
 
@app.route("/video")
def video():
    def stream():                                  # a generator: each yield = one JPEG frame (MJPEG)
        while worker.is_alive():
            with worker.lock:
                jpeg = worker.jpeg
            if jpeg:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            time.sleep(0.03)
    return Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame")
 
 
@app.route("/screenshot", methods=["POST"])
def screenshot():
    return jsonify(message=worker.take_screenshot())
 
 
@app.route("/record", methods=["POST"])
def record():
    return jsonify(message=worker.toggle_recording())
 
 
@app.route("/motion", methods=["POST"])
def motion():
    return jsonify(message=worker.toggle_motion())
 
 
if __name__ == "__main__":
    try:
        validate_url(config.CAMERA_URL)
        check_reachable(config.CAMERA_URL)
    except CameraConnectionError as error:
        print(f"Error: {error}")
        sys.exit(1)
 
    worker = CameraWorker()
    worker.start()
    try:
        # 127.0.0.1 = only this computer can open it (safer for a camera feed)
        app.run(host="127.0.0.1", port=5000, threaded=True)
    finally:
        worker.running = False
        worker.join(timeout=3)   # lets the worker finish the recording and release the camera
 