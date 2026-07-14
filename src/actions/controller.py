from __future__ import annotations

from typing import Callable

import pyautogui

_ACTIONS: dict[str, Callable[[], None]] = {
    "mouse_click_left": lambda: pyautogui.click(button="left"),
    "mouse_click_right": lambda: pyautogui.click(button="right"),
    "presentation_next_slide": lambda: pyautogui.press("right"),
    "presentation_previous_slide": lambda: pyautogui.press("left"),
    "media_play_pause": lambda: pyautogui.press("playpause"),
}


class ActionController:
    """Ejecuta acciones del sistema operativo a partir de un nombre lógico.

    Desacopla el nombre de acción usado en los perfiles YAML de la llamada
    real a pyautogui, para que los perfiles no dependan de qué librería de
    automatización se use por debajo.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self._dry_run = dry_run

    def execute(self, action_name: str) -> None:
        if action_name not in _ACTIONS:
            raise ValueError(f"Acción desconocida: '{action_name}'")
        if self._dry_run:
            return
        _ACTIONS[action_name]()
