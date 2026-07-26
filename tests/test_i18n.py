from sunny_places.i18n import get_text


def test_get_text_returns_spanish_copy_for_known_key() -> None:
    assert get_text("es", "app_title") == "Sunny Places"


def test_get_text_returns_english_copy_for_known_key() -> None:
    assert get_text("en", "search_label") == "Search a place"


def test_get_text_falls_back_to_spanish_for_missing_locale() -> None:
    assert get_text("fr", "map_title") == "Mapa solar"


def test_get_text_returns_key_when_missing_everywhere() -> None:
    assert get_text("es", "unknown.key") == "unknown.key"


def test_data_sources_caption_credits_copernicus_and_osm_tiles() -> None:
    spanish = get_text("es", "data_sources_caption")
    english = get_text("en", "data_sources_caption")

    for caption in (spanish, english):
        assert "Open-Meteo" in caption
        assert "Copernicus DEM GLO-90" in caption
        assert "OpenStreetMap" in caption
        assert "CARTO" not in caption
        assert "basemaps.cartocdn.com" not in caption

    assert "programa Copernicus" in spanish
    assert "Copernicus programme" in english
