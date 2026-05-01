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
        "<div style='width: 300px; line-height: 1.35;'>"
        f"<b>{safe_title}</b><br/>"
        f"{score_label}: {score:.1f}<br/>"
        f"{coordinates_label}: {latitude:.5f}, {longitude:.5f}<br/>"
        f"<span style='display:none'>place_key={key}</span>"
        "</div>"
    )


def _interpolate_channel(start: int, end: int, ratio: float) -> int:
    return round(start + (end - start) * ratio)


def _score_to_fill(
    score: float,
    minimum_score: float,
    maximum_score: float,
    layer_mode: str,
) -> tuple[str, float]:
    if maximum_score <= minimum_score:
        ratio = 0.5
    else:
        ratio = (score - minimum_score) / (maximum_score - minimum_score)
    ratio = min(max(ratio, 0.0), 1.0)

    if ratio <= 0.5:
        local_ratio = ratio / 0.5
        if layer_mode == "wind":
            start = (18, 40, 66)
            end = (78, 188, 214)
        elif layer_mode == "comfort":
            start = (30, 54, 42)
            end = (102, 196, 145)
        else:
            start = (23, 50, 77)
            end = (139, 211, 255)
    else:
        local_ratio = (ratio - 0.5) / 0.5
        if layer_mode == "wind":
            start = (78, 188, 214)
            end = (190, 255, 222)
        elif layer_mode == "comfort":
            start = (102, 196, 145)
            end = (255, 214, 102)
        else:
            start = (139, 211, 255)
            end = (255, 159, 28)

    red = _interpolate_channel(start[0], end[0], local_ratio)
    green = _interpolate_channel(start[1], end[1], local_ratio)
    blue = _interpolate_channel(start[2], end[2], local_ratio)
    opacity = 0.34 + (0.42 * ratio)
    return f"#{red:02x}{green:02x}{blue:02x}", opacity


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
    weather_details_html: str,
    sample_label: str,
    score_label: str,
    coordinates_label: str,
    elevation_label: str,
    slope_label: str,
) -> str:
    return (
        "<div style='width: 300px;'>"
        + _build_popup_html(
            sample_label,
            sample.score or 0.0,
            sample.latitude,
            sample.longitude,
            build_sample_key(sample),
            score_label,
            coordinates_label,
        )
        + weather_details_html
        + f"<br/>{elevation_label}: {(sample.elevation_m or 0.0):.0f} m"
        + f"<br/>{slope_label}: {sample.slope_deg:.1f} deg"
        + "</div>"
    )


def _build_weather_details_html(
    weather_context: dict[str, float],
    cloud_cover_label: str,
    shortwave_radiation_label: str,
    direct_radiation_label: str,
    diffuse_radiation_label: str,
    dni_label: str,
    wind_speed_label: str,
    wind_gusts_label: str,
    wind_direction_label: str,
    layer_mode: str,
) -> str:
    default_details = (
        f"<br/>{wind_speed_label}: {weather_context['wind_speed_10m']:.1f} km/h"
        + f"<br/>{wind_gusts_label}: {weather_context['wind_gusts_10m']:.1f} km/h"
        + f"<br/>{wind_direction_label}: {weather_context['wind_direction_10m']:.0f} deg"
    )
    if layer_mode == "sun":
        return (
            f"<br/>{cloud_cover_label}: {weather_context['cloud_cover']:.0f}%"
            + f"<br/>{shortwave_radiation_label}: {weather_context['shortwave_radiation']:.0f} W/m2"
            + f"<br/>{direct_radiation_label}: {weather_context['direct_radiation']:.0f} W/m2"
            + f"<br/>{diffuse_radiation_label}: {weather_context['diffuse_radiation']:.0f} W/m2"
            + f"<br/>{dni_label}: {weather_context['direct_normal_irradiance']:.0f} W/m2"
        )
    if layer_mode == "comfort":
        return (
            f"<br/>{cloud_cover_label}: {weather_context['cloud_cover']:.0f}%"
            + f"<br/>{direct_radiation_label}: {weather_context['direct_radiation']:.0f} W/m2"
            + f"<br/>{wind_speed_label}: {weather_context['wind_speed_10m']:.1f} km/h"
            + f"<br/>{wind_gusts_label}: {weather_context['wind_gusts_10m']:.1f} km/h"
            + f"<br/>{wind_direction_label}: {weather_context['wind_direction_10m']:.0f} deg"
        )
    return default_details


def _place_popup_html(
    place: CandidatePlace,
    score_label: str,
    coordinates_label: str,
    weather_details_html: str,
) -> str:
    return (
        "<div style='width: 300px;'>"
        + _build_popup_html(
            place.name,
            place.score,
            place.latitude,
            place.longitude,
            build_place_key(place),
            score_label,
            coordinates_label,
        )
        + weather_details_html
        + "</div>"
    )


def _bar_popup_html(
    place: CandidatePlace,
    coordinates_label: str,
    bars_label: str,
) -> str:
    safe_name = html.escape(place.name)
    return (
        "<div style='width: 240px; line-height: 1.35;'>"
        f"<b>{safe_name}</b><br/>"
        f"{bars_label}: {html.escape(place.category)}<br/>"
        f"{coordinates_label}: {place.latitude:.5f}, {place.longitude:.5f}"
        "</div>"
    )


def build_folium_map(
    center_latitude: float,
    center_longitude: float,
    samples: list[SamplePoint],
    places: list[CandidatePlace],
    bar_places: list[CandidatePlace],
    selected_key: str | None,
    weather_context: dict[str, float],
    sample_label: str,
    score_label: str,
    coordinates_label: str,
    bars_label: str,
    cloud_cover_label: str,
    shortwave_radiation_label: str,
    direct_radiation_label: str,
    diffuse_radiation_label: str,
    dni_label: str,
    wind_speed_label: str,
    wind_gusts_label: str,
    wind_direction_label: str,
    elevation_label: str,
    slope_label: str,
    layer_mode: str,
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
    scores = [sample.score or 0.0 for sample in samples]
    minimum_score = min(scores, default=0.0)
    maximum_score = max(scores, default=0.0)
    samples_group = folium.FeatureGroup(name="heatmap-cells")
    weather_details_html = _build_weather_details_html(
        weather_context,
        cloud_cover_label,
        shortwave_radiation_label,
        direct_radiation_label,
        diffuse_radiation_label,
        dni_label,
        wind_speed_label,
        wind_gusts_label,
        wind_direction_label,
        layer_mode,
    )
    for sample in samples:
        score = sample.score or 0.0
        fill_color, fill_opacity = _score_to_fill(score, minimum_score, maximum_score, layer_mode)
        sample_key = build_sample_key(sample)
        is_selected = sample_key == selected_key
        sample_tooltip: str | folium.Tooltip
        if is_selected:
            sample_tooltip = folium.Tooltip(
                _sample_popup_html(
                    sample,
                    weather_details_html,
                    sample_label,
                    score_label,
                    coordinates_label,
                    elevation_label,
                    slope_label,
                ),
                permanent=True,
                sticky=False,
                direction="top",
            )
        else:
            sample_tooltip = f"{score_label}: {score:.1f}"
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
            popup=folium.Popup(
                _sample_popup_html(
                    sample,
                    weather_details_html,
                    sample_label,
                    score_label,
                    coordinates_label,
                    elevation_label,
                    slope_label,
                ),
                max_width=340,
                show=is_selected,
            ),
            tooltip=sample_tooltip,
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
            popup=folium.Popup(
                _place_popup_html(
                    place,
                    score_label,
                    coordinates_label,
                    weather_details_html,
                ),
                max_width=340,
                show=True,
            ),
            tooltip=place.name,
        ).add_to(places_group)
    places_group.add_to(folium_map)

    bars_group = folium.FeatureGroup(name="bars")
    for bar_place in bar_places:
        folium.CircleMarker(
            location=[bar_place.latitude, bar_place.longitude],
            radius=4,
            weight=1.5,
            color="#ffd166",
            fill=True,
            fill_color="#ff9f1c",
            fill_opacity=0.85,
            popup=folium.Popup(
                _bar_popup_html(
                    bar_place,
                    coordinates_label,
                    bars_label,
                ),
                max_width=260,
            ),
            tooltip=bar_place.name,
        ).add_to(bars_group)
    bars_group.add_to(folium_map)

    return folium_map
