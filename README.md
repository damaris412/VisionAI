# VisionAI

Framework de control por gestos de mano en tiempo real, construido con Python, OpenCV y MediaPipe (modelos de IA para tracking de manos). Reconoce gestos vía cámara web y los traduce en acciones del sistema operativo (mover cursor, clic, scroll, atajos) según un **perfil** activo intercambiable (mouse, presentaciones, reproductor multimedia).

## Estado del proyecto

En desarrollo iterativo. Progreso actual:

- [x] **Fase 0-1**: Entorno + captura de video en hilo dedicado (productor-consumidor, sin acumulación de lag)
- [x] **Fase 2**: Detección de manos y landmarks (MediaPipe HandLandmarker, Tasks API)
- [x] **Fase 3**: Máquina de estados para reconocimiento de gestos (gesto de pellizco -> clic)
- [ ] Fase 4: Sistema de perfiles (YAML) y mapeo de acciones
- [ ] Fase 5: Detección de aplicación activa y cambio automático de perfil
- [ ] Fase 6: HUD visual, calibración de usuario, suavizado de cursor
- [ ] Fase 7: Tests, CI, documentación final

## Arquitectura

```
src/
├── capture/    # Captura de cámara en hilo dedicado (camera_stream.py, frame_queue.py)
├── vision/     # Wrapper de MediaPipe HandLandmarker, utilidades de landmarks
├── gestures/   # Máquina de estados + reglas geométricas de reconocimiento
├── profiles/   # Carga de perfiles YAML + detección de app activa
├── actions/    # Ejecución de acciones del SO (pyautogui) + suavizado de cursor
└── hud/        # Overlay visual de depuración/feedback en pantalla
```

Cada gesto detectado se emite como un evento desacoplado de la acción que dispara — el mismo gesto puede significar cosas distintas según el perfil activo.

## Modelos de IA

`src/vision/hand_tracker.py` usa MediaPipe **HandLandmarker** (Tasks API) para
detectar 21 puntos clave por mano. El modelo entrenado (~8 MB) se descarga
automáticamente en `models/` la primera vez que se ejecuta — no se versiona en
git, igual que los pesos de cualquier modelo de ML.

## Reconocimiento de gestos

`src/gestures/gesture_state_machine.py` filtra la señal ruidosa por frame
(IDLE → CANDIDATE → CONFIRMED → COOLDOWN) para que un gesto sostenido dispare
un único evento en vez de decenas mientras tiembla la mano. `gesture_definitions.py`
define las reglas geométricas sobre los landmarks; el primer gesto implementado
es **pellizco (pulgar + índice) → clic**, con la distancia normalizada por el
tamaño de la palma para que el umbral no dependa de qué tan cerca está la mano
de la cámara.

## Requisitos

- Python 3.11–3.13 (MediaPipe aún no soporta 3.14 al momento de escribir esto)
- Cámara web

## Instalación

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

Presiona `q` para salir.

## Desarrollo

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```
