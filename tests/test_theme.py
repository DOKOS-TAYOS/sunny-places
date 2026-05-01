from sunny_places.theme import DARK_THEME, build_map_style


def test_dark_theme_uses_dark_base_mode() -> None:
    assert DARK_THEME["base"] == "dark"


def test_build_map_style_exposes_low_heatmap_alpha() -> None:
    style = build_map_style()

    assert style["heatmap_alpha"] < 0.45
    assert style["basemap_style"]
