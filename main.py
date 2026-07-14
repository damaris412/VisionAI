import argparse
import time

import cv2

from src.actions.controller import ActionController
from src.capture.camera_stream import CameraStream
from src.gestures.gesture_definitions import is_pinching
from src.gestures.gesture_state_machine import GestureStateMachine, StateMachineConfig
from src.profiles.app_detector import AppProfileDetector
from src.profiles.profile_loader import load_profile
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_utils import draw_hand

_HANDEDNESS_ES = {"Left": "Derecha", "Right": "Izquierda"}
_ACTION_FLASH_FRAMES = 15


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VisionAI - control por gestos")
    parser.add_argument(
        "--profile",
        default=None,
        help=(
            "Fuerza un perfil especifico (mouse, presentation, media) y "
            "desactiva la deteccion automatica por aplicacion activa"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Imprime las acciones en vez de ejecutarlas (útil para probar sin disparar clics/teclas reales)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    controller = ActionController(dry_run=args.dry_run)

    auto_detect = args.profile is None
    detector = AppProfileDetector() if auto_detect else None
    profile = load_profile(detector.poll(time.monotonic()) if detector else args.profile)

    window_name = (
        "VisionAI - Deteccion automatica de perfil" if auto_detect else f"VisionAI - Perfil: {profile.name}"
    )
    if args.dry_run:
        window_name += " [dry-run]"

    with (
        CameraStream(camera_index=0, width=1280, height=720, target_fps=30) as camera,
        HandTracker(max_num_hands=1) as tracker,
    ):
        pinch_machine = GestureStateMachine(StateMachineConfig(confirm_frames=3, cooldown_frames=10))
        action_flash_remaining = 0

        start_time = time.monotonic()
        last_fps_update = start_time
        frames_since_update = 0
        display_fps = 0.0

        while True:
            frame = camera.read(timeout=2.0)
            if frame is None:
                print("No se recibieron frames de la cámara (timeout). Saliendo.")
                break

            if detector is not None:
                desired_profile_name = detector.poll(time.monotonic())
                if desired_profile_name != profile.name:
                    profile = load_profile(desired_profile_name)
                    print(f"Cambio automático de perfil -> {profile.name}")

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
                action_name = profile.action_for("pinch")
                if action_name:
                    controller.execute(action_name)
                    prefix = "[dry-run] " if args.dry_run else ""
                    print(f"{prefix}[{profile.name}] pellizco -> {action_name}")
                action_flash_remaining = _ACTION_FLASH_FRAMES

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

            if action_flash_remaining > 0:
                cv2.putText(
                    image,
                    "ACCION!",
                    (image.shape[1] // 2 - 120, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2.0,
                    (0, 0, 255),
                    4,
                )
                action_flash_remaining -= 1

            frames_since_update += 1
            now = time.monotonic()
            if now - last_fps_update >= 0.5:
                display_fps = frames_since_update / (now - last_fps_update)
                frames_since_update = 0
                last_fps_update = now

            cv2.putText(
                image,
                f"FPS: {display_fps:.1f}  |  perfil: {profile.name}  |  gesto: {pinch_machine.state.value}  |  descartados: {camera.dropped_frames}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
            cv2.imshow(window_name, image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
