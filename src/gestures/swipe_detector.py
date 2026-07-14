from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class SwipeConfig:
    # Pensado para uso "de pie, a distancia" (presentando frente a un
    # proyector) en vez de sentado frente a la cámara: a mayor distancia de
    # la cámara, el mismo movimiento de la mano cubre una fracción menor del
    # cuadro, así que el umbral es más permisivo que un valor calibrado para
    # uso de escritorio.
    window_frames: int = 10
    min_displacement: float = 0.15
    cooldown_frames: int = 20


class SwipeDetector:
    """Detecta un swipe horizontal: la mano abierta se desplaza de un lado
    al otro del cuadro dentro de una ventana corta de frames.

    A diferencia de GestureStateMachine (que evalúa una señal booleana
    estática por frame, como el pellizco), un swipe es un patrón de
    movimiento: hace falta la posición X de varios frames recientes para
    saber si hubo desplazamiento neto suficiente y en qué dirección.
    """

    def __init__(self, config: SwipeConfig | None = None) -> None:
        self.config = config or SwipeConfig()
        self._positions: deque[float] = deque(maxlen=self.config.window_frames)
        self._cooldown_remaining = 0

    def update(self, hand_open: bool, x: float | None) -> str | None:
        """Alimenta la posición X normalizada de la mano en este frame (o
        None si no hay mano o no está abierta). Devuelve "left", "right" o
        None."""
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= 1
            self._positions.clear()
            return None

        if not hand_open or x is None:
            self._positions.clear()
            return None

        self._positions.append(x)
        if len(self._positions) < self.config.window_frames:
            return None

        displacement = self._positions[-1] - self._positions[0]
        if abs(displacement) < self.config.min_displacement:
            return None

        self._cooldown_remaining = self.config.cooldown_frames
        self._positions.clear()
        return "right" if displacement > 0 else "left"
