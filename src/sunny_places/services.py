from __future__ import annotations

from datetime import datetime, timedelta, timezone

import streamlit as st
from requests import RequestException

from sunny_places.comfort import calculate_comfort_score
from sunny_places.demo_logic import compute_grid_size_for_radius
from sunny_places.geocoding import fetch_nearby_bars, fetch_nearby_places, search_places
from sunny_places.models import (
    AnalysisBasePayload,
    CandidatePlace,
    SamplePoint,
    SearchResult,
    WeatherSnapshot,
)
from sunny_places.sampling import (
    apply_terrain_metrics,
    generate_sample_grid,
    great_circle_distance_m,
)
from sunny_places.solar import calculate_sun_score
from sunny_places.ui_state import build_sample_key
from sunny_places.weather import fetch_elevations, fetch_weather_snapshot
from sunny_places.wind import calculate_wind_score


@st.cache_data(show_spinner=False, ttl=1800)
def cached_search_places(query: str, limit: int = 5) -> list[SearchResult]:
    return search_places(query, limit=limit)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_fetch_nearby_places(
    latitude: float,
    longitude: float,
    radius_m: float,
) -> list[CandidatePlace]:
    return fetch_nearby_places(latitude, longitude, radius_m=radius_m)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_fetch_nearby_bars(
    latitude: float,
    longitude: float,
    radius_m: float,
) -> list[CandidatePlace]:
    return fetch_nearby_bars(latitude, longitude, radius_m=radius_m)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_fetch_weather_snapshot(
    latitude: float,
    longitude: float,
    target_datetime: datetime,
) -> WeatherSnapshot:
    return fetch_weather_snapshot(latitude, longitude, target_datetime)


@st.cache_data(show_spinner=False, ttl=86400)
def cached_fetch_elevations(
    latitudes: tuple[float, ...],
    longitudes: tuple[float, ...],
) -> list[float]:
    return fetch_elevations(list(latitudes), list(longitudes))


def _build_local_datetime(target_datetime: datetime, offset_seconds: int) -> datetime:
    offset = timezone(timedelta(seconds=offset_seconds))
    return target_datetime.replace(tzinfo=offset)


def _fallback_weather_snapshot() -> WeatherSnapshot:
    return WeatherSnapshot(
        cloud_cover=20.0,
        shortwave_radiation=700.0,
        direct_radiation=520.0,
        diffuse_radiation=120.0,
        direct_normal_irradiance=760.0,
        wind_speed_10m=16.0,
        wind_gusts_10m=24.0,
        wind_direction_10m=300.0,
        timezone_name="UTC",
        utc_offset_seconds=0,
    )


def _attach_nearest_sample_keys(
    places: list[CandidatePlace],
    samples: list[SamplePoint],
) -> list[CandidatePlace]:
    for place in places:
        nearest_sample = min(
            samples,
            key=lambda sample: great_circle_distance_m(
                place.latitude,
                place.longitude,
                sample.latitude,
                sample.longitude,
            ),
        )
        place.metadata["nearest_sample_key"] = build_sample_key(nearest_sample)
        place.metadata["nearest_sample_latitude"] = nearest_sample.latitude
        place.metadata["nearest_sample_longitude"] = nearest_sample.longitude
    return places


def build_weather_context(
    weather_snapshot: WeatherSnapshot,
    radius_m: float,
    layer_mode: str,
) -> dict[str, float]:
    return {
        "cloud_cover": weather_snapshot.cloud_cover,
        "shortwave_radiation": weather_snapshot.shortwave_radiation,
        "direct_radiation": weather_snapshot.direct_radiation,
        "diffuse_radiation": weather_snapshot.diffuse_radiation,
        "direct_normal_irradiance": weather_snapshot.direct_normal_irradiance,
        "wind_speed_10m": weather_snapshot.wind_speed_10m,
        "wind_gusts_10m": weather_snapshot.wind_gusts_10m,
        "wind_direction_10m": weather_snapshot.wind_direction_10m,
        "radius_m": radius_m,
        "layer_mode": layer_mode,
    }


def apply_active_layer_scores(
    samples: list[SamplePoint],
    places: list[CandidatePlace],
    layer_mode: str,
) -> tuple[list[SamplePoint], list[CandidatePlace]]:
    sample_scores: dict[str, float] = {}
    for sample in samples:
        if layer_mode == "wind":
            sample.score = sample.wind_score
        elif layer_mode == "comfort":
            sample.score = calculate_comfort_score(
                sample.sun_score or 0.0, sample.wind_score or 0.0
            )
        else:
            sample.score = sample.sun_score
        sample_scores[build_sample_key(sample)] = sample.score or 0.0

    for place in places:
        nearest_sample_key = str(place.metadata.get("nearest_sample_key", ""))
        place.score = sample_scores.get(nearest_sample_key, 0.0)

    return samples, places


@st.cache_data(show_spinner=False, ttl=1800)
def cached_compute_analysis_base(
    latitude: float,
    longitude: float,
    target_datetime_iso: str,
    radius_m: float,
) -> AnalysisBasePayload:
    target_datetime = datetime.fromisoformat(target_datetime_iso)
    warnings: list[str] = []
    grid_size = compute_grid_size_for_radius(radius_m)
    samples = generate_sample_grid(
        latitude,
        longitude,
        radius_m=radius_m,
        grid_size=grid_size,
    )

    try:
        elevations = cached_fetch_elevations(
            tuple(sample.latitude for sample in samples),
            tuple(sample.longitude for sample in samples),
        )
        for sample, elevation in zip(samples, elevations, strict=True):
            sample.elevation_m = elevation
        samples = apply_terrain_metrics(samples)
    except RequestException:
        warnings.append("provider_warning")

    try:
        weather_snapshot = cached_fetch_weather_snapshot(
            latitude,
            longitude,
            target_datetime,
        )
    except RequestException:
        weather_snapshot = _fallback_weather_snapshot()
        warnings.append("provider_warning")

    localized_datetime = _build_local_datetime(target_datetime, weather_snapshot.utc_offset_seconds)
    for sample in samples:
        sample.sun_score = calculate_sun_score(
            sample.latitude,
            sample.longitude,
            localized_datetime,
            weather_snapshot,
            slope_deg=sample.slope_deg,
            aspect_deg=sample.aspect_deg,
        )
        sample.wind_score = calculate_wind_score(
            weather_snapshot,
            slope_deg=sample.slope_deg,
            aspect_deg=sample.aspect_deg,
        )

    try:
        places = cached_fetch_nearby_places(
            latitude,
            longitude,
            radius_m=radius_m,
        )
        places = _attach_nearest_sample_keys(places, samples)
    except RequestException:
        places = []
        warnings.append("provider_warning")

    return AnalysisBasePayload(
        samples=samples,
        places=places,
        weather_snapshot=weather_snapshot,
        warnings=warnings,
    )
