import pytest

from src.actions.cursor_smoother import CursorSmoother


def test_first_call_snaps_directly_to_input():
    smoother = CursorSmoother(smoothing_factor=0.4)

    assert smoother.smooth(100.0, 200.0) == (100.0, 200.0)


def test_moves_partway_toward_new_position_each_call():
    smoother = CursorSmoother(smoothing_factor=0.5)

    smoother.smooth(0.0, 0.0)
    x, y = smoother.smooth(100.0, 100.0)

    assert x == pytest.approx(50.0)
    assert y == pytest.approx(50.0)


def test_converges_to_a_steady_target_over_repeated_calls():
    smoother = CursorSmoother(smoothing_factor=0.3)

    smoother.smooth(0.0, 0.0)
    for _ in range(50):
        x, y = smoother.smooth(100.0, 100.0)

    assert x == pytest.approx(100.0, abs=0.01)
    assert y == pytest.approx(100.0, abs=0.01)


def test_reset_clears_state_so_next_call_snaps_again():
    smoother = CursorSmoother(smoothing_factor=0.3)
    smoother.smooth(0.0, 0.0)

    smoother.reset()

    assert smoother.smooth(500.0, 500.0) == (500.0, 500.0)


def test_rejects_out_of_range_smoothing_factor():
    with pytest.raises(ValueError):
        CursorSmoother(smoothing_factor=0.0)
    with pytest.raises(ValueError):
        CursorSmoother(smoothing_factor=1.5)
