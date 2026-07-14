# VisionAI

Framework de control por gestos de mano en tiempo real, construido con Python, OpenCV y MediaPipe (modelos de IA para tracking de manos). Reconoce gestos vía cámara web y los traduce en acciones del sistema operativo (mover cursor, clic, scroll, atajos) según un **perfil** activo intercambiable (mouse, presentaciones, reproductor multimedia).

## Estado del proyecto

En desarrollo iterativo. Progreso actual:

- [x] **Fase 0-1**: Entorno + captura de video en hilo dedicado (productor-consumidor, sin acumulación de lag)
- [ ] Fase 2: Detección de manos y landmarks (MediaPipe Hands)
- [ ] Fase 3: Máquina de estados para reconocimiento de gestos
- [ ] Fase 4: Sistema de perfiles (YAML) y mapeo de acciones
- [ ] Fase 5: Detección de aplicación activa y cambio automático de perfil
- [ ] Fase 6: HUD visual, calibración de usuario, suavizado de cursor
- [ ] Fase 7: Tests, CI, documentación final

## Arquitectura

```
src/
├── capture/    # Captura de cámara en hilo dedicado (camera_stream.py, frame_queue.py)
├── vision/     # Wrapper de MediaPipe Hands, utilidades de landmarks
├── gestures/   # Máquina de estados + reglas geométricas de reconocimiento
├── profiles/   # Carga de perfiles YAML + detección de app activa
├── actions/    # Ejecución de acciones del SO (pyautogui) + suavizado de cursor
└── hud/        # Overlay visual de depuración/feedback en pantalla
```

Cada gesto detectado se emite como un evento desacoplado de la acción que dispara — el mismo gesto puede significar cosas distintas según el perfil activo.

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
