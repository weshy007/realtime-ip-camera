# IP Camera Viewer

A lightweight Python desktop viewer for an IP camera (or a phone running **IP Webcam**) on your local network. It shows live video with overlays, takes screenshots, records video and survives network problems.

> ⚠️ Only use a camera you own or have explicit permission to use. Never commit your camera address, username or password.

## Features
- Live stream with OpenCV
- Resize + overlay: date/time, camera name, resolution, estimated FPS
- `S` = screenshot, `R` = start/stop recording, `Esc` = quit
- Clean errors for bad URL, camera off, dropped connection, failed reads
- Safe shutdown (recording saved, camera released, windows closed)

## Folder structure

```
ip-camera-viewer/
├── src/
│   ├── main.py          # The program: main loop + key handling + safe shutdown
│   ├── config.py        # Settings read from .env (no secrets in code)
│   ├── camera.py        # Validate URL, check camera is reachable, open, reconnect
│   ├── processing.py    # Resize, FPS counter, text overlay
│   ├── media.py         # Screenshot saving + video Recorder
│   └── web.py           # Flask browser dashboard
├── screenshots/         # Saved screenshots (created automatically)
├── recordings/          # Saved videos (created automatically)
├── docs/
│   ├── report.pdf       # report (technical questions + test evidence)
│   └── evidence/        # Screenshots proving each test case
├── .env                 # YOUR camera URL (git-ignored)
├── .env.example         # Template to copy to .env 
├── .gitignore
├── requirements.txt
├── README.md
└── TESTING.md           # Test cases TC01-TC10 with a results log
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your camera settings
copy .env.example .env         # Windows   (macOS/Linux: cp .env.example .env)
# then edit .env and put in your real camera URL

# 4. Run
python src/main.py
```

**Phone as a camera:** install IP Webcam (Android), join the same Wi-Fi as your computer, tap *Start server* and copy the URL it shows, adding `/video` (e.g. `http://192.168.1.23:8080/video`).

## Controls

| Key | Action |
|-----|--------|
| `S` | Save a screenshot to `screenshots/` |
| `R` | Start / stop recording to `recordings/` |
| `Esc` | Quit (Ctrl+C in the terminal also works) |

## The 5 steps

Commit at the end of every step.

| Step | Goal | Brief phase | Files | Done when |
|------|------|-------------|-------|-----------|
| **1. Setup** | Folder, venv, dependencies, camera running, URL in `.env`, `.gitignore` | Phase 1 | `.env`, `.gitignore`, `requirements.txt`, `config.py` | `.env` is ignored by Git; phone stream opens in a browser |
| **2. Live stream** | Connect, read frames, show a window, Esc quits and releases everything | Phase 2 | `camera.py`, `main.py` | TC01 passes |
| **3. Process frames** | Resize to fixed width; overlay time, name, resolution, FPS | Phase 3 | `processing.py` | TC04, TC05 pass |
| **4. Capture + record** | `S` screenshots, `R` recording with REC status | Phases 4 & 5 | `media.py` | TC06, TC07 pass |
| **5. Harden, test, document** | Error handling, reconnect, safe shutdown, run all tests, write the report | Phase 6 + testing + report | `camera.py`, `main.py`, `TESTING.md`, `docs/` | TC02, TC03, TC08, TC09, TC10 pass; report answers all 20 technical questions |

**Suggested commit messages:** `Set up project, config and gitignore` → `Show live stream with Esc to quit` → `Add resize and overlays` → `Add screenshot and recording` → `Add error handling and reconnect` → `Add tests and report`.

## How the code fits together

```
main.py ──► config.py        (settings)
   │
   ├──► camera.py            (validate → check reachable → open → reconnect)
   ├──► processing.py        (resize → FPS → overlay)
   └──► media.py             (screenshot / Recorder)
```

Each frame goes through: **read → resize → overlay → (record) → add REC/message on a copy → show → check keys**.

Recordings and screenshots are saved *without* the temporary "REC" badge and confirmation message, because those are drawn on a copy used only for display.

## Bonus: Flask vs FastAPI for the browser dashboard

| | **Flask** | **FastAPI** |
|---|---|---|
| Learning curve | Very gentle, few concepts | Steeper (type hints, async, Pydantic) |
| Streaming video | Generator + `Response(...)` in ~5 lines | `StreamingResponse`, works but needs more care |
| Fit with OpenCV | `cap.read()` is **blocking**; Flask's threaded model suits that | Async is wasted on blocking code, so you need threads anyway |
| Extra setup | `pip install flask` | `pip install fastapi uvicorn` + an ASGI server |
| Strengths | Simple, huge number of MJPEG examples | Fast APIs, automatic docs, many concurrent clients |
| Overkill here? | No | Somewhat |

**Verdict: Flask.** This project is a single camera, a blocking OpenCV loop and one or two viewers. Flask is the shortest path to a working dashboard and is easy to explain in your report. FastAPI becomes the better choice only if you later need a proper REST API, many simultaneous users or async multi-camera handling (which also connects nicely to technical question D4).

Run it with `python src/web_app.py` and open `http://127.0.0.1:5000`. It binds to `127.0.0.1` so only your own computer can see the feed.

## Privacy and security
- Credentials live only in `.env` (git-ignored); `.env.example` has fake values.
- Use only cameras you own or have permission for, and tell anyone who may be recorded.
- Screenshots and recordings are git-ignored so they are never pushed.