# Roadmap de gestos — perfil `presentation`

Notas de uso real y gestos propuestos para exposiciones orales con diapositivas
(PowerPoint / Canva / Google Slides), a partir de feedback de uso en vivo.

## Configuración de pantalla (HDMI / proyector)

VisionAI no necesita ninguna configuración especial para presentar:

1. `Win + P` → **Extender** (no "Duplicar"). El proyector muestra solo la
   presentación en pantalla completa; tu laptop sigue mostrando su propio
   escritorio, incluida la ventana de VisionAI con la cámara.
2. La webcam sigue viendo lo que tenga enfrente sin importar qué se proyecta.
3. **Cuidado con el foco de ventana**: las acciones de "avanzar/retroceder
   diapositiva" simulan una tecla (`pyautogui.press("right"/"left")`), que
   llega a la ventana que tenga el foco del sistema operativo en ese momento.
   Si se hace click sobre la ventana de VisionAI, la tecla le llega a esa
   ventana en vez de a PowerPoint. Conviene no tocar la ventana de la cámara
   una vez que arrancó la presentación.

## Gestos implementados

| Gesto | Cómo se hace | Acción | Módulo |
|---|---|---|---|
| Swipe derecha | Mano abierta (4 dedos extendidos), desplazar de izquierda a derecha | Avanzar diapositiva | `src/gestures/swipe_detector.py` |
| Swipe izquierda | Mano abierta, desplazar de derecha a izquierda | Retroceder diapositiva | `src/gestures/swipe_detector.py` |
| Pellizco (respaldo) | Pulgar + índice se tocan | Avanzar diapositiva | `src/gestures/gesture_definitions.py` |
| Puntero/láser virtual | Solo índice extendido, resto curvado (`is_pointing`) | Mueve el cursor real, siguiendo la punta del índice | `is_pointing()` + `pointer_control` en `Profile` |

**Nota de sensibilidad**: el swipe se calibró originalmente para uso "de
escritorio" (25% del ancho del cuadro en 8 frames / ~0.27s), demasiado
exigente para presentar de pie y lejos de la cámara. Ajustado a
`min_displacement=0.15`, `window_frames=10` — pendiente de volver a probar en
vivo con este nuevo umbral.

## Gestos propuestos (no implementados aún)

| Gesto | Cómo se hace | Acción propuesta | Notas de factibilidad |
|---|---|---|---|
| Zoom | Pellizco pulgar-índice que se abre (zoom in) o se cierra (zoom out) | Zoom sobre la diapositiva/imagen | **Sin solución universal todavía**: ni PowerPoint en modo presentación, ni Canva, ni Google Slides tienen un atajo de teclado estándar para zoom en vivo. Falta decidir la app objetivo y la acción exacta antes de implementar |
| Doble "clic" con índice | Mover el índice hacia adelante y atrás dos veces rápido | Doble clic (reproducir/interactuar con un objeto de la diapositiva) | Necesita un detector nuevo, similar en espíritu a `SwipeDetector` pero midiendo desplazamiento en profundidad (Z) o un patrón de dos pulsos en vez de posición X |
| Puño abrir/cerrar | Cerrar el puño y volver a abrir | Play/Pause de video embebido (tecla espacio) | Necesita `is_fist()` — el opuesto de `is_hand_open()`, incluyendo el pulgar curvado hacia la palma |

## Cómo continuar

Cuando se retome este trabajo, priorizar en este orden sugerido:
1. ~~Ajustar sensibilidad del swipe existente~~ — hecho.
2. ~~Puntero/láser virtual~~ — hecho (`is_pointing()` + `pointer_control`).
3. Puño para play/pause (gesto nuevo simple, geometría similar a `is_hand_open`).
4. Doble clic con índice (gesto nuevo, requiere diseño de detector).
5. Zoom (bloqueado hasta decidir una acción concreta y viable por app).
