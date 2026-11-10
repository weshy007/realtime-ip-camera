"""processing.py - resize, FPS estimate, overlay."""
import numpy as np
import pytest

import processing
from processing import FPSCounter, draw_overlay, put_text, resize_to_width


# ---------- frames are NumPy arrays (technical questions B7, C12) ----------
def test_a_720p_colour_frame_has_shape_720_1280_3():
    frame = np.zeros((720, 1280, 3), np.uint8)
    assert frame.shape == (720, 1280, 3)  # (height, width, channels)


# ---------- resize (TC05) ----------
def test_resize_1920x1080_to_width_960_gives_960x540():
    frame = np.zeros((1080, 1920, 3), np.uint8)
    assert resize_to_width(frame, 960).shape == (540, 960, 3)


@pytest.mark.parametrize("w,h,target", [(1280, 720, 640), (640, 480, 320), (1920, 1080, 1280), (640, 360, 960)])
def test_resize_keeps_aspect_ratio(w, h, target):
    resized = resize_to_width(np.zeros((h, w, 3), np.uint8), target)
    new_h, new_w = resized.shape[:2]
    assert new_w == target
    assert abs(new_w / new_h - w / h) < 0.02


def test_resize_keeps_three_colour_channels():
    assert resize_to_width(np.zeros((480, 640, 3), np.uint8), 320).shape[2] == 3


# ---------- FPS (technical question C11) ----------
@pytest.fixture
def fake_clock(monkeypatch):
    """Lets a test decide exactly how much time passes between frames."""
    clock = {"now": 1000.0}
    monkeypatch.setattr(processing.time, "time", lambda: clock["now"])
    return clock


def test_fps_is_about_20_when_frames_are_50ms_apart(fake_clock):
    counter = FPSCounter()
    for _ in range(30):
        fake_clock["now"] += 0.05
        fps = counter.tick()
    assert fps == pytest.approx(20.0, rel=0.01)


def test_fps_smoothing_softens_one_slow_frame(fake_clock):
    counter = FPSCounter()
    for _ in range(30):
        fake_clock["now"] += 0.05
        counter.tick()
    fake_clock["now"] += 0.5  # one very slow frame: raw FPS would be 2
    fps = counter.tick()
    assert 2.0 < fps < 20.0   # smoothed, not a sudden drop to 2
    assert fps == pytest.approx(18.2, abs=0.1)


def test_fps_does_not_crash_when_no_time_passes(fake_clock):
    counter = FPSCounter()
    assert counter.tick() == 0.0


# ---------- overlay (TC04) ----------
def test_put_text_draws_pixels():
    frame = np.zeros((100, 300, 3), np.uint8)
    put_text(frame, "Hello", (10, 50))
    assert frame.any()


def test_overlay_draws_in_the_top_right_and_leaves_top_left_alone():
    frame = np.zeros((540, 960, 3), np.uint8)
    draw_overlay(frame, "Office Camera", 22.6)
    assert frame[0:130, 700:960].any()          # our stats are top-right
    assert not frame[0:200, 0:300].any()        # top-left stays free for the phone app's text
    assert not frame[200:540, :].any()          # nothing drawn lower down


def test_overlay_shows_the_resolution_of_the_frame_it_is_given():
    small = np.zeros((180, 320, 3), np.uint8)
    large = np.zeros((540, 960, 3), np.uint8)
    draw_overlay(small, "Cam", 10)
    draw_overlay(large, "Cam", 10)
    assert small.any() and large.any()
    assert small.shape == (180, 320, 3) and large.shape == (540, 960, 3)  # size is never changed


def test_overlay_timestamp_changes_between_seconds(monkeypatch):
    from datetime import datetime as real_datetime

    class Clock:
        current = real_datetime(2026, 11, 9, 18, 26, 5)

        @classmethod
        def now(cls):
            return cls.current

    monkeypatch.setattr(processing, "datetime", Clock)
    first = np.zeros((200, 600, 3), np.uint8)
    draw_overlay(first, "Cam", 10)
    Clock.current = real_datetime(2026, 11, 9, 18, 26, 6)
    second = np.zeros((200, 600, 3), np.uint8)
    draw_overlay(second, "Cam", 10)
    assert not np.array_equal(first, second)
