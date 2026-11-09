# Test Record

Run each test against your own program. For every test fill in **Actual result** and **Status**, and save a screenshot in `docs/evidence/` named after the test ID (e.g. `TC01.png`). Copy these into your PDF report.

**Status key:** ⬜ Not run · ✅ Pass · ❌ Fail

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

## Bugs found and fixed
| Test ID | Problem | Fix | Commit |
|---------|---------|-----|--------|
| | | | |