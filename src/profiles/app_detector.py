from __future__ import annotations

from pathlib import Path
from typing import Callable

import psutil
import win32gui
import win32process
import yaml

_MAPPING_PATH = Path(__file__).resolve().parents[2] / "config" / "app_profiles.yaml"
_DEFAULT_KEY = "default"


def get_foreground_process_name() -> str | None:
    """Nombre (en minúsculas) del ejecutable con foco, o None si no se pudo
    determinar (sin ventana activa, o el proceso ya cerró)."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def load_app_profile_mapping() -> dict[str, str]:
    with _MAPPING_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class AppProfileDetector:
    """Decide qué perfil cargar según la aplicación que tiene el foco.

    Consulta la ventana activa como mucho una vez cada `poll_interval_s` en
    vez de en cada frame: GetForegroundWindow + resolver el proceso es
    barato, pero no hay razón para hacerlo 30 veces por segundo si el
    usuario no cambia de ventana tan seguido.
    """

    def __init__(
        self,
        mapping: dict[str, str] | None = None,
        poll_interval_s: float = 1.0,
        process_name_provider: Callable[[], str | None] = get_foreground_process_name,
    ) -> None:
        self._mapping = mapping if mapping is not None else load_app_profile_mapping()
        self._poll_interval_s = poll_interval_s
        self._process_name_provider = process_name_provider
        self._last_poll = float("-inf")
        self._current_profile = self._mapping.get(_DEFAULT_KEY, "mouse")

    @property
    def current_profile(self) -> str:
        return self._current_profile

    def poll(self, now: float) -> str:
        """Devuelve el perfil vigente. Solo vuelve a consultar la ventana
        activa si ya pasó poll_interval_s desde la última consulta."""
        if now - self._last_poll < self._poll_interval_s:
            return self._current_profile

        self._last_poll = now
        process_name = self._process_name_provider()
        if process_name is not None:
            self._current_profile = self._mapping.get(process_name, self._mapping.get(_DEFAULT_KEY, "mouse"))
        return self._current_profile
