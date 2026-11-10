"""
Keys:   
    S = screenshot, 
    R = start/stop recording, 
    M = motion detection on/off,
    A = auto-record on motion on/off, 
    Esc = quit
"""
import config
import sys
import time

import cv2

from camera import CameraConnectionError, check_reachable, open_camera, reconnect, validate_url
from media import Recorder, save_screenshot
from motion import MotionDetector, draw_motion
from processing import FPSCounter, draw_overlay, put_text, resize_to_width


WINDOW = "IP Camera Viewer"


def start_recording(recorder, frame, fps):
    """Start a recording. Uses the measured FPS so the video plays at the right speed."""
    return recorder.start(frame, fps if fps >= 5 else 20.0)


def main():
    # ---- 1. Connect (fail early with a friendly message) ----------------
    try:
        validate_url(config.CAMERA_URL)
        check_reachable(config.CAMERA_URL)
        cap = open_camera(config.CAMERA_URL)
    except CameraConnectionError as error:
        print(f"Error: {error}")
        return 1
 
    recorder = Recorder(config.RECORDING_DIR)
    fps_counter = FPSCounter()
    detector = MotionDetector(config.MOTION_MIN_AREA, config.MOTION_IGNORE)

    message, message_until = "", 0.0     # short on-screen confirmation text

    motion_on = False        # M key
    auto_record = False      # A key
    auto_started = False     # True only if the CURRENT recording was started by motion
    last_motion = 0.0        # when motion was last seen
 
    # ---- 2. Main loop ----------------------------------------------------
    try:
        while True:
            ok, frame = cap.read()       # ok = False means the read failed
            if not ok:
                cap = reconnect(cap, config.CAMERA_URL)   # raises CameraError after the limit
                continue
 
            frame = resize_to_width(frame, config.DISPLAY_WIDTH)
            fps = fps_counter.tick()
 
            # Motion runs BEFORE the overlay is drawn, otherwise our own
            # changing clock would count as "motion".
            boxes = detector.detect(frame) if motion_on else []
 
            draw_overlay(frame, config.CAMERA_NAME, fps)
 
            # Auto-record: start on motion, stop after a quiet period
            if auto_record:
                now = time.time()
                if boxes:
                    last_motion = now
                    if not recorder.is_recording:
                        try:
                            start_recording(recorder, frame, fps)
                            auto_started = True
                        except RuntimeError as error:
                            message, message_until = str(error), now + 2
                elif auto_started and recorder.is_recording and now - last_motion > config.QUIET_SECONDS:
                    recorder.stop()
                    auto_started = False
                    message, message_until = "Quiet - recording saved", now + 2
 
            # Save/record the clean frame (before the REC badge is drawn on it)
            if recorder.is_recording:
                recorder.write(frame)
 
            # Draw the temporary status stuff on a COPY, only for the screen
            display = frame.copy()
            h, w = display.shape[:2]
            draw_motion(display, boxes)
            if recorder.is_recording:
                secs = recorder.elapsed()
                cv2.circle(display, (w - 100, h - 20), 8, (0, 0, 255), -1)   # red dot (bottom-right)
                put_text(display, f"REC {secs // 60:02d}:{secs % 60:02d}", (w - 85, h - 14), (0, 0, 255))
            status = ""
            if motion_on:
                status = "Motion: DETECTED" if boxes else "Motion: watching"
            if auto_record:
                status += "  |  Auto-REC on"
            if status:
                put_text(display, status, (10, h - 40), (0, 0, 255) if boxes else (255, 255, 255))
            if time.time() < message_until:
                put_text(display, message, (10, h - 15), (0, 255, 0))
 
            cv2.imshow(WINDOW, display)
 
            # waitKey(1) does two jobs: it lets the window refresh AND reads a key press
            key = cv2.waitKey(1) & 0xFF
            if key == 27:                                    # Esc
                break
            elif key in (ord("s"), ord("S")):
                path = save_screenshot(frame, config.SCREENSHOT_DIR)
                message, message_until = "Screenshot saved", time.time() + 2
                print(f"Saved {path}")
            elif key in (ord("r"), ord("R")):
                auto_started = False                         # manual control from now on
                if recorder.is_recording:
                    recorder.stop()
                    message, message_until = "Recording saved", time.time() + 2
                else:
                    try:
                        print(f"Recording to {start_recording(recorder, frame, fps)}")
                    except RuntimeError as error:
                        message, message_until = str(error), time.time() + 2
            elif key in (ord("m"), ord("M")):
                motion_on = not motion_on
                detector.reset()
                if not motion_on:
                    auto_record = False                      # auto-record needs motion detection
                message, message_until = f"Motion {'on' if motion_on else 'off'}", time.time() + 2
            elif key in (ord("a"), ord("A")):
                auto_record = not auto_record
                if auto_record and not motion_on:
                    motion_on = True
                    detector.reset()
                if not auto_record and auto_started:
                    recorder.stop()                          # stop a motion-started recording
                    auto_started = False
                message, message_until = f"Auto-record {'on' if auto_record else 'off'}", time.time() + 2
 
    except KeyboardInterrupt:                                # Ctrl+C
        print("\nStopped by user.")
    except CameraConnectionError as error:                             # reconnect gave up
        print(f"Error: {error}")
        return 1
 
    # ---- 3. Safe shutdown: runs on Esc, Ctrl+C AND errors ----------------
    finally:
        recorder.stop()          # finish any recording so the file plays
        cap.release()            # free the camera
        cv2.destroyAllWindows()  # close the window
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())