from sunny_places.app_state import DEFAULT_CENTER, DEFAULT_LOCALE


def test_default_app_state_starts_in_bilbao_and_spanish() -> None:
    assert DEFAULT_CENTER.latitude == 43.2630
    assert DEFAULT_CENTER.longitude == -2.9350
    assert DEFAULT_LOCALE == "es"
