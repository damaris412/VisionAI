import time

import cv2

from src.capture.camera_stream import CameraStream
from src.gestures.gesture_definitions import is_pinching
from src.gestures.gesture_state_machine import GestureStateMachine, StateMachineConfig
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_utils import draw_hand

WINDOW_NAME = "VisionAI - Paso 3: Gesto de pellizco"

_HANDEDNESS_ES = {"Left": "Derecha", "Right": "Izquierda"}
_CLICK_FLASH_FRAMES = 15


def main() -> None:
    with (
        CameraStream(camera_index=0, width=1280, height=720, target_fps=30) as camera,
        HandTracker(max_num_hands=1) as tracker,
    ):
        pinch_machine = GestureStateMachine(StateMachineConfig(confirm_frames=3, cooldown_frames=10))
        click_flash_remaining = 0

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
            hand = hands[0] if hands else None

            fired = pinch_machine.update(active=hand is not None and is_pinching(hand.landmarks))
            if fired:
                click_flash_remaining = _CLICK_FLASH_FRAMES
                print("CLIC (pellizco detectado)")

            if hand is not None:
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

            if click_flash_remaining > 0:
                cv2.putText(
                    image,
                    "CLIC!",
                    (image.shape[1] // 2 - 90, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2.0,
                    (0, 0, 255),
                    4,
                )
                click_flash_remaining -= 1

            frames_since_update += 1
            now = time.monotonic()
            if now - last_fps_update >= 0.5:
                display_fps = frames_since_update / (now - last_fps_update)
                frames_since_update = 0
                last_fps_update = now

            cv2.putText(
                image,
                f"FPS: {display_fps:.1f}  |  gesto: {pinch_machine.state.value}  |  descartados: {camera.dropped_frames}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.imshow(WINDOW_NAME, image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
