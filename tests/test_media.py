"""media.py - screenshots and recordings."""
import re
import time

import cv2
import numpy as np
import pytest

import media
from helpers import video_frame_count


def frame(width=320, height=180, value=120):
    return np.full((height, width, 3), value, np.uint8)


# ---------- file names (technical question C15) ----------
def test_timestamp_format_includes_milliseconds():
    assert re.fullmatch(r"\d{8}_\d{6}_\d{3}", media.timestamp())


def test_timestamps_differ_over_time():
    first = media.timestamp()
    time.sleep(0.01)
    assert media.timestamp() != first


# ---------- FPS declared for a recording ----------
@pytest.mark.parametrize("measured,expected", [
    (0.0, 20.0), (3.2, 20.0),       # too low or not measured yet -> 20
    (5.0, 5.0), (22.6, 23.0),       # normal values are rounded
    (96.391, 60.0), (5000.0, 60.0),  # startup spikes are capped (these broke the mp4 codec)
])
def test_safe_fps(measured, expected):
    assert media.safe_fps(measured) == expected


def test_recorder_accepts_a_startup_spike_in_measured_fps(tmp_path):
    recorder = media.Recorder(str(tmp_path))
    path = recorder.start(frame(), media.safe_fps(96.391))
    recorder.write(frame())
    recorder.stop()
    assert video_frame_count(path) == 1


# ---------- screenshots (TC06) ----------
def test_screenshot_creates_missing_folder_and_file(tmp_path):
    folder = tmp_path / "does" / "not" / "exist"
    path = media.save_screenshot(frame(), str(folder))
    assert folder.is_dir()
    assert path.endswith(".png") and "screenshot_" in path
    assert cv2.imread(path).shape == (180, 320, 3)


def test_two_screenshots_are_two_separate_files(tmp_path):
    first = media.save_screenshot(frame(), str(tmp_path))
    time.sleep(0.01)
    second = media.save_screenshot(frame(), str(tmp_path))
    assert first != second
    assert len(list(tmp_path.glob("*.png"))) == 2


def test_screenshot_is_saved_without_loss(tmp_path):
    original = np.random.randint(0, 255, (180, 320, 3), dtype=np.uint8)
    path = media.save_screenshot(original, str(tmp_path))
    assert np.array_equal(cv2.imread(path), original)  # PNG is lossless


# ---------- recorder (TC07) ----------
def test_recorder_starts_not_recording(tmp_path):
    recorder = media.Recorder(str(tmp_path))
    assert not recorder.is_recording
    assert recorder.elapsed() == 0


def test_recording_creates_a_playable_timestamped_mp4(tmp_path):
    recorder = media.Recorder(str(tmp_path / "recordings"))
    path = recorder.start(frame(), 20.0)
    assert recorder.is_recording
    for _ in range(20):
        recorder.write(frame())
    recorder.stop()
    assert not recorder.is_recording
    assert path.endswith(".mp4") and "recording_" in path
    assert video_frame_count(path) == 20


def test_recorder_elapsed_time_counts_up(tmp_path):
    recorder = media.Recorder(str(tmp_path))
    recorder.start(frame(), 20.0)
    time.sleep(1.1)
    assert recorder.elapsed() >= 1
    recorder.stop()
    assert recorder.elapsed() == 0


def test_recorder_resizes_frames_of_the_wrong_size(tmp_path):
    """A frame of a different size than declared would silently break the video (question C13)."""
    recorder = media.Recorder(str(tmp_path))
    path = recorder.start(frame(320, 180), 20.0)
    for _ in range(5):
        recorder.write(frame(320, 180))
    for _ in range(5):
        recorder.write(frame(640, 360))   # wrong size
    recorder.stop()
    assert video_frame_count(path) == 10  # none of them were dropped


def test_stopping_twice_or_writing_without_start_is_safe(tmp_path):
    recorder = media.Recorder(str(tmp_path))
    recorder.write(frame())  # nothing happens, no error
    recorder.stop()
    recorder.start(frame(), 20.0)
    recorder.stop()
    recorder.stop()


def test_two_recordings_never_overwrite_each_other(tmp_path):
    recorder = media.Recorder(str(tmp_path))
    first = recorder.start(frame(), 20.0)
    recorder.write(frame())
    recorder.stop()
    time.sleep(0.01)
    second = recorder.start(frame(), 20.0)
    recorder.write(frame())
    recorder.stop()
    assert first != second
    assert len(list(tmp_path.glob("*.mp4"))) == 2


def test_recorder_reports_a_failed_start_cleanly(tmp_path, monkeypatch):
    class BrokenWriter:
        def __init__(self, *a, **k):
            pass

        def isOpened(self):
            return False

    monkeypatch.setattr(media.cv2, "VideoWriter", BrokenWriter)
    recorder = media.Recorder(str(tmp_path))
    with pytest.raises(RuntimeError):
        recorder.start(frame(), 20.0)
    assert not recorder.is_recording
