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

_CURLED_FINGER_JOINTS = (
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


def is_pointing(landmarks: np.ndarray) -> bool:
    """True si el índice está extendido y los demás dedos largos (medio,
    anular, meñique) están curvados hacia la palma: la seña clásica de
    "apuntar" con el dedo, distinta de la mano abierta usada para el swipe."""
    wrist = landmarks[WRIST]
    index_extended = _distance(landmarks[INDEX_FINGER_TIP], wrist) > _distance(landmarks[INDEX_MCP], wrist)
    others_curled = all(
        _distance(landmarks[tip], wrist) < _distance(landmarks[mcp], wrist)
        for tip, mcp in _CURLED_FINGER_JOINTS
    )
    return index_extended and others_curled
