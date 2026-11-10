"""main.py - the whole loop, driven by a fake camera and fake key presses.

Key script: {frame_number: key}. A key is pressed right after that frame is shown.
Use ord("r") etc. for letters, 27 for Esc and "CTRL_C" to simulate Ctrl+C.
"""
import requests
import pytest

import camera
import config
import main
from camera import CameraConnectionError
from helpers import FakeCapture, moving_frame, static_frame, video_frame_count


@pytest.fixture
def run_main(monkeypatch, settings):
    def _run(cap, keys=None):
        script = dict(keys or {})
        script.setdefault(400, 27)               # safety net: never loop forever
        shown = {"n": 0}
        windows = {"destroyed": 0}

        def fake_imshow(name, image):
            shown["n"] += 1

        def fake_wait_key(ms):
            action = script.get(shown["n"], 255)  # 255 = no key
            if action == "CTRL_C":
                raise KeyboardInterrupt
            return action

        monkeypatch.setattr(main, "check_reachable", lambda url: None)
        monkeypatch.setattr(main, "open_camera", lambda url: cap)
        monkeypatch.setattr(main.cv2, "imshow", fake_imshow)
        monkeypatch.setattr(main.cv2, "waitKey", fake_wait_key)
        monkeypatch.setattr(main.cv2, "destroyAllWindows",
                            lambda: windows.update(destroyed=windows["destroyed"] + 1))
        code = main.main()
        return code, shown["n"], windows["destroyed"]

    return _run


def recordings(settings):
    return sorted((settings / "recordings").glob("*.mp4"))


# ---------- TC02 / TC03: start-up errors ----------
def test_tc02_invalid_url_prints_a_clear_error_and_exits(monkeypatch, settings, capsys):
    monkeypatch.setattr(config, "CAMERA_URL", "htp://camera")
    assert main.main() == 1
    output = capsys.readouterr()
    assert "Invalid camera URL" in output.out
    assert "Traceback" not in output.out + output.err


def test_tc03_camera_unavailable_reports_and_exits(monkeypatch, settings, capsys):
    def no_answer(*a, **k):
        raise requests.exceptions.ConnectTimeout("no answer")

    monkeypatch.setattr(camera.requests, "get", no_answer)
    monkeypatch.setattr(main, "open_camera",
                        lambda url: pytest.fail("must not open the stream if the camera did not answer"))
    assert main.main() == 1
    output = capsys.readouterr()
    assert "Cannot reach the camera" in output.out
    assert "Traceback" not in output.out + output.err


# ---------- TC01: normal run + Esc ----------
def test_tc01_frames_are_shown_and_esc_shuts_down_cleanly(run_main):
    cap = FakeCapture()
    code, shown, destroyed = run_main(cap, {5: 27})
    assert code == 0
    assert shown == 5
    assert cap.released
    assert destroyed == 1


# ---------- TC06: screenshots ----------
def test_tc06_s_key_saves_separate_screenshots(run_main, settings):
    cap = FakeCapture(delay=0.01)
    run_main(cap, {3: ord("s"), 8: ord("S"), 10: 27})
    shots = list((settings / "screenshots").glob("*.png"))
    assert len(shots) == 2


# ---------- TC07: recording ----------
def test_tc07_r_starts_and_stops_a_playable_recording(run_main, settings):
    cap = FakeCapture(delay=0.02)
    run_main(cap, {3: ord("r"), 30: ord("r"), 35: 27})
    files = recordings(settings)
    assert len(files) == 1
    assert 20 <= video_frame_count(files[0]) <= 30   # about the 27 frames shown in between


# ---------- TC09 / TC10: shutdown while recording ----------
def test_tc09_esc_during_recording_saves_the_file(run_main, settings):
    cap = FakeCapture(delay=0.01)
    code, _, destroyed = run_main(cap, {3: ord("r"), 20: 27})
    files = recordings(settings)
    assert code == 0 and cap.released and destroyed == 1
    assert len(files) == 1 and video_frame_count(files[0]) > 10


def test_tc10_ctrl_c_during_recording_has_no_traceback_and_saves_the_file(run_main, settings):
    cap = FakeCapture(delay=0.01)
    code, _, destroyed = run_main(cap, {3: ord("r"), 20: "CTRL_C"})   # would raise if not handled
    files = recordings(settings)
    assert code == 0 and cap.released and destroyed == 1
    assert len(files) == 1 and video_frame_count(files[0]) > 10


# ---------- TC08: dropped connection ----------
def test_tc08_a_failed_read_triggers_a_reconnect_and_streaming_continues(run_main, monkeypatch):
    cap = FakeCapture(fail_at={5})
    calls = []

    def fake_reconnect(old, url):
        calls.append(url)
        return old

    monkeypatch.setattr(main, "reconnect", fake_reconnect)
    code, shown, _ = run_main(cap, {12: 27})
    assert code == 0
    assert len(calls) == 1
    assert shown == 12   # kept going after the drop


def test_tc08_recovers_when_the_camera_comes_back(run_main, monkeypatch):
    broken = FakeCapture(fail_from=5)
    healthy = FakeCapture()
    monkeypatch.setattr(camera, "check_reachable", lambda url: None)
    monkeypatch.setattr(camera, "open_camera", lambda url: healthy)
    code, shown, _ = run_main(broken, {15: 27})
    assert code == 0
    assert broken.released          # the dead connection was thrown away
    assert healthy.n > 0            # frames now come from the new connection
    assert healthy.released         # and it is released at the end too


def test_tc08_gives_up_after_the_retry_limit_and_exits_cleanly(run_main, monkeypatch, capsys):
    cap = FakeCapture(fail_from=5)
    attempts = {"n": 0}

    def still_down(url):
        attempts["n"] += 1
        raise CameraConnectionError("down")

    monkeypatch.setattr(camera, "check_reachable", still_down)
    code, _, destroyed = run_main(cap)
    output = capsys.readouterr()
    assert code == 1
    assert attempts["n"] == config.MAX_RECONNECTS
    assert "Giving up" in output.out
    assert "Traceback" not in output.out + output.err
    assert cap.released and destroyed == 1


def test_tc08_a_recording_in_progress_is_saved_when_the_connection_is_lost(run_main, monkeypatch, settings):
    cap = FakeCapture(fail_from=20, delay=0.005)
    monkeypatch.setattr(camera, "check_reachable", lambda url: (_ for _ in ()).throw(CameraConnectionError("down")))
    code, _, _ = run_main(cap, {3: ord("r")})
    files = recordings(settings)
    assert code == 1
    assert len(files) == 1 and video_frame_count(files[0]) > 5


# ---------- Bonus: motion + auto-record ----------
def test_auto_record_starts_on_motion_and_stops_after_the_quiet_period(run_main, settings):
    def scene(n):
        return moving_frame(n) if n <= 30 else static_frame(n)   # movement, then stillness

    cap = FakeCapture(frame_fn=scene, delay=0.02)
    run_main(cap, {2: ord("a"), 150: 27})   # ~3 s in total, quiet period is 1 s
    files = recordings(settings)
    assert len(files) == 1
    frames = video_frame_count(files[0])
    assert 20 < frames < 130                # it recorded the movement but stopped long before the end


def test_no_motion_means_no_auto_recording(run_main, settings):
    cap = FakeCapture(delay=0.005)
    run_main(cap, {2: ord("a"), 60: 27})
    assert recordings(settings) == []


def test_a_manual_recording_is_not_stopped_by_the_quiet_period(run_main, settings):
    cap = FakeCapture(delay=0.02)           # nothing ever moves
    run_main(cap, {3: ord("r"), 5: ord("a"), 130: 27})   # > 2 s, quiet period is 1 s
    files = recordings(settings)
    assert len(files) == 1
    assert video_frame_count(files[0]) >= 100
