from __future__ import annotations


class CursorSmoother:
    """Suaviza la posición del cursor con un promedio móvil exponencial, para
    que el temblor de landmark a landmark no se traduzca en un cursor que
    salta de un pixel a otro entre frames en vez de deslizarse."""

    def __init__(self, smoothing_factor: float = 0.4) -> None:
        if not 0.0 < smoothing_factor <= 1.0:
            raise ValueError("smoothing_factor debe estar en el rango (0, 1]")
        self._smoothing_factor = smoothing_factor
        self._smoothed_x: float | None = None
        self._smoothed_y: float | None = None

    def smooth(self, x: float, y: float) -> tuple[float, float]:
        if self._smoothed_x is None or self._smoothed_y is None:
            self._smoothed_x, self._smoothed_y = x, y
        else:
            alpha = self._smoothing_factor
            self._smoothed_x += alpha * (x - self._smoothed_x)
            self._smoothed_y += alpha * (y - self._smoothed_y)
        return self._smoothed_x, self._smoothed_y

    def reset(self) -> None:
        self._smoothed_x = None
        self._smoothed_y = None
