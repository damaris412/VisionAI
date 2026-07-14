# VisionAI

Framework de control por gestos de mano en tiempo real, construido con Python, OpenCV y MediaPipe (modelos de IA para tracking de manos). Reconoce gestos vía cámara web y los traduce en acciones del sistema operativo (mover cursor, clic, scroll, atajos) según un **perfil** activo intercambiable (mouse, presentaciones, reproductor multimedia).

## Estado del proyecto

En desarrollo iterativo. Progreso actual:

- [x] **Fase 0-1**: Entorno + captura de video en hilo dedicado (productor-consumidor, sin acumulación de lag)
- [x] **Fase 2**: Detección de manos y landmarks (MediaPipe HandLandmarker, Tasks API)
- [x] **Fase 3**: Máquina de estados para reconocimiento de gestos (gesto de pellizco -> clic)
- [x] **Fase 4**: Sistema de perfiles (YAML) y mapeo de acciones
- [x] **Fase 5**: Detección de aplicación activa y cambio automático de perfil (Windows)
- [x] **Fase 6**: HUD visual, calibración de usuario, suavizado de cursor, gesto de swipe
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

`src/gestures/swipe_detector.py` reconoce un segundo tipo de gesto: **swipe**
(deslizar la mano abierta de un lado al otro). A diferencia del pellizco (una
señal estática por frame), el swipe es un patrón de movimiento — se trackea la
posición X de la muñeca en una ventana corta de frames y se dispara solo si el
desplazamiento neto supera un umbral en menos de esa ventana, con su propio
cooldown para no repetirse mientras la mano sigue en movimiento.

## Perfiles y acciones

El mismo gesto significa cosas distintas según el **perfil** activo — la
lógica de reconocimiento nunca sabe qué acción dispara, solo emite el nombre
del gesto. Los perfiles viven en `config/profiles/*.yaml`:

| Perfil | Gesto | Acción |
|---|---|---|
| `mouse` (default) | Pellizco | Clic izquierdo |
| `mouse` (default) | Índice (continuo) | Mover cursor |
| `presentation` | Swipe derecha/izquierda | Avanzar/retroceder diapositiva |
| `media` | Pellizco | Play/Pause |

`src/profiles/profile_loader.py` carga el YAML; `src/actions/controller.py`
traduce el nombre de acción a la llamada real de `pyautogui`. Ambos están
desacoplados: agregar un perfil nuevo es solo agregar un archivo YAML, sin
tocar código.

```bash
python main.py --profile presentation
python main.py --profile mouse --dry-run   # imprime la acción sin ejecutarla
```

## Detección automática de perfil (Windows)

Sin `--profile`, VisionAI detecta qué aplicación tiene el foco y carga el
perfil correspondiente solo, según `config/app_profiles.yaml` (proceso en
primer plano -> perfil; `default` cubre cualquier app no listada):

```bash
python main.py               # detección automática
python main.py --profile mouse   # fuerza un perfil fijo, desactiva la detección
```

`src/profiles/app_detector.py` usa `pywin32` para leer la ventana activa y
`psutil` para resolver el nombre del proceso; consulta el sistema como mucho
una vez por segundo (`AppProfileDetector.poll`), no en cada frame. Esta pieza
es específica de Windows por ahora.

## Control de cursor: calibración y suavizado

En el perfil `mouse`, la punta del índice mueve el cursor del sistema. Dos
piezas hacen que esto se sienta usable en vez de errático:

- **Calibración** (`src/gestures/calibration.py`): al iniciar, una pantalla
  guía al usuario a mover el índice por su zona cómoda de movimiento durante
  unos segundos. Esa zona (no el cuadro completo de la cámara) es la que se
  mapea a la pantalla completa, para no tener que estirar el brazo hasta el
  borde de la cámara para llegar a la esquina de la pantalla. `--skip-calibration`
  usa una zona por defecto razonable sin pasar por ese paso.
- **Suavizado** (`src/actions/cursor_smoother.py`): un promedio móvil
  exponencial sobre la posición mapeada, para que el temblor normal de la
  detección de landmarks no se traduzca en un cursor que salta de un pixel a
  otro en vez de deslizarse.

`ActionController.move_cursor` además recorta la posición final a un par de
pixels de cada borde de la pantalla: PyAutoGUI aborta con una excepción si el
cursor llega *exactamente* a una esquina (su mecanismo de "fail-safe" para que
el usuario recupere el control moviendo el mouse real) — el recorte evita que
el mapeo por gestos genere esa coordenada exacta, sin desactivar el fail-safe.

## HUD

`src/hud/overlay.py` centraliza el overlay de depuración/feedback: barra de
estado (FPS, perfil, estado del gesto, frames descartados), etiqueta de
lateralidad por mano, marca del punto que controla el cursor, y el flash de
"ACCION!" al confirmarse un gesto.

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
python main.py                       # detección automática de perfil, con calibración
python main.py --profile mouse       # fuerza el perfil mouse
python main.py --dry-run             # imprime acciones y no mueve el cursor/mouse real
python main.py --skip-calibration    # usa una zona de cursor por defecto
```

Presiona `q` para salir.

## Desarrollo

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```
