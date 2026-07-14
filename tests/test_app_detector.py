from src.profiles.app_detector import AppProfileDetector, load_app_profile_mapping

MAPPING = {"powerpnt.exe": "presentation", "vlc.exe": "media", "default": "mouse"}


def make_detector(process_name: str | None, poll_interval_s: float = 1.0) -> AppProfileDetector:
    return AppProfileDetector(
        mapping=MAPPING,
        poll_interval_s=poll_interval_s,
        process_name_provider=lambda: process_name,
    )


def test_maps_known_process_to_its_profile():
    detector = make_detector("powerpnt.exe")

    assert detector.poll(now=0.0) == "presentation"


def test_falls_back_to_default_for_unknown_process():
    detector = make_detector("notepad.exe")

    assert detector.poll(now=0.0) == "mouse"


def test_starts_with_default_profile_before_first_poll():
    detector = AppProfileDetector(mapping=MAPPING, process_name_provider=lambda: "vlc.exe")

    assert detector.current_profile == "mouse"


def test_caches_result_within_poll_interval():
    calls = []

    def provider() -> str:
        calls.append(1)
        return "powerpnt.exe"

    detector = AppProfileDetector(mapping=MAPPING, poll_interval_s=1.0, process_name_provider=provider)

    detector.poll(now=0.0)
    detector.poll(now=0.5)

    assert len(calls) == 1


def test_rechecks_after_poll_interval_elapses():
    calls = []

    def provider() -> str:
        calls.append(1)
        return "vlc.exe"

    detector = AppProfileDetector(mapping=MAPPING, poll_interval_s=1.0, process_name_provider=provider)

    detector.poll(now=0.0)
    detector.poll(now=1.5)

    assert len(calls) == 2


def test_keeps_previous_profile_when_process_name_becomes_unavailable():
    responses = iter(["powerpnt.exe", None])
    detector = AppProfileDetector(
        mapping=MAPPING, poll_interval_s=0.0, process_name_provider=lambda: next(responses)
    )

    assert detector.poll(now=0.0) == "presentation"
    assert detector.poll(now=1.0) == "presentation"


def test_load_app_profile_mapping_reads_real_config_file():
    mapping = load_app_profile_mapping()

    assert mapping["powerpnt.exe"] == "presentation"
    assert mapping["default"] == "mouse"
