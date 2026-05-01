from __future__ import annotations

import html

import folium

from sunny_places.models import CandidatePlace, SamplePoint
from sunny_places.theme import DARK_THEME
from sunny_places.ui_state import build_place_key, build_sample_key

DARK_TILE_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
DARK_TILE_ATTR = "&copy; OpenStreetMap contributors &copy; CARTO"


def _build_popup_html(
    title: str,
    score: float,
    latitude: float,
    longitude: float,
    key: str,
    score_label: str,
    coordinates_label: str,
) -> str:
    safe_title = html.escape(title)
    return (
        f"<b>{safe_title}</b><br/>"
        f"{score_label}: {score:.1f}<br/>"
        f"{coordinates_label}: {latitude:.5f}, {longitude:.5f}<br/>"
        f"<span style='display:none'>place_key={key}</span>"
    )


def _score_to_fill(score: float) -> tuple[str, float]:
    if score >= 80:
        return "#ff9f1c", 0.72
    if score >= 60:
        return "#ffd166", 0.64
    if score >= 40:
        return "#8bd3ff", 0.54
    if score >= 20:
        return "#457b9d", 0.46
    return "#17324d", 0.34


def _derive_cell_deltas(samples: list[SamplePoint]) -> tuple[float, float]:
    latitudes = sorted({sample.latitude for sample in samples})
    longitudes = sorted({sample.longitude for sample in samples})
    latitude_step = 0.0012
    longitude_step = 0.0012
    if len(latitudes) > 1:
        latitude_step = min(
            abs(current - previous)
            for previous, current in zip(latitudes, latitudes[1:], strict=False)
            if abs(current - previous) > 0
        )
    if len(longitudes) > 1:
        longitude_step = min(
            abs(current - previous)
            for previous, current in zip(longitudes, longitudes[1:], strict=False)
            if abs(current - previous) > 0
        )
    return latitude_step / 2.0, longitude_step / 2.0


def _sample_popup_html(
    sample: SamplePoint,
    weather_context: dict[str, float],
    sample_label: str,
    score_label: str,
    coordinates_label: str,
    cloud_cover_label: str,
    direct_radiation_label: str,
    diffuse_radiation_label: str,
) -> str:
    return (
        _build_popup_html(
            sample_label,
            sample.score or 0.0,
            sample.latitude,
            sample.longitude,
            build_sample_key(sample),
            score_label,
            coordinates_label,
        )
        + f"<br/>{cloud_cover_label}: {weather_context['cloud_cover']:.0f}%"
        + f"<br/>{direct_radiation_label}: {weather_context['direct_radiation']:.0f} W/m2"
        + f"<br/>{diffuse_radiation_label}: {weather_context['diffuse_radiation']:.0f} W/m2"
        + f"<br/>Elevation: {(sample.elevation_m or 0.0):.0f} m"
        + f"<br/>Slope: {sample.slope_deg:.1f} deg"
    )


def _place_popup_html(
    place: CandidatePlace,
    weather_context: dict[str, float],
    score_label: str,
    coordinates_label: str,
    cloud_cover_label: str,
    direct_radiation_label: str,
    diffuse_radiation_label: str,
) -> str:
    return (
        _build_popup_html(
            place.name,
            place.score,
            place.latitude,
            place.longitude,
            build_place_key(place),
            score_label,
            coordinates_label,
        )
        + f"<br/>{cloud_cover_label}: {weather_context['cloud_cover']:.0f}%"
        + f"<br/>{direct_radiation_label}: {weather_context['direct_radiation']:.0f} W/m2"
        + f"<br/>{diffuse_radiation_label}: {weather_context['diffuse_radiation']:.0f} W/m2"
    )


def build_folium_map(
    center_latitude: float,
    center_longitude: float,
    samples: list[SamplePoint],
    places: list[CandidatePlace],
    selected_key: str | None,
    weather_context: dict[str, float],
    sample_label: str,
    score_label: str,
    coordinates_label: str,
    cloud_cover_label: str,
    direct_radiation_label: str,
    diffuse_radiation_label: str,
    zoom_start: int = 13,
) -> folium.Map:
    folium_map = folium.Map(
        location=[center_latitude, center_longitude],
        zoom_start=zoom_start,
        tiles=DARK_TILE_URL,
        attr=DARK_TILE_ATTR,
        control_scale=True,
    )

    latitude_delta, longitude_delta = _derive_cell_deltas(samples)
    samples_group = folium.FeatureGroup(name="heatmap-cells")
    for sample in samples:
        score = sample.score or 0.0
        fill_color, fill_opacity = _score_to_fill(score)
        sample_key = build_sample_key(sample)
        is_selected = sample_key == selected_key
        folium.Rectangle(
            bounds=[
                [sample.latitude - latitude_delta, sample.longitude - longitude_delta],
                [sample.latitude + latitude_delta, sample.longitude + longitude_delta],
            ],
            weight=2 if is_selected else 0.4,
            color=DARK_THEME["accent_secondary"] if is_selected else fill_color,
            fill=True,
            fill_color=fill_color,
            fill_opacity=min(fill_opacity + (0.16 if is_selected else 0.0), 0.92),
            popup=_sample_popup_html(
                sample,
                weather_context,
                sample_label,
                score_label,
                coordinates_label,
                cloud_cover_label,
                direct_radiation_label,
                diffuse_radiation_label,
            ),
            tooltip=f"{score_label}: {score:.1f}",
        ).add_to(samples_group)
    samples_group.add_to(folium_map)

    places_group = folium.FeatureGroup(name="places")
    for place in places:
        place_key = build_place_key(place)
        if place_key != selected_key:
            continue
        folium.CircleMarker(
            location=[place.latitude, place.longitude],
            radius=10,
            weight=3,
            color=DARK_THEME["accent_secondary"],
            fill=True,
            fill_color=DARK_THEME["accent"],
            fill_opacity=0.95,
            popup=_place_popup_html(
                place,
                weather_context,
                score_label,
                coordinates_label,
                cloud_cover_label,
                direct_radiation_label,
                diffuse_radiation_label,
            ),
            tooltip=place.name,
        ).add_to(places_group)
    places_group.add_to(folium_map)

    if selected_key:
        for place in places:
            if build_place_key(place) == selected_key:
                folium_map.location = [place.latitude, place.longitude]
                break
        else:
            for sample in samples:
                if build_sample_key(sample) == selected_key:
                    folium_map.location = [sample.latitude, sample.longitude]
                    break

    return folium_map
