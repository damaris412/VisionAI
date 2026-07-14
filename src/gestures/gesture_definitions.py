from __future__ import annotations

import numpy as np

WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_MCP = 9
MIDDLE_FINGER_TIP = 12
RING_MCP = 13
RING_FINGER_TIP = 16
PINKY_MCP = 17
PINKY_FINGER_TIP = 20

PINCH_THRESHOLD_RATIO = 0.35

_LONG_FINGER_JOINTS = (
    (INDEX_FINGER_TIP, INDEX_MCP),
    (MIDDLE_FINGER_TIP, MIDDLE_FINGER_MCP),
    (RING_FINGER_TIP, RING_MCP),
    (PINKY_FINGER_TIP, PINKY_MCP),
)


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


def is_hand_open(landmarks: np.ndarray) -> bool:
    """True si índice, medio, anular y meñique están extendidos: la punta de
    cada uno queda más lejos de la muñeca que su nudillo (MCP). El pulgar no
    se evalúa, para que un pellizco con los demás dedos extendidos (p. ej.
    una seña de "OK") no cuente como mano abierta."""
    wrist = landmarks[WRIST]
    return all(
        _distance(landmarks[tip], wrist) > _distance(landmarks[mcp], wrist)
        for tip, mcp in _LONG_FINGER_JOINTS
    )
