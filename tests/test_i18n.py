from sunny_places.i18n import get_text


def test_get_text_returns_spanish_copy_for_known_key() -> None:
    assert get_text("es", "app_title") == "Sunny Places"


def test_get_text_returns_english_copy_for_known_key() -> None:
    assert get_text("en", "search_label") == "Search a place"


def test_get_text_falls_back_to_spanish_for_missing_locale() -> None:
    assert get_text("fr", "map_title") == "Mapa solar"


def test_get_text_returns_key_when_missing_everywhere() -> None:
    assert get_text("es", "unknown.key") == "unknown.key"
