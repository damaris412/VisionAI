import argparse
import time

import cv2
import pyautogui

from src.actions.controller import ActionController
from src.actions.cursor_smoother import CursorSmoother
from src.capture.camera_stream import CameraStream
from src.gestures.calibration import DEFAULT_CALIBRATION, CalibrationResult, run_calibration
from src.gestures.gesture_definitions import INDEX_FINGER_TIP, is_hand_open, is_pinching, is_pointing
from src.gestures.gesture_state_machine import GestureStateMachine, StateMachineConfig
from src.gestures.swipe_detector import SwipeDetector
from src.hud import overlay
from src.profiles.app_detector import AppProfileDetector
from src.profiles.profile_loader import load_profile
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_utils import draw_hand

_HANDEDNESS_ES = {"Left": "Derecha", "Right": "Izquierda"}
_ACTION_FLASH_FRAMES = 15
_ACTION_LABELS_ES = {
    "mouse_click_left": "CLIC IZQUIERDO",
    "mouse_click_right": "CLIC DERECHO",
    "presentation_next_slide": "SIGUIENTE DIAPOSITIVA",
    "presentation_previous_slide": "DIAPOSITIVA ANTERIOR",
    "media_play_pause": "PLAY / PAUSA",
}


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
        help="Imprime las acciones y no mueve el cursor real (util para probar sin efectos en el sistema)",
    )
    parser.add_argument(
        "--skip-calibration",
        action="store_true",
        help="Omite la calibracion de cursor y usa una zona cómoda por defecto",
    )
    return parser.parse_args()


def _move_cursor_to_index_tip(
    image,
    hand,
    calibration: CalibrationResult,
    cursor_smoother: CursorSmoother,
    controller: ActionController,
    screen_w: int,
    screen_h: int,
) -> None:
    """Mapea la punta del índice a la pantalla (vía calibración + suavizado),
    mueve el cursor real y dibuja la marca del punto controlado. Comparten
    esta lógica el perfil `mouse` (cursor_control, siempre activo con mano
    visible) y `presentation` (pointer_control, solo mientras se apunta)."""
    index_x, index_y = hand.landmarks[INDEX_FINGER_TIP][:2]
    unit_x, unit_y = calibration.map_to_unit_square(index_x, index_y)
    smooth_x, smooth_y = cursor_smoother.smooth(unit_x * screen_w, unit_y * screen_h)
    controller.move_cursor(int(smooth_x), int(smooth_y))
    cursor_pixel = (int(index_x * image.shape[1]), int(index_y * image.shape[0]))
    overlay.draw_cursor_target(image, cursor_pixel)


def main() -> None:
    args = parse_args()
    controller = ActionController(dry_run=args.dry_run)
    screen_w, screen_h = pyautogui.size()

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
        calibration = (
            DEFAULT_CALIBRATION if args.skip_calibration else run_calibration(camera, tracker, window_name=window_name)
        )

        pinch_machine = GestureStateMachine(StateMachineConfig(confirm_frames=3, cooldown_frames=10))
        swipe_detector = SwipeDetector()
        cursor_smoother = CursorSmoother()
        action_flash_remaining = 0
        action_flash_text = ""

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
                    cursor_smoother.reset()  # evita un salto usando la última posición del perfil anterior
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

            pinching = hand is not None and is_pinching(hand.landmarks)
            fired_pinch = pinch_machine.update(active=pinching)
            if fired_pinch:
                action_name = profile.action_for("pinch")
                if action_name:
                    controller.execute(action_name)
                    prefix = "[dry-run] " if args.dry_run else ""
                    print(f"{prefix}[{profile.name}] pellizco -> {action_name}")
                    action_flash_text = _ACTION_LABELS_ES.get(action_name, action_name.replace("_", " ").upper())
                    action_flash_remaining = _ACTION_FLASH_FRAMES

            # No consideramos la mano "abierta" para el swipe mientras hay un
            # pellizco sostenido (un "OK" con los demás dedos extendidos
            # también pasaría is_hand_open), para que arrastrar la mano en
            # medio de un clic no dispare un swipe por accidente.
            hand_open = hand is not None and is_hand_open(hand.landmarks) and not pinching
            wrist_x = hand.landmarks[0][0] if hand is not None else None
            swipe_direction = swipe_detector.update(hand_open, wrist_x)
            if swipe_direction:
                gesture_name = f"swipe_{swipe_direction}"
                action_name = profile.action_for(gesture_name)
                if action_name:
                    controller.execute(action_name)
                    prefix = "[dry-run] " if args.dry_run else ""
                    print(f"{prefix}[{profile.name}] {gesture_name} -> {action_name}")
                    action_flash_text = _ACTION_LABELS_ES.get(action_name, action_name.replace("_", " ").upper())
                    action_flash_remaining = _ACTION_FLASH_FRAMES

            # cursor_control mueve el cursor con solo tener una mano visible
            # (perfil mouse); pointer_control (perfil presentation) exige
            # además la seña de "apuntar", para no mover el puntero láser
            # cada vez que la mano pasa por el cuadro sin intención de señalar.
            if hand is not None and (profile.cursor_control or (profile.pointer_control and is_pointing(hand.landmarks))):
                _move_cursor_to_index_tip(image, hand, calibration, cursor_smoother, controller, screen_w, screen_h)

            if hand is not None:
                draw_hand(image, hand.landmarks)
                wrist_x_px, wrist_y_px = (hand.landmarks[0][:2] * [image.shape[1], image.shape[0]]).astype(int)
                label = _HANDEDNESS_ES[hand.handedness]
                overlay.draw_hand_label(image, (wrist_x_px, wrist_y_px), label, hand.score)

            if action_flash_remaining > 0:
                overlay.draw_action_flash(image, action_flash_text)
                action_flash_remaining -= 1

            frames_since_update += 1
            now = time.monotonic()
            if now - last_fps_update >= 0.5:
                display_fps = frames_since_update / (now - last_fps_update)
                frames_since_update = 0
                last_fps_update = now

            overlay.draw_status_bar(image, display_fps, profile.name, pinch_machine.state.value, camera.dropped_frames)
            cv2.imshow(window_name, image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
