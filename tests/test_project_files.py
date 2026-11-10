"""Repository hygiene: no secrets in code, and .gitignore protects the right things."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_gitignore_protects_secrets_and_output():
    lines = (ROOT / ".gitignore").read_text().splitlines()
    assert ".env" in lines
    assert "screenshots/*" in lines
    assert "recordings/*" in lines


def test_env_example_exists_and_has_no_real_credentials():
    text = (ROOT / ".env.example").read_text()
    assert "CAMERA_URL" in text
    assert not re.search(r"://(?!username:password)[^/\s:@]+:[^/\s@]+@", text)


def test_source_code_contains_no_hard_coded_credentials():
    pattern = re.compile(r"://[^/\s\"'@]+:[^/\s\"'@]+@")        # scheme://user:pass@host
    for path in (ROOT / "src").glob("*.py"):
        assert not pattern.search(path.read_text()), f"credentials found in {path.name}"


def test_camera_url_is_read_from_the_environment_not_written_in_code():
    text = (ROOT / "src" / "config.py").read_text()
    assert 'config("CAMERA_URL"' in text


def test_required_documents_exist():
    for name in ("README.md", "TESTING.md", "requirements.txt"):
        assert (ROOT / name).is_file()
