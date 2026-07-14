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

# PyAutoGUI aborta con una excepción si el cursor llega exactamente a una
# esquina de la pantalla (su mecanismo de "fail-safe" para que el usuario
# pueda recuperar el control moviendo el mouse real a una esquina). Este
# margen evita que el mapeo por gestos genere esa coordenada exacta, sin
# desactivar el fail-safe: el usuario siempre puede seguir usando su mouse
# físico para llegar a la esquina real y abortar.
_SCREEN_EDGE_MARGIN = 2


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

    def move_cursor(self, x: int, y: int) -> None:
        if self._dry_run:
            return
        screen_w, screen_h = pyautogui.size()
        safe_x = min(max(x, _SCREEN_EDGE_MARGIN), screen_w - _SCREEN_EDGE_MARGIN)
        safe_y = min(max(y, _SCREEN_EDGE_MARGIN), screen_h - _SCREEN_EDGE_MARGIN)
        pyautogui.moveTo(safe_x, safe_y, _pause=False)
