from __future__ import annotations

from typing import Any

import folium

from sunny_places.map_folium import BASEMAP_TILES, build_folium_map
from sunny_places.models import CandidatePlace, SamplePoint
from sunny_places.ui_state import build_place_key, build_sample_key


def _weather_context() -> dict[str, float]:
    return {
        "cloud_cover": 20.0,
        "shortwave_radiation": 700.0,
        "direct_radiation": 520.0,
        "diffuse_radiation": 120.0,
        "direct_normal_irradiance": 760.0,
        "wind_speed_10m": 16.0,
        "wind_gusts_10m": 24.0,
        "wind_direction_10m": 300.0,
    }


def _build_map(**overrides: Any) -> folium.Map:
    sample = SamplePoint(latitude=43.2640, longitude=-2.9440, distance_m=0.0, score=42.0)
    kwargs: dict[str, Any] = {
        "center_latitude": 43.2640,
        "center_longitude": -2.9440,
        "samples": [sample],
        "places": [],
        "bar_places": [],
        "selected_key": build_sample_key(sample),
        "weather_context": _weather_context(),
        "sample_label": "Punto de muestra",
        "score_label": "Indice",
        "coordinates_label": "Coordenadas",
        "bars_label": "Bar",
        "cloud_cover_label": "Nubosidad",
        "shortwave_radiation_label": "Radiacion global",
        "direct_radiation_label": "Radiacion directa",
        "diffuse_radiation_label": "Radiacion difusa",
        "dni_label": "DNI",
        "wind_speed_label": "Viento",
        "wind_gusts_label": "Rachas",
        "wind_direction_label": "Direccion",
        "elevation_label": "Elevacion",
        "slope_label": "Pendiente",
        "layer_mode": "sun",
    }
    kwargs.update(overrides)
    return build_folium_map(**kwargs)


def test_selected_sample_popup_opens_by_default() -> None:
    folium_map = _build_map()
    rendered = folium_map.get_root().render()

    assert ".openPopup();" in rendered


def test_selected_sample_uses_permanent_tooltip() -> None:
    folium_map = _build_map()
    rendered = folium_map.get_root().render()

    assert '"permanent": true' in rendered


def test_selected_place_popup_opens_by_default() -> None:
    place = CandidatePlace(
        name="Parque",
        latitude=43.2640,
        longitude=-2.9440,
        category="park",
        score=42.0,
    )
    sample = SamplePoint(latitude=43.2640, longitude=-2.9440, distance_m=0.0, score=42.0)

    folium_map = _build_map(
        samples=[sample],
        places=[place],
        selected_key=build_place_key(place),
    )
    rendered = folium_map.get_root().render()

    assert ".openPopup();" in rendered


def test_basemap_uses_openstreetmap_tiles_not_carto() -> None:
    assert BASEMAP_TILES == "OpenStreetMap"

    rendered = _build_map().get_root().render()

    assert "openstreetmap.org" in rendered.lower()
    assert "basemaps.cartocdn.com" not in rendered
    assert "CARTO" not in rendered
