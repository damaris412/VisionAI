import numpy as np

from src.gestures.gesture_definitions import (
    INDEX_FINGER_TIP,
    INDEX_MCP,
    MIDDLE_FINGER_MCP,
    MIDDLE_FINGER_TIP,
    PINKY_FINGER_TIP,
    PINKY_MCP,
    RING_FINGER_TIP,
    RING_MCP,
    THUMB_TIP,
    WRIST,
    is_hand_open,
    is_pinching,
    is_pointing,
    palm_size,
)

_LONG_FINGERS = (
    (INDEX_FINGER_TIP, INDEX_MCP),
    (MIDDLE_FINGER_TIP, MIDDLE_FINGER_MCP),
    (RING_FINGER_TIP, RING_MCP),
    (PINKY_FINGER_TIP, PINKY_MCP),
)

_CURLED_FINGERS = (
    (MIDDLE_FINGER_TIP, MIDDLE_FINGER_MCP),
    (RING_FINGER_TIP, RING_MCP),
    (PINKY_FINGER_TIP, PINKY_MCP),
)


def _set_extended(landmarks, tip, mcp):
    landmarks[mcp] = (0.5, 0.4, 0.0)
    landmarks[tip] = (0.5, 0.1, 0.0)


def _set_curled(landmarks, tip, mcp):
    landmarks[mcp] = (0.5, 0.4, 0.0)
    landmarks[tip] = (0.5, 0.45, 0.0)


def make_landmarks() -> np.ndarray:
    return np.zeros((21, 3), dtype=np.float32)


def test_palm_size_is_distance_between_wrist_and_middle_mcp():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.0, 0.0, 0.0)
    landmarks[MIDDLE_FINGER_MCP] = (0.0, 0.5, 0.0)

    assert palm_size(landmarks) == 0.5


def test_is_pinching_true_when_fingertips_are_close_relative_to_palm():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.0, 0.0, 0.0)
    landmarks[MIDDLE_FINGER_MCP] = (0.0, 0.5, 0.0)
    landmarks[THUMB_TIP] = (0.3, 0.3, 0.0)
    landmarks[INDEX_FINGER_TIP] = (0.31, 0.3, 0.0)

    assert is_pinching(landmarks) is True


def test_is_pinching_false_when_fingertips_are_far_apart():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.0, 0.0, 0.0)
    landmarks[MIDDLE_FINGER_MCP] = (0.0, 0.5, 0.0)
    landmarks[THUMB_TIP] = (0.0, 0.0, 0.0)
    landmarks[INDEX_FINGER_TIP] = (0.5, 0.0, 0.0)

    assert is_pinching(landmarks) is False


def test_is_pinching_false_when_palm_size_is_zero():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.0, 0.0, 0.0)
    landmarks[MIDDLE_FINGER_MCP] = (0.0, 0.0, 0.0)
    landmarks[THUMB_TIP] = (0.0, 0.0, 0.0)
    landmarks[INDEX_FINGER_TIP] = (0.0, 0.0, 0.0)

    assert is_pinching(landmarks) is False


def test_is_hand_open_true_when_all_four_fingers_extended():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    for tip, mcp in _LONG_FINGERS:
        landmarks[mcp] = (0.5, 0.4, 0.0)
        landmarks[tip] = (0.5, 0.1, 0.0)

    assert is_hand_open(landmarks) is True


def test_is_hand_open_false_when_fingers_are_curled():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    for tip, mcp in _LONG_FINGERS:
        landmarks[mcp] = (0.5, 0.4, 0.0)
        landmarks[tip] = (0.5, 0.45, 0.0)  # la punta queda más cerca de la muñeca que el nudillo

    assert is_hand_open(landmarks) is False


def test_is_hand_open_false_when_only_some_fingers_are_extended():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    for tip, mcp in _LONG_FINGERS:
        landmarks[mcp] = (0.5, 0.4, 0.0)
        landmarks[tip] = (0.5, 0.1, 0.0)
    # el meñique queda curvado
    landmarks[PINKY_FINGER_TIP] = (0.5, 0.45, 0.0)

    assert is_hand_open(landmarks) is False


def test_is_pointing_true_when_only_index_is_extended():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    _set_extended(landmarks, INDEX_FINGER_TIP, INDEX_MCP)
    for tip, mcp in _CURLED_FINGERS:
        _set_curled(landmarks, tip, mcp)

    assert is_pointing(landmarks) is True


def test_is_pointing_false_when_hand_is_fully_open():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    for tip, mcp in _LONG_FINGERS:
        _set_extended(landmarks, tip, mcp)

    assert is_pointing(landmarks) is False


def test_is_pointing_false_when_index_is_also_curled():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    _set_curled(landmarks, INDEX_FINGER_TIP, INDEX_MCP)
    for tip, mcp in _CURLED_FINGERS:
        _set_curled(landmarks, tip, mcp)

    assert is_pointing(landmarks) is False


def test_is_pointing_false_when_a_second_finger_stays_extended():
    landmarks = make_landmarks()
    landmarks[WRIST] = (0.5, 0.5, 0.0)
    _set_extended(landmarks, INDEX_FINGER_TIP, INDEX_MCP)
    _set_extended(landmarks, MIDDLE_FINGER_TIP, MIDDLE_FINGER_MCP)  # también extendido
    _set_curled(landmarks, RING_FINGER_TIP, RING_MCP)
    _set_curled(landmarks, PINKY_FINGER_TIP, PINKY_MCP)

    assert is_pointing(landmarks) is False
