import time

import cv2

from src.capture.camera_stream import CameraStream

WINDOW_NAME = "Vision Gestos - Paso 1: Captura"


def main() -> None:
    with CameraStream(camera_index=0, width=1280, height=720, target_fps=30) as camera:
        last_fps_update = time.monotonic()
        frames_since_update = 0
        display_fps = 0.0

        while True:
            frame = camera.read(timeout=2.0)
            if frame is None:
                print("No se recibieron frames de la cámara (timeout). Saliendo.")
                break

            frames_since_update += 1
            now = time.monotonic()
            if now - last_fps_update >= 0.5:
                display_fps = frames_since_update / (now - last_fps_update)
                frames_since_update = 0
                last_fps_update = now

            image = cv2.flip(frame.image, 1)
            cv2.putText(
                image,
                f"FPS: {display_fps:.1f}  |  descartados: {camera.dropped_frames}",
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
