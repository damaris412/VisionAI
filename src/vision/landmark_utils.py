from __future__ import annotations

import cv2
import numpy as np
from mediapipe.tasks.python.vision import HandLandmarksConnections

HAND_CONNECTIONS: list[tuple[int, int]] = [
    (c.start, c.end) for c in HandLandmarksConnections.HAND_CONNECTIONS
]


def denormalize(landmarks: np.ndarray, image_width: int, image_height: int) -> np.ndarray:
    """Convierte landmarks normalizados [0,1] a coordenadas de píxel (x, y) enteras."""
    pixel_points = landmarks[:, :2].copy()
    pixel_points[:, 0] *= image_width
    pixel_points[:, 1] *= image_height
    return pixel_points.astype(np.int32)


def draw_hand(
    image_bgr: np.ndarray,
    landmarks: np.ndarray,
    color: tuple[int, int, int] = (0, 200, 0),
) -> None:
    """Dibuja los 21 puntos y sus conexiones sobre el frame, in-place."""
    height, width = image_bgr.shape[:2]
    points = denormalize(landmarks, width, height)

    for start_idx, end_idx in HAND_CONNECTIONS:
        start = (int(points[start_idx][0]), int(points[start_idx][1]))
        end = (int(points[end_idx][0]), int(points[end_idx][1]))
        cv2.line(image_bgr, start, end, (255, 255, 255), 2)

    for x, y in points:
        cv2.circle(image_bgr, (int(x), int(y)), 4, color, -1)
