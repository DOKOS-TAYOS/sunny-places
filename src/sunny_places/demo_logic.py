from __future__ import annotations

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


def format_data_error_message(base_message: str, error: Exception) -> str:
    lowered = str(error).lower()
    if "429" in lowered or "too many requests" in lowered or "rate limit" in lowered:
        return f"{base_message} Please try again in a moment."
    if "timeout" in lowered:
        return f"{base_message} The providers took too long to respond."
    return base_message
