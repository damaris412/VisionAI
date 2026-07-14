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
