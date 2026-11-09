"""
Keys: S = screenshot, R = start/stop recording, Esc = quit
"""
import sys
import time

import cv2

import config
from camera import CameraConnectionError, check_reachable, open_stream, reconnect, validate_url
from media import Recorder, save_screenshot
from processing import FPSCounter, draw_overlay, put_text, resize_to_width

WINDOW = "IP Camera Viewer"


def main():
    # ---- 1. Connect (fail early with a friendly message) ----------------
    try:
        validate_url(config.CAMERA_URL)
        check_reachable(config.CAMERA_URL)
        cap = open_stream(config.CAMERA_URL)
    except CameraConnectionError as error:
        print(f"Error: {error}")
        return 1
 
    recorder = Recorder(config.RECORDING_DIR)
    fps_counter = FPSCounter()
    message, message_until = "", 0.0     # short on-screen confirmation text
 
    # ---- 2. Main loop ----------------------------------------------------
    try:
        while True:
            ok, frame = cap.read()       # ok = False means the read failed
            if not ok:
                cap = reconnect(cap, config.CAMERA_URL)   # raises CameraError after the limit
                continue
 
            # Process the frame
            frame = resize_to_width(frame, config.DISPLAY_WIDTH)
            fps = fps_counter.tick()
            draw_overlay(frame, config.CAMERA_NAME, fps)
 
            # Save/record the clean frame (before the REC badge is drawn on it)
            if recorder.is_recording:
                recorder.write(frame)
 
            # Draw the temporary status stuff on a COPY, only for the screen
            display = frame.copy()
            h, w = display.shape[:2]
            if recorder.is_recording:
                secs = recorder.elapsed()
                cv2.circle(display, (w - 100, h - 20), 8, (0, 0, 255), -1)   # red dot (bottom-right)
                put_text(display, f"REC {secs // 60:02d}:{secs % 60:02d}", (w - 85, h - 14), (0, 0, 255))
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
                if recorder.is_recording:
                    recorder.stop()
                    message, message_until = "Recording saved", time.time() + 2
                else:
                    try:
                        # Use the measured FPS so the video plays at the right speed
                        rec_fps = fps if fps >= 5 else 20.0
                        print(f"Recording to {recorder.start(frame, rec_fps)}")
                    except RuntimeError as error:
                        message, message_until = str(error), time.time() + 2
 
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