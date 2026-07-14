import threading
import time
from dataclasses import dataclass

import numpy as np


@dataclass
class Frame:
    image: np.ndarray
    frame_id: int
    timestamp: float


class LatestFrameSlot:
    """Buffer de un solo slot: siempre entrega el frame más reciente.

    A diferencia de una cola FIFO, si el consumidor (inferencia) es más lento
    que el productor (cámara), los frames viejos se descartan en vez de
    acumularse. Para control en tiempo real nos importa la latencia del
    frame más nuevo, no procesar cada frame capturado.
    """

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._frame: Frame | None = None
        self._next_frame_id = 0
        self._dropped_frames = 0

    def put(self, image: np.ndarray) -> None:
        with self._condition:
            if self._frame is not None:
                self._dropped_frames += 1
            self._frame = Frame(
                image=image,
                frame_id=self._next_frame_id,
                timestamp=time.monotonic(),
            )
            self._next_frame_id += 1
            self._condition.notify_all()

    def get(self, timeout: float | None = None) -> Frame | None:
        """Bloquea hasta que haya un frame nuevo disponible y lo consume."""
        with self._condition:
            got_frame = self._condition.wait_for(
                lambda: self._frame is not None, timeout=timeout
            )
            if not got_frame:
                return None
            frame = self._frame
            self._frame = None
            return frame

    @property
    def dropped_frames(self) -> int:
        with self._condition:
            return self._dropped_frames
