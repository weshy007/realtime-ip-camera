"""web_app.py (bonus) - the Flask dashboard and its button routes, using a fake camera."""
import time

import pytest

import web
from helpers import FakeCapture, video_frame_count


@pytest.fixture
def dashboard(monkeypatch, settings):
    monkeypatch.setattr(web, "open_camera", lambda url: FakeCapture(delay=0.01))
    worker = web.CameraWorker()
    monkeypatch.setattr(web, "worker", worker)
    yield worker, web.app.test_client(), settings
    worker.running = False
    if worker.is_alive():
        worker.join(timeout=3)


def wait_for_video(worker):
    for _ in range(300):
        with worker.lock:
            if worker.jpeg:
                return
        time.sleep(0.01)
    pytest.fail("no video arrived")


def test_page_has_the_three_controls(dashboard):
    _, client, _ = dashboard
    page = client.get("/").get_data(as_text=True)
    assert "/video" in page
    for label in ("Screenshot", "recording", "Motion"):
        assert label in page


def test_buttons_say_so_when_there_is_no_video_yet(dashboard):
    _, client, _ = dashboard    # worker not started
    assert client.post("/screenshot").json["message"] == "No video yet"
    assert client.post("/record").json["message"] == "No video yet"


def test_screenshot_button_saves_an_image(dashboard):
    worker, client, settings = dashboard
    worker.start()
    wait_for_video(worker)
    assert client.post("/screenshot").json["message"].startswith("Saved")
    assert len(list((settings / "screenshots").glob("*.png"))) == 1


def test_record_button_starts_and_stops_a_playable_recording(dashboard):
    worker, client, settings = dashboard
    worker.start()
    wait_for_video(worker)
    assert client.post("/record").json["message"].startswith("Recording to")
    time.sleep(0.5)
    assert client.post("/record").json["message"] == "Recording saved"
    files = list((settings / "recordings").glob("*.mp4"))
    assert len(files) == 1 and video_frame_count(files[0]) > 5


def test_motion_button_toggles(dashboard):
    _, client, _ = dashboard
    assert client.post("/motion").json["message"] == "Motion detection on"
    assert client.post("/motion").json["message"] == "Motion detection off"


def test_video_route_streams_jpeg_frames(dashboard):
    worker, _, _ = dashboard
    worker.start()
    wait_for_video(worker)
    with web.app.test_request_context():
        response = web.video()
        assert response.mimetype == "multipart/x-mixed-replace"
        first_chunk = next(iter(response.response))
        response.response.close()
    assert first_chunk.startswith(b"--frame") and b"image/jpeg" in first_chunk


def test_a_recording_in_progress_is_saved_when_the_worker_stops(dashboard):
    worker, client, settings = dashboard
    worker.start()
    wait_for_video(worker)
    client.post("/record")
    time.sleep(0.3)
    worker.running = False
    worker.join(timeout=3)
    files = list((settings / "recordings").glob("*.mp4"))
    assert len(files) == 1 and video_frame_count(files[0]) > 3
