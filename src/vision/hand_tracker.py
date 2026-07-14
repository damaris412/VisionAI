from __future__ import annotations

import urllib.request
from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "hand_landmarker.task"


def _ensure_model_downloaded() -> Path:
    if not _MODEL_PATH.exists():
        _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
    return _MODEL_PATH


@dataclass(frozen=True)
class Hand:
    landmarks: np.ndarray  # (21, 3) float32: x, y normalizados [0,1], z relativo a la muñeca
    handedness: str  # "Left" o "Right", tal como lo reporta MediaPipe
    score: float


class HandTracker:
    """Wrapper sobre MediaPipe HandLandmarker (Tasks API).

    El modelo entrenado se descarga automáticamente en el primer uso a
    ``models/`` (no se versiona en git: es un artefacto binario, igual que
    los pesos de cualquier modelo de ML).
    """

    def __init__(
        self,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.6,
    ) -> None:
        model_path = _ensure_model_downloaded()
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            running_mode=vision.RunningMode.VIDEO,
        )
        self._detector = vision.HandLandmarker.create_from_options(options)

    def process(self, image_bgr: np.ndarray, timestamp_ms: int) -> list[Hand]:
        # El modo VIDEO de la Tasks API exige timestamps estrictamente
        # crecientes entre llamadas; reusar o retroceder un timestamp lanza error.
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self._detector.detect_for_video(mp_image, timestamp_ms)

        hands: list[Hand] = []
        for landmarks, handedness in zip(result.hand_landmarks, result.handedness):
            points = np.array([(lm.x, lm.y, lm.z) for lm in landmarks], dtype=np.float32)
            category = handedness[0]
            hands.append(
                Hand(landmarks=points, handedness=category.category_name, score=category.score)
            )
        return hands

    def close(self) -> None:
        self._detector.close()

    def __enter__(self) -> HandTracker:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
