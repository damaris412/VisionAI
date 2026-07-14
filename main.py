import time

import cv2

from src.capture.camera_stream import CameraStream
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_utils import draw_hand

WINDOW_NAME = "VisionAI - Paso 2: Deteccion de manos"

_HANDEDNESS_ES = {"Left": "Derecha", "Right": "Izquierda"}


def main() -> None:
    with (
        CameraStream(camera_index=0, width=1280, height=720, target_fps=30) as camera,
        HandTracker(max_num_hands=2) as tracker,
    ):
        start_time = time.monotonic()
        last_fps_update = start_time
        frames_since_update = 0
        display_fps = 0.0

        while True:
            frame = camera.read(timeout=2.0)
            if frame is None:
                print("No se recibieron frames de la cámara (timeout). Saliendo.")
                break

            # Espejamos primero para mostrar una vista "selfie" natural, y
            # detectamos sobre esa misma imagen espejada. MediaPipe estima
            # la lateralidad asumiendo una imagen sin espejar, así que el
            # resultado queda invertido respecto a la mano real del usuario;
            # _HANDEDNESS_ES compensa ese giro al traducir la etiqueta.
            image = cv2.flip(frame.image, 1)
            timestamp_ms = int((time.monotonic() - start_time) * 1000)
            hands = tracker.process(image, timestamp_ms)

            for hand in hands:
                draw_hand(image, hand.landmarks)
                wrist_x, wrist_y = (hand.landmarks[0][:2] * [image.shape[1], image.shape[0]]).astype(int)
                label = _HANDEDNESS_ES[hand.handedness]
                cv2.putText(
                    image,
                    f"{label} ({hand.score:.2f})",
                    (wrist_x - 30, wrist_y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 140, 255),
                    2,
                )

            frames_since_update += 1
            now = time.monotonic()
            if now - last_fps_update >= 0.5:
                display_fps = frames_since_update / (now - last_fps_update)
                frames_since_update = 0
                last_fps_update = now

            cv2.putText(
                image,
                f"FPS: {display_fps:.1f}  |  manos: {len(hands)}  |  descartados: {camera.dropped_frames}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow(WINDOW_NAME, image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
