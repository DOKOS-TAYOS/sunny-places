from __future__ import annotations

import re

from sunny_places.models import CandidatePlace, SamplePoint


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return cleaned.strip("-") or "place"


def build_place_key(place: CandidatePlace) -> str:
    return f"{place.category}-{place.latitude:.6f}-{place.longitude:.6f}-{slugify(place.name)}"


def build_sample_key(sample: SamplePoint) -> str:
    return f"sample-{sample.latitude:.6f}-{sample.longitude:.6f}"


def find_place_by_key(
    places: list[CandidatePlace],
    selected_key: str | None,
) -> CandidatePlace | None:
    if not selected_key:
        return None
    for place in places:
        if build_place_key(place) == selected_key:
            return place
    return None


def find_sample_by_key(
    samples: list[SamplePoint],
    selected_key: str | None,
) -> SamplePoint | None:
    if not selected_key:
        return None
    for sample in samples:
        if build_sample_key(sample) == selected_key:
            return sample
    return None


def extract_selected_key_from_map_event(event: dict[str, object] | None) -> str | None:
    if not event:
        return None

    popup_value = event.get("last_object_clicked_popup")
    if not isinstance(popup_value, str):
        return None
    marker = "place_key="
    if marker not in popup_value:
        return None
    return popup_value.split(marker, maxsplit=1)[1].strip()


def extract_clicked_coordinates(event: dict[str, object] | None) -> tuple[float, float] | None:
    if not event:
        return None
    clicked = event.get("last_clicked")
    if not isinstance(clicked, dict):
        return None
    latitude = clicked.get("lat")
    longitude = clicked.get("lng")
    if isinstance(latitude, int | float) and isinstance(longitude, int | float):
        return float(latitude), float(longitude)
    return None
