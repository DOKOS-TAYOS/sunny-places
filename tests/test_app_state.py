from sunny_places.app_state import get_default_view_state


def test_default_view_state_starts_in_bilbao_dark_mode_and_spanish() -> None:
    state = get_default_view_state()

    assert state.center.latitude == 43.2630
    assert state.center.longitude == -2.9350
    assert state.locale == "es"
    assert state.theme == "dark"
