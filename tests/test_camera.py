"""camera.py - URL checking, reachability, opening and reconnecting."""
import pytest
import requests

import camera
from camera import CameraConnectionError
from helpers import FakeCapture


# ---------- validate_url (TC02) ----------
@pytest.mark.parametrize("url", [
    "http://192.168.1.23:8080/video",
    "https://camera.local/video",
    "rtsp://192.168.1.23:554/stream",
    "http://admin:admin@192.168.1.23:8081/video",
])
def test_validate_url_accepts_good_urls(url):
    camera.validate_url(url)  # must not raise


@pytest.mark.parametrize("url", ["", "htp://camera", "camera", "http://", "ftp://192.168.1.23/video"])
def test_validate_url_rejects_bad_urls(url):
    with pytest.raises(CameraConnectionError) as error:
        camera.validate_url(url)
    assert "Invalid camera URL" in str(error.value)


# ---------- check_reachable (TC03) ----------
class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.closed = False

    def close(self):
        self.closed = True


def test_check_reachable_ok_closes_the_connection(monkeypatch):
    response = FakeResponse(200)
    monkeypatch.setattr(camera.requests, "get", lambda *a, **k: response)
    camera.check_reachable("http://192.168.1.23:8080/video")
    assert response.closed


def test_check_reachable_uses_a_timeout_so_it_never_hangs(monkeypatch):
    seen = {}

    def fake_get(url, **kwargs):
        seen.update(kwargs)
        return FakeResponse(200)

    monkeypatch.setattr(camera.requests, "get", fake_get)
    camera.check_reachable("http://192.168.1.23:8080/video")
    assert seen["timeout"] == camera.config.CONNECTION_TIMEOUT


@pytest.mark.parametrize("problem", [
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout,
])
def test_check_reachable_camera_off_gives_clean_error(monkeypatch, problem):
    def fake_get(*a, **k):
        raise problem("boom")

    monkeypatch.setattr(camera.requests, "get", fake_get)
    with pytest.raises(CameraConnectionError) as error:
        camera.check_reachable("http://192.168.1.99:8080/video")
    assert "Cannot reach the camera" in str(error.value)


@pytest.mark.parametrize("status", [401, 403])
def test_check_reachable_login_refused(monkeypatch, status):
    monkeypatch.setattr(camera.requests, "get", lambda *a, **k: FakeResponse(status))
    with pytest.raises(CameraConnectionError) as error:
        camera.check_reachable("http://192.168.1.23:8080/video")
    assert "login" in str(error.value)


def test_check_reachable_http_error_status(monkeypatch):
    monkeypatch.setattr(camera.requests, "get", lambda *a, **k: FakeResponse(404))
    with pytest.raises(CameraConnectionError) as error:
        camera.check_reachable("http://192.168.1.23:8080/wrong")
    assert "HTTP 404" in str(error.value)


def test_check_reachable_skips_http_check_for_rtsp(monkeypatch):
    def must_not_be_called(*a, **k):
        raise AssertionError("requests.get should not be used for rtsp")

    monkeypatch.setattr(camera.requests, "get", must_not_be_called)
    camera.check_reachable("rtsp://192.168.1.23:554/stream")


# ---------- open_camera ----------
def test_open_camera_returns_capture_when_open(monkeypatch):
    fake = FakeCapture()
    monkeypatch.setattr(camera.cv2, "VideoCapture", lambda url: fake)
    assert camera.open_stream("http://x/video") is fake


def test_open_camera_raises_and_releases_when_it_cannot_open(monkeypatch):
    fake = FakeCapture()
    fake.released = True  # isOpened() is False
    fake.release = lambda: setattr(fake, "released_called", True)
    monkeypatch.setattr(camera.cv2, "VideoCapture", lambda url: fake)
    with pytest.raises(CameraConnectionError):
        camera.open_stream("http://x/video")
    assert fake.released_called


# ---------- reconnect (TC08) ----------
@pytest.fixture
def no_waiting(monkeypatch):
    monkeypatch.setattr(camera.time, "sleep", lambda s: None)
    monkeypatch.setattr(camera.config, "MAX_RECONNECTS", 3)


def test_reconnect_releases_old_capture_and_returns_new_one(monkeypatch, no_waiting):
    old, new = FakeCapture(), FakeCapture()
    monkeypatch.setattr(camera, "check_reachable", lambda url: None)
    monkeypatch.setattr(camera, "open_camera", lambda url: new)
    assert camera.reconnect(old, "http://x/video") is new
    assert old.released


def test_reconnect_recovers_on_a_later_attempt(monkeypatch, no_waiting):
    attempts = {"n": 0}

    def flaky_check(url):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise CameraConnectionError("still down")

    new = FakeCapture()
    monkeypatch.setattr(camera, "check_reachable", flaky_check)
    monkeypatch.setattr(camera, "open_camera", lambda url: new)
    assert camera.reconnect(FakeCapture(), "http://x/video") is new
    assert attempts["n"] == 3


def test_reconnect_gives_up_after_the_limit(monkeypatch, no_waiting, capsys):
    attempts = {"n": 0}

    def always_down(url):
        attempts["n"] += 1
        raise CameraConnectionError("down")

    monkeypatch.setattr(camera, "check_reachable", always_down)
    with pytest.raises(CameraConnectionError) as error:
        camera.reconnect(FakeCapture(), "http://x/video")
    assert attempts["n"] == 3  # exactly MAX_RECONNECTS, not forever
    assert "Giving up" in str(error.value)
    assert "Reconnecting (1/3)" in capsys.readouterr().out
