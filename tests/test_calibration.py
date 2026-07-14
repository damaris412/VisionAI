import pytest

from src.gestures.calibration import CalibrationResult


def test_maps_center_of_calibrated_zone_to_center_of_unit_square():
    calibration = CalibrationResult(min_x=0.2, max_x=0.8, min_y=0.3, max_y=0.7)

    unit_x, unit_y = calibration.map_to_unit_square(0.5, 0.5)

    assert unit_x == pytest.approx(0.5)
    assert unit_y == pytest.approx(0.5)


def test_clamps_values_outside_the_calibrated_zone():
    calibration = CalibrationResult(min_x=0.2, max_x=0.8, min_y=0.2, max_y=0.8)

    assert calibration.map_to_unit_square(0.0, 0.0) == (0.0, 0.0)
    assert calibration.map_to_unit_square(1.0, 1.0) == (1.0, 1.0)


def test_maps_calibrated_bounds_to_unit_square_edges():
    calibration = CalibrationResult(min_x=0.25, max_x=0.75, min_y=0.1, max_y=0.9)

    assert calibration.map_to_unit_square(0.25, 0.1) == (0.0, 0.0)
    assert calibration.map_to_unit_square(0.75, 0.9) == (1.0, 1.0)


def test_does_not_divide_by_zero_when_zone_has_no_span():
    calibration = CalibrationResult(min_x=0.5, max_x=0.5, min_y=0.5, max_y=0.5)

    unit_x, unit_y = calibration.map_to_unit_square(0.5, 0.5)

    assert unit_x >= 0.0
    assert unit_y >= 0.0
