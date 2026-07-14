import time

import numpy as np

import src.gestures.calibration as calibration_module
from src.gestures.calibration import run_calibration


class _Frame:
    def __init__(self, image):
        self.image = image


class _FakeCamera:
    def read(self, timeout=1.0):
        return _Frame(np.zeros((4, 4, 3), dtype=np.uint8))


class _RecordingTracker:
    def __init__(self):
        self.timestamps = []

    def process(self, image, timestamp_ms):
        self.timestamps.append(timestamp_ms)
        return []


def test_calibration_reuses_the_shared_start_time_instead_of_its_own_clock(monkeypatch):
    # Regresión: run_calibration solía medir sus propios timestamps desde un
    # `time.monotonic()` local. Como el HandLandmarker exige timestamps
    # estrictamente crecientes durante TODA su vida útil (no solo dentro de
    # esta función), el primer frame del loop principal -calculado desde un
    # start_time posterior- llegaba con un timestamp menor y MediaPipe
    # lanzaba "Input timestamp must be monotonically increasing", tumbando
    # el programa justo después de calibrar.
    monkeypatch.setattr(calibration_module.cv2, "imshow", lambda *a, **k: None)
    monkeypatch.setattr(calibration_module.cv2, "waitKey", lambda *a, **k: None)
    monkeypatch.setattr(calibration_module.cv2, "destroyWindow", lambda *a, **k: None)

    start_time = time.monotonic() - 10.0  # simula que el programa ya lleva 10s corriendo
    tracker = _RecordingTracker()

    run_calibration(_FakeCamera(), tracker, start_time, duration_s=0.05)

    assert tracker.timestamps
    assert all(ts >= 9500 for ts in tracker.timestamps)
    assert tracker.timestamps == sorted(tracker.timestamps)
