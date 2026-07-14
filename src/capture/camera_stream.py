from __future__ import annotations

import sys
import threading
from types import TracebackType

import cv2

from src.capture.frame_queue import Frame, LatestFrameSlot

_CAPTURE_BACKEND = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY


class CameraStream:
    """Lee frames de la cámara en un hilo dedicado.

    Mantener la lectura de cv2.VideoCapture en su propio hilo evita que el
    tiempo de inferencia (MediaPipe) bloquee la captura: la cámara sigue
    entregando frames a su propio ritmo aunque el consumidor vaya más lento,
    y el consumidor siempre recibe el frame más reciente vía LatestFrameSlot.
    """

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
        target_fps: int = 30,
    ) -> None:
        self._camera_index = camera_index
        self._width = width
        self._height = height
        self._target_fps = target_fps

        self._capture: cv2.VideoCapture | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._slot = LatestFrameSlot()

    def start(self) -> CameraStream:
        self._capture = cv2.VideoCapture(self._camera_index, _CAPTURE_BACKEND)
        if not self._capture.isOpened():
            raise RuntimeError(
                f"No se pudo abrir la cámara con índice {self._camera_index}. "
                "Verifica que esté conectada y no esté en uso por otra aplicación."
            )

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._capture.set(cv2.CAP_PROP_FPS, self._target_fps)

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        return self

    def _capture_loop(self) -> None:
        assert self._capture is not None
        while not self._stop_event.is_set():
            ok, image = self._capture.read()
            if not ok:
                continue
            self._slot.put(image)

    def read(self, timeout: float = 1.0) -> Frame | None:
        """Devuelve el frame más reciente disponible, o None si hubo timeout."""
        return self._slot.get(timeout=timeout)

    @property
    def dropped_frames(self) -> int:
        return self._slot.dropped_frames

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._capture is not None:
            self._capture.release()

    def __enter__(self) -> CameraStream:
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.stop()
