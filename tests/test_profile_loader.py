import pytest

from src.profiles.profile_loader import load_profile


def test_loads_mouse_profile():
    profile = load_profile("mouse")

    assert profile.name == "mouse"
    assert profile.action_for("pinch") == "mouse_click_left"


def test_loads_presentation_profile():
    profile = load_profile("presentation")

    assert profile.name == "presentation"
    assert profile.action_for("pinch") == "presentation_next_slide"


def test_loads_media_profile():
    profile = load_profile("media")

    assert profile.name == "media"
    assert profile.action_for("pinch") == "media_play_pause"


def test_action_for_unknown_gesture_returns_none():
    profile = load_profile("mouse")

    assert profile.action_for("swipe_left") is None


def test_missing_profile_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_profile("does_not_exist")
