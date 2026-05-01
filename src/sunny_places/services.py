from __future__ import annotations

from datetime import datetime

import streamlit as st

from sunny_places.geocoding import fetch_nearby_places, search_places
from sunny_places.models import CandidatePlace, SearchResult, WeatherSnapshot
from sunny_places.weather import fetch_elevations, fetch_weather_snapshot


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
