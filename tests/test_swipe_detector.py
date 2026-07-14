from src.gestures.swipe_detector import SwipeConfig, SwipeDetector


def make_detector(**overrides) -> SwipeDetector:
    config = SwipeConfig(window_frames=4, min_displacement=0.3, cooldown_frames=3, **overrides)
    return SwipeDetector(config)


def test_no_swipe_while_hand_is_closed():
    detector = make_detector()

    results = [detector.update(False, 0.5) for _ in range(10)]

    assert all(result is None for result in results)


def test_detects_rightward_swipe_when_displacement_exceeds_threshold():
    detector = make_detector()

    results = [detector.update(True, x) for x in [0.1, 0.2, 0.3, 0.5]]

    assert results == [None, None, None, "right"]


def test_detects_leftward_swipe_when_displacement_exceeds_threshold():
    detector = make_detector()

    results = [detector.update(True, x) for x in [0.5, 0.4, 0.3, 0.1]]

    assert results == [None, None, None, "left"]


def test_no_swipe_when_displacement_is_too_small():
    detector = make_detector()

    results = [detector.update(True, x) for x in [0.4, 0.45, 0.42, 0.44]]

    assert all(result is None for result in results)


def test_cooldown_prevents_immediate_retrigger():
    detector = make_detector()

    for x in [0.1, 0.2, 0.3, 0.5]:
        detector.update(True, x)  # dispara "right" en el último update

    results_during_cooldown = [detector.update(True, x) for x in [0.5, 0.6, 0.7]]

    assert all(result is None for result in results_during_cooldown)


def test_can_fire_again_after_cooldown_and_new_window():
    detector = make_detector()

    for x in [0.1, 0.2, 0.3, 0.5]:
        detector.update(True, x)
    for x in [0.5, 0.6, 0.7]:  # consume el cooldown de 3 frames
        detector.update(True, x)

    results = [detector.update(True, x) for x in [0.1, 0.2, 0.3, 0.5]]

    assert results == [None, None, None, "right"]


def test_losing_the_hand_resets_the_window():
    detector = make_detector()

    detector.update(True, 0.1)
    detector.update(True, 0.2)
    detector.update(False, None)

    results = [detector.update(True, x) for x in [0.5, 0.6, 0.7]]

    assert all(result is None for result in results)
