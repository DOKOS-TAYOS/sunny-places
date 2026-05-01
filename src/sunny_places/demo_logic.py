from __future__ import annotations

from math import ceil, cos, floor, log2, radians

from sunny_places.models import CandidatePlace, SamplePoint


def build_fallback_places(
    samples: list[SamplePoint],
    prefix_label: str,
    limit: int = 10,
) -> list[CandidatePlace]:
    sorted_samples = sorted(samples, key=lambda point: point.score or 0.0, reverse=True)[:limit]
    places: list[CandidatePlace] = []
    for index, sample in enumerate(sorted_samples, start=1):
        places.append(
            CandidatePlace(
                name=f"{prefix_label} {index}",
                latitude=sample.latitude,
                longitude=sample.longitude,
                category="sample",
                score=sample.score or 0.0,
                distance_m=sample.distance_m,
                metadata={"source": "fallback_sample"},
            )
        )
    return places


def compute_grid_size_for_radius(radius_m: float, max_cell_side_m: float = 200.0) -> int:
    interval_count = max(2, ceil((2 * radius_m) / max_cell_side_m))
    interval_count = max(interval_count, 10)
    if interval_count % 2 == 1:
        interval_count += 1
    return interval_count + 1


def compute_zoom_for_radius(
    radius_m: float,
    latitude: float,
    viewport_width_px: int = 900,
    padding_factor: float = 1.35,
) -> int:
    safe_radius_m = max(radius_m, 1.0)
    visible_width_m = safe_radius_m * 2 * padding_factor
    meters_per_pixel = visible_width_m / viewport_width_px
    latitude_factor = max(cos(radians(latitude)), 0.2)
    zoom = log2((156543.03392 * latitude_factor) / meters_per_pixel)
    return max(1, min(18, floor(zoom)))


def format_data_error_message(
    base_message: str,
    error: Exception,
    retry_message: str,
    timeout_message: str,
) -> str:
    lowered = str(error).lower()
    if "429" in lowered or "too many requests" in lowered or "rate limit" in lowered:
        return f"{base_message} {retry_message}"
    if "timeout" in lowered:
        return f"{base_message} {timeout_message}"
    return base_message
