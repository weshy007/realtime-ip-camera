"""config.py - settings parsing."""
import config as app_config


def test_parse_box_valid():
    assert app_config._parse_box("0,0,320,200") == (0, 0, 320, 200)


def test_parse_box_with_spaces():
    assert app_config._parse_box("10, 20, 30, 40") == (10, 20, 30, 40)


def test_parse_box_empty_means_ignore_nothing():
    assert app_config._parse_box("") is None


def test_parse_box_wrong_count_or_text():
    assert app_config._parse_box("1,2,3") is None
    assert app_config._parse_box("a,b,c,d") is None


def test_default_settings_have_sensible_types():
    assert isinstance(app_config.DISPLAY_WIDTH, int) and app_config.DISPLAY_WIDTH > 0
    assert isinstance(app_config.MAX_RECONNECTS, int) and app_config.MAX_RECONNECTS > 0
    assert app_config.CONNECTION_TIMEOUT > 0
