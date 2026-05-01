from __future__ import annotations

DARK_THEME: dict[str, str | float] = {
    "base": "dark",
    "background": "#07111d",
    "panel": "#0f1b2d",
    "text": "#f5f7fb",
    "muted": "#9fb2c9",
    "accent": "#ffbc42",
    "accent_secondary": "#7ae7c7",
}


def build_map_style() -> dict[str, str | float]:
    return {
        "basemap_style": "dark",
        "heatmap_alpha": 0.28,
        "point_fill": [255, 188, 66, 145],
        "selected_fill": [122, 231, 199, 230],
    }


def build_streamlit_css() -> str:
    return f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at top left, rgba(255,188,66,0.12), transparent 28%),
            radial-gradient(circle at top right, rgba(122,231,199,0.10), transparent 25%),
            linear-gradient(180deg, {DARK_THEME["background"]} 0%, #050b14 100%);
        color: {DARK_THEME["text"]};
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(15,27,45,0.98), rgba(7,17,29,0.98));
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    .sunny-card {{
        background: rgba(15, 27, 45, 0.82);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 35px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }}
    .sunny-muted {{
        color: {DARK_THEME["muted"]};
        font-size: 0.95rem;
    }}
    .sunny-card-strong {{
        border-color: rgba(122,231,199,0.45);
        box-shadow: 0 12px 36px rgba(122,231,199,0.14);
    }}
    .sunny-kpi {{
        display: inline-block;
        margin-right: 0.85rem;
        margin-top: 0.45rem;
        padding: 0.4rem 0.6rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        font-size: 0.88rem;
    }}
    </style>
    """
