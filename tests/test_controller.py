import pytest

import src.actions.controller as controller_module
from src.actions.controller import ActionController


def test_execute_calls_the_mapped_pyautogui_action(monkeypatch):
    calls = []
    monkeypatch.setitem(controller_module._ACTIONS, "mouse_click_left", lambda: calls.append("clicked"))

    ActionController().execute("mouse_click_left")

    assert calls == ["clicked"]


def test_dry_run_does_not_execute_the_action(monkeypatch):
    calls = []
    monkeypatch.setitem(controller_module._ACTIONS, "mouse_click_left", lambda: calls.append("clicked"))

    ActionController(dry_run=True).execute("mouse_click_left")

    assert calls == []


def test_unknown_action_raises_value_error():
    with pytest.raises(ValueError):
        ActionController().execute("does_not_exist")


def test_move_cursor_calls_pyautogui_move_to(monkeypatch):
    calls = []
    monkeypatch.setattr(controller_module.pyautogui, "size", lambda: (1920, 1080))
    monkeypatch.setattr(
        controller_module.pyautogui, "moveTo", lambda x, y, _pause=True: calls.append((x, y))
    )

    ActionController().move_cursor(500, 300)

    assert calls == [(500, 300)]


def test_move_cursor_dry_run_does_not_move(monkeypatch):
    calls = []
    monkeypatch.setattr(controller_module.pyautogui, "size", lambda: (1920, 1080))
    monkeypatch.setattr(
        controller_module.pyautogui, "moveTo", lambda x, y, _pause=True: calls.append((x, y))
    )

    ActionController(dry_run=True).move_cursor(500, 300)

    assert calls == []


def test_move_cursor_clamps_away_from_screen_corners(monkeypatch):
    calls = []
    monkeypatch.setattr(controller_module.pyautogui, "size", lambda: (1920, 1080))
    monkeypatch.setattr(
        controller_module.pyautogui, "moveTo", lambda x, y, _pause=True: calls.append((x, y))
    )

    ActionController().move_cursor(0, 0)
    ActionController().move_cursor(1920, 1080)

    assert calls == [(2, 2), (1918, 1078)]
