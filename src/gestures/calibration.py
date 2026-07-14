from __future__ import annotations

import time
from dataclasses import dataclass

import cv2

from src.capture.camera_stream import CameraStream
from src.gestures.gesture_definitions import INDEX_FINGER_TIP
from src.vision.hand_tracker import HandTracker

_MIN_RANGE = 0.05


@dataclass(frozen=True)
class CalibrationResult:
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    def map_to_unit_square(self, x: float, y: float) -> tuple[float, float]:
        """Reescala (x, y) normalizados desde la zona cómoda calibrada a
        [0, 1], con clamping para que salirse de esa zona no mande el
        cursor fuera de pantalla."""
        span_x = max(self.max_x - self.min_x, 1e-6)
        span_y = max(self.max_y - self.min_y, 1e-6)
        unit_x = min(max((x - self.min_x) / span_x, 0.0), 1.0)
        unit_y = min(max((y - self.min_y) / span_y, 0.0), 1.0)
        return unit_x, unit_y


DEFAULT_CALIBRATION = CalibrationResult(min_x=0.2, max_x=0.8, min_y=0.2, max_y=0.8)


def run_calibration(
    camera: CameraStream,
    tracker: HandTracker,
    duration_s: float = 4.0,
    window_name: str = "VisionAI - Calibracion",
) -> CalibrationResult:
    """Guía al usuario a mover el índice por su zona cómoda de movimiento
    durante `duration_s` segundos y devuelve esos límites, para mapear esa
    zona (no el cuadro completo de la cámara) al área de la pantalla."""
    min_x, max_x = 1.0, 0.0
    min_y, max_y = 1.0, 0.0
    seen_any = False

    start = time.monotonic()
    while time.monotonic() - start < duration_s:
        frame = camera.read(timeout=1.0)
        if frame is None:
            continue

        image = cv2.flip(frame.image, 1)
        timestamp_ms = int((time.monotonic() - start) * 1000)
        hands = tracker.process(image, timestamp_ms)

        if hands:
            x, y = hands[0].landmarks[INDEX_FINGER_TIP][:2]
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            seen_any = True

        remaining = duration_s - (time.monotonic() - start)
        cv2.putText(
            image,
            f"Calibrando: mueve el indice por tu zona comoda ({remaining:.1f}s)",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        cv2.imshow(window_name, image)
        cv2.waitKey(1)

    cv2.destroyWindow(window_name)

    if not seen_any or (max_x - min_x) < _MIN_RANGE or (max_y - min_y) < _MIN_RANGE:
        return DEFAULT_CALIBRATION

    # Margen para no exigir que el usuario llegue justo al borde que tocó
    # durante la calibración para alcanzar el borde de la pantalla.
    margin_x = (max_x - min_x) * 0.1
    margin_y = (max_y - min_y) * 0.1
    return CalibrationResult(
        min_x=max(min_x - margin_x, 0.0),
        max_x=min(max_x + margin_x, 1.0),
        min_y=max(min_y - margin_y, 0.0),
        max_y=min(max_y + margin_y, 1.0),
    )
