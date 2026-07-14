from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GestureState(Enum):
    IDLE = "idle"
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    COOLDOWN = "cooldown"


@dataclass
class StateMachineConfig:
    confirm_frames: int = 3
    cooldown_frames: int = 15


class GestureStateMachine:
    """Convierte una señal booleana ruidosa por frame en eventos discretos.

    Sin esto, un pellizco que tiembla entre "tocando" y "no tocando" entre
    frames dispararía decenas de clics por segundo en vez de uno solo.
    """

    def __init__(self, config: StateMachineConfig | None = None) -> None:
        self.config = config or StateMachineConfig()
        self.state = GestureState.IDLE
        self._frame_count = 0

    def update(self, active: bool) -> bool:
        """Alimenta la lectura de un frame. Devuelve True solo en el frame
        exacto en que el gesto pasa a CONFIRMED (el evento de disparo)."""
        fired = False

        if self.state == GestureState.IDLE:
            if active:
                self.state = GestureState.CANDIDATE
                self._frame_count = 1

        elif self.state == GestureState.CANDIDATE:
            if not active:
                self.state = GestureState.IDLE
                self._frame_count = 0
            else:
                self._frame_count += 1
                if self._frame_count >= self.config.confirm_frames:
                    self.state = GestureState.CONFIRMED
                    self._frame_count = 0
                    fired = True

        elif self.state == GestureState.CONFIRMED:
            # Estado transitorio de un solo frame: el evento ya se emitió;
            # pasamos a COOLDOWN para no volver a disparar mientras el
            # usuario sigue sosteniendo el gesto.
            self.state = GestureState.COOLDOWN
            self._frame_count = 0

        elif self.state == GestureState.COOLDOWN:
            # Requiere AMBAS condiciones (no solo el conteo de frames): si
            # solo exigiéramos el conteo, un pellizco sostenido más tiempo
            # que cooldown_frames volvería a IDLE y luego a CANDIDATE sin
            # soltar la mano, disparando un segundo clic con el gesto aún
            # activo. Exigir también `not active` fuerza a que el usuario
            # suelte el gesto para poder repetirlo.
            self._frame_count += 1
            if not active and self._frame_count >= self.config.cooldown_frames:
                self.state = GestureState.IDLE
                self._frame_count = 0

        return fired
