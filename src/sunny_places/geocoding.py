from __future__ import annotations

from typing import Any

import requests

from sunny_places.models import CandidatePlace, SearchResult
from sunny_places.sampling import great_circle_distance_m

USER_AGENT = "SunnyPlaces/0.1 (public-streamlit-app)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def parse_search_results(payload: list[dict[str, Any]]) -> list[SearchResult]:
    results: list[SearchResult] = []
    for item in payload:
        name = str(item.get("display_name", "")).strip()
        lat = item.get("lat")
        lon = item.get("lon")
        if not name or lat is None or lon is None:
            continue
        results.append(SearchResult(name=name, latitude=float(lat), longitude=float(lon)))
    return results


def parse_nearby_places(payload: dict[str, Any]) -> list[CandidatePlace]:
    places: list[CandidatePlace] = []
    seen: set[tuple[str, float, float]] = set()
    for element in payload.get("elements", []):
        tags = element.get("tags", {})
        name = str(tags.get("name", "")).strip()
        if not name:
            continue

        latitude = element.get("lat")
        longitude = element.get("lon")
        if latitude is None or longitude is None:
            center = element.get("center", {})
            latitude = center.get("lat")
            longitude = center.get("lon")
        if latitude is None or longitude is None:
            continue

        category = (
            tags.get("leisure")
            or tags.get("tourism")
            or tags.get("natural")
            or tags.get("place")
            or "place"
        )
        key = (name, round(float(latitude), 6), round(float(longitude), 6))
        if key in seen:
            continue
        seen.add(key)
        places.append(
            CandidatePlace(
                name=name,
                latitude=float(latitude),
                longitude=float(longitude),
                category=str(category),
                score=0.0,
            )
        )
    return places


def search_places(query: str, limit: int = 5, timeout_s: float = 12.0) -> list[SearchResult]:
    response = requests.get(
        NOMINATIM_URL,
        params={"q": query, "format": "jsonv2", "limit": limit},
        headers={"User-Agent": USER_AGENT},
        timeout=timeout_s,
    )
    response.raise_for_status()
    return parse_search_results(response.json())


def build_overpass_query(latitude: float, longitude: float, radius_m: float) -> str:
    radius = int(radius_m)
    return f"""
    [out:json][timeout:25];
    (
      nwr(around:{radius},{latitude},{longitude})[name][leisure~"park|garden|nature_reserve|pitch|playground"];
      nwr(around:{radius},{latitude},{longitude})[name][tourism~"viewpoint|picnic_site|attraction"];
      nwr(around:{radius},{latitude},{longitude})[name][natural~"beach|wood|scrub|grassland|peak"];
      nwr(around:{radius},{latitude},{longitude})[name][landuse~"meadow|grass|recreation_ground"];
      nwr(around:{radius},{latitude},{longitude})[name][amenity~"marketplace|fountain|bench|shelter"];
      nwr(around:{radius},{latitude},{longitude})[name][highway~"pedestrian|footway"];
    );
    out center;
    """


def fetch_nearby_places(
    latitude: float, longitude: float, radius_m: float, timeout_s: float = 18.0
) -> list[CandidatePlace]:
    query = build_overpass_query(latitude, longitude, radius_m)
    last_error: Exception | None = None
    places: list[CandidatePlace] = []
    for overpass_url in OVERPASS_URLS:
        try:
            response = requests.post(
                overpass_url,
                data=query.encode("utf-8"),
                headers={"User-Agent": USER_AGENT, "Content-Type": "text/plain"},
                timeout=timeout_s,
            )
            response.raise_for_status()
            places = parse_nearby_places(response.json())
            if places:
                break
        except requests.RequestException as exc:
            last_error = exc

    if not places and last_error is not None:
        raise last_error

    for place in places:
        place.distance_m = round(
            great_circle_distance_m(latitude, longitude, place.latitude, place.longitude), 1
        )
    return sorted(places, key=lambda place: place.distance_m or 0.0)
