from sunny_places.theme import DARK_THEME, build_streamlit_css


def test_dark_theme_contains_expected_core_colors() -> None:
    assert DARK_THEME["background"].startswith("#")
    assert DARK_THEME["accent"].startswith("#")


def test_build_streamlit_css_includes_theme_colors() -> None:
    css = build_streamlit_css()

    assert DARK_THEME["background"] in css
    assert DARK_THEME["text"] in css
