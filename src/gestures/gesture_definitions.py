from __future__ import annotations

import numpy as np

WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_MCP = 9

PINCH_THRESHOLD_RATIO = 0.35


def _distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a[:2] - b[:2]))


def palm_size(landmarks: np.ndarray) -> float:
    """Distancia muñeca -> nudillo del medio: referencia de escala de la mano
    que se usa para normalizar otras distancias, para que el umbral de
    pellizco no dependa de qué tan cerca está la mano de la cámara."""
    return _distance(landmarks[WRIST], landmarks[MIDDLE_FINGER_MCP])


def is_pinching(landmarks: np.ndarray, threshold_ratio: float = PINCH_THRESHOLD_RATIO) -> bool:
    scale = palm_size(landmarks)
    if scale == 0:
        return False
    pinch_distance = _distance(landmarks[THUMB_TIP], landmarks[INDEX_FINGER_TIP])
    return (pinch_distance / scale) < threshold_ratio
