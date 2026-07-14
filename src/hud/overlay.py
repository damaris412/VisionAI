from __future__ import annotations

import cv2
import numpy as np

_GREEN = (0, 255, 0)
_ORANGE = (0, 140, 255)
_RED = (0, 0, 255)
_CYAN = (255, 255, 0)


def draw_status_bar(image: np.ndarray, fps: float, profile_name: str, gesture_state: str, dropped_frames: int) -> None:
    cv2.putText(
        image,
        f"FPS: {fps:.1f}  |  perfil: {profile_name}  |  gesto: {gesture_state}  |  descartados: {dropped_frames}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        _GREEN,
        2,
    )


def draw_hand_label(image: np.ndarray, wrist_pixel: tuple[int, int], label: str, score: float) -> None:
    x, y = wrist_pixel
    cv2.putText(
        image,
        f"{label} ({score:.2f})",
        (x - 30, y + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        _ORANGE,
        2,
    )


def draw_action_flash(image: np.ndarray, text: str = "ACCION!") -> None:
    cv2.putText(
        image,
        text,
        (image.shape[1] // 2 - 120, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        2.0,
        _RED,
        4,
    )


def draw_cursor_target(image: np.ndarray, pixel: tuple[int, int]) -> None:
    cv2.circle(image, pixel, 10, _CYAN, 2)
    cv2.circle(image, pixel, 2, _CYAN, -1)
