import numpy as np

from src.gestures.gesture_definitions import (
    INDEX_FINGER_TIP,
    MIDDLE_FINGER_MCP,
    THUMB_TIP,
    WRIST,
    is_pinching,
    palm_size,
)


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
