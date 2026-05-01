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


def is_sample_key(selected_key: str | None) -> bool:
    return isinstance(selected_key, str) and selected_key.startswith("sample-")


def determine_map_click_action(
    clicked_key: str | None,
    pending_precise_sample_key: str | None,
) -> str:
    if not clicked_key:
        return "recenter"
    if not is_sample_key(clicked_key):
        return "select_object"
    if pending_precise_sample_key == clicked_key:
        return "recenter"
    return "arm_sample"


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


def _derive_sample_cell_half_deltas(samples: list[SamplePoint]) -> tuple[float, float]:
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


def find_clicked_sample_key(
    samples: list[SamplePoint],
    clicked_coordinates: tuple[float, float] | None,
) -> str | None:
    if clicked_coordinates is None or not samples:
        return None

    clicked_latitude, clicked_longitude = clicked_coordinates
    latitude_delta, longitude_delta = _derive_sample_cell_half_deltas(samples)
    for sample in samples:
        if (
            abs(clicked_latitude - sample.latitude) <= latitude_delta
            and abs(clicked_longitude - sample.longitude) <= longitude_delta
        ):
            return build_sample_key(sample)
    return None


def extract_selected_key_from_map_event(event: dict[str, object] | None) -> str | None:
    if not event:
        return None

    popup_value = event.get("last_object_clicked_popup")
    if not isinstance(popup_value, str):
        return None
    match = re.search(r"place_key=([A-Za-z0-9._:-]+)", popup_value)
    if match is None:
        return None
    return match.group(1)


def extract_clicked_coordinates(event: dict[str, object] | None) -> tuple[float, float] | None:
    if not event:
        return None
    for key in ("last_object_clicked", "last_clicked"):
        clicked = event.get(key)
        if not isinstance(clicked, dict):
            continue
        latitude = clicked.get("lat")
        longitude = clicked.get("lng")
        if isinstance(latitude, int | float) and isinstance(longitude, int | float):
            return float(latitude), float(longitude)
    return None
