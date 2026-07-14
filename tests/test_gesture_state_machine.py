from src.gestures.gesture_state_machine import GestureState, GestureStateMachine, StateMachineConfig


def make_machine() -> GestureStateMachine:
    return GestureStateMachine(StateMachineConfig(confirm_frames=3, cooldown_frames=2))


def test_stays_idle_without_activity():
    machine = make_machine()

    assert machine.update(False) is False
    assert machine.state == GestureState.IDLE


def test_needs_confirm_frames_before_firing():
    machine = make_machine()

    assert machine.update(True) is False
    assert machine.state == GestureState.CANDIDATE
    assert machine.update(True) is False
    assert machine.state == GestureState.CANDIDATE
    assert machine.update(True) is True
    assert machine.state == GestureState.CONFIRMED


def test_releasing_early_resets_to_idle():
    machine = make_machine()

    machine.update(True)
    machine.update(True)
    assert machine.state == GestureState.CANDIDATE

    machine.update(False)
    assert machine.state == GestureState.IDLE


def test_does_not_refire_while_held_through_cooldown():
    machine = make_machine()

    fired_frames = [machine.update(True) for _ in range(10)]

    assert fired_frames.count(True) == 1


def test_returns_to_idle_after_being_released_for_cooldown_frames():
    machine = make_machine()
    for _ in range(3):
        machine.update(True)
    assert machine.state == GestureState.CONFIRMED

    machine.update(True)
    assert machine.state == GestureState.COOLDOWN

    for _ in range(machine.config.cooldown_frames):
        machine.update(False)
    assert machine.state == GestureState.IDLE


def test_can_fire_again_after_a_full_release_cycle():
    machine = make_machine()

    for _ in range(3):
        machine.update(True)
    machine.update(True)
    for _ in range(machine.config.cooldown_frames):
        machine.update(False)
    assert machine.state == GestureState.IDLE

    fired_again = [machine.update(True) for _ in range(3)]
    assert fired_again[-1] is True
