"""Shared pytest setup: lets tests import from src/ and keeps them away from your real .env."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
# Set BEFORE config is imported, so a real .env file can never leak into the tests
os.environ["CAMERA_URL"] = "http://192.168.1.23:8080/video"

import config as app_config  # noqa: E402


@pytest.fixture
def settings(monkeypatch, tmp_path):
    """Test-friendly settings: small frames, output into a temp folder, short waits."""
    monkeypatch.setattr(app_config, "CAMERA_URL", "http://192.168.1.23:8080/video")
    monkeypatch.setattr(app_config, "CAMERA_NAME", "Test Cam")
    monkeypatch.setattr(app_config, "DISPLAY_WIDTH", 320)
    monkeypatch.setattr(app_config, "SCREENSHOT_DIR", str(tmp_path / "screenshots"))
    monkeypatch.setattr(app_config, "RECORDING_DIR", str(tmp_path / "recordings"))
    monkeypatch.setattr(app_config, "MOTION_IGNORE", None)
    monkeypatch.setattr(app_config, "QUIET_SECONDS", 1)
    monkeypatch.setattr(app_config, "MAX_RECONNECTS", 2)
    monkeypatch.setattr(app_config, "RECONNECT_DELAY", 0)
    return tmp_path
