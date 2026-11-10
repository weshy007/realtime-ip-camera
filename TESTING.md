# Test Record

Run each test against your own program. For every test fill in **Actual result** and **Status**, and save a screenshot in `docs/evidence/` named after the test ID (e.g. `TC01.png`). Copy these into your PDF report.

**Status key:** ⬜ Not run · ✅ Pass · ❌ Fail

## Automated tests (pytest)

Run `python -m pytest -v` from the project folder. These use a fake camera and check the logic behind the manual test cases. Put a screenshot of the passing run in `docs/evidence/automated-tests.png`.

| Manual test | Automated check | File |
|-------------|-----------------|------|
| TC01 Live stream | Frames are shown, Esc exits and releases everything | `test_main.py` |
| TC02 Invalid URL | Bad URLs rejected; clean message, no traceback | `test_camera.py`, `test_main.py` |
| TC03 Camera unavailable | Timeout is used; clean message, stream never opened | `test_camera.py`, `test_main.py` |
| TC04 Overlays | Stats are drawn top-right; timestamp changes; FPS maths and smoothing | `test_processing.py` |
| TC05 Resizing | 1920x1080 → 960x540; aspect ratio kept | `test_processing.py` |
| TC06 Screenshot | Folder created, separate timestamped PNGs, lossless | `test_media.py`, `test_main.py` |
| TC07 Recording | Playable .mp4, correct frame count, elapsed timer | `test_media.py`, `test_main.py` |
| TC08 Connection drop | Reconnect, recovery, retry limit, recording saved | `test_camera.py`, `test_main.py` |
| TC09 Esc during recording | File saved and playable, camera released | `test_main.py` |
| TC10 Ctrl+C during recording | No exception, file saved, camera released | `test_main.py` |
| TC11 Motion detection | Box around movement, noise and ignored area skipped | `test_motion.py` |
| TC12 Auto-record | Starts on motion, stops after quiet period, manual recording untouched | `test_main.py` |
| TC13 Web dashboard | Routes, buttons, JPEG stream, recording saved on stop | `test_web_app.py` |
| Privacy | No credentials in code, `.env` git-ignored | `test_project_files.py` |

**Automated test result:** ____ passed / ____ failed  **Date:** ____

---

## Summary

| ID | Test | Status | Evidence |
|----|------|--------|----------|
| TC01 | Live stream starts | ⬜ | `docs/evidence/TC01.png` |
| TC02 | Invalid URL | ⬜ | `docs/evidence/TC02.png` |
| TC03 | Camera unavailable | ⬜ | `docs/evidence/TC03.png` |
| TC04 | Overlays | ⬜ | `docs/evidence/TC04.png` |
| TC05 | Resizing | ⬜ | `docs/evidence/TC05.png` |
| TC06 | Screenshot | ⬜ | `docs/evidence/TC06.png` |
| TC07 | Recording | ⬜ | `docs/evidence/TC07.png` |
| TC08 | Connection drop | ⬜ | `docs/evidence/TC08.png` |
| TC09 | Esc during recording | ⬜ | `docs/evidence/TC09.png` |
| TC10 | Ctrl+C during recording | ⬜ | `docs/evidence/TC10.png` |

### Bonus tests

| ID | Test | Status | Evidence |
|----|------|--------|----------|
| TC11 | Motion detection | ⬜ | `docs/evidence/TC11.png` |
| TC12 | Auto-record on motion | ⬜ | `docs/evidence/TC12.png` |
| TC13 | Web dashboard controls | ⬜ | `docs/evidence/TC13.png` |

**Test date:** ____ **Camera used:** ____ **Python / OpenCV version:** ____

---

## TC01 - Live stream starts
- **What to do:** Run `python src/main.py` with the correct camera URL in `.env`.
- **Expected:** A window shows live video within a few seconds.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC01.png`

## TC02 - Invalid URL
- **What to do:** Set `CAMERA_URL=htp://camera` in `.env`, then run the program.
- **Expected:** A clear error message; the program exits cleanly with no traceback.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC02.png`

## TC03 - Camera unavailable
- **What to do:** Stop the camera app (or use a wrong IP address), then run the program.
- **Expected:** It reports that the camera cannot be reached within a reasonable time (about 5 s, no hanging) and exits cleanly.
- **Actual result:**
- **Time taken to report:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC03.png`

## TC04 - Overlays
- **What to do:** Watch the stream for 30 seconds.
- **Expected:** The timestamp updates every second; camera name, resolution and an FPS value are shown and readable.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC04.png`

## TC05 - Resizing
- **What to do:** Compare the window to your configured `DISPLAY_WIDTH`.
- **Expected:** Frames are shown at that width with the aspect ratio kept, nothing stretched or squashed.
- **Actual result:** (note the camera resolution and displayed resolution, e.g. 1920x1080 → 960x540)
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC05.png`

## TC06 - Screenshot
- **What to do:** Press `S` twice, a few seconds apart.
- **Expected:** Two separate timestamped images in `screenshots/`, and an on-screen confirmation each time.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC06.png`

## TC07 - Recording
- **What to do:** Press `R`, wait about 10 seconds, press `R` again.
- **Expected:** A recording status (red dot + "REC" + timer) shows while recording; a timestamped file in `recordings/` plays in a media player and lasts about 10 seconds.
- **Actual result:** (note the file's real duration)
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC07.png`

## TC08 - Connection drop
- **What to do:** While streaming, turn the phone's Wi-Fi off for 10 seconds, then on again.
- **Expected:** The program reports the drop and retries; it recovers when the camera returns, or exits cleanly once its retry limit is reached.
- **Actual result:** (note how many retries it used)
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC08.png`

## TC09 - Esc during recording
- **What to do:** Start a recording with `R`, then press `Esc`.
- **Expected:** The program exits, the window closes, and the recording is saved and plays.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC09.png`

## TC10 - Ctrl+C during recording
- **What to do:** Start a recording with `R`, then press `Ctrl+C` in the terminal.
- **Expected:** No traceback; the recording is saved and plays; the camera is released.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC10.png`

---

## TC11 - Motion detection (bonus)
- **What to do:** Press `M`. Keep still for 5 seconds, then wave a hand in front of the camera.
- **Expected:** "Motion: watching" while still (no boxes); green boxes and "Motion: DETECTED" when you move. The phone app's clock does not trigger boxes.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC11.png`

## TC12 - Auto-record on motion (bonus)
- **What to do:** Press `A`. Wave a hand, then stay still for longer than `QUIET_SECONDS` (default 5 s).
- **Expected:** Recording starts by itself on motion (REC badge appears) and stops after the quiet period; a playable file is in `recordings/`. A manual recording started with `R` is not stopped automatically.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC12.png`

## TC13 - Web dashboard controls (bonus)
- **What to do:** Run `python src/web_app.py`, open `http://127.0.0.1:5000`, click Screenshot, Start/stop recording (about 10 s) and Motion detection.
- **Expected:** Live video in the browser; each button shows a message; a screenshot and a playable recording appear in their folders; boxes appear on motion.
- **Actual result:**
- **Status:** ⬜
- **Evidence:** `docs/evidence/TC13.png`

---

## Bugs found and fixed
| Test ID | Problem | Fix | Commit |
|---------|---------|-----|--------|
| Automated tests | Recording failed to start when the measured FPS spiked right after the stream started (e.g. 96.391 FPS broke the mp4 codec) | Added `safe_fps()`: round the value and cap it at 60 (20 if too low) | |
| | | | |