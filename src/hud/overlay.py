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
    """Centra el texto y reduce el tamaño de fuente si hace falta, para que
    etiquetas largas (p. ej. "SIGUIENTE DIAPOSITIVA") no se salgan del cuadro
    como pasaría con un tamaño fijo pensado solo para "ACCION!"."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 4
    max_width = image.shape[1] - 40

    font_scale = 2.0
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    while text_w > max_width and font_scale > 0.5:
        font_scale -= 0.1
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    x = (image.shape[1] - text_w) // 2
    y = 60 + text_h
    cv2.putText(image, text, (x, y), font, font_scale, _RED, thickness)


def draw_cursor_target(image: np.ndarray, pixel: tuple[int, int]) -> None:
    cv2.circle(image, pixel, 10, _CYAN, 2)
    cv2.circle(image, pixel, 2, _CYAN, -1)
