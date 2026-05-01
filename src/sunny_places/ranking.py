from __future__ import annotations

from sunny_places.models import CandidatePlace


def split_ranked_places(
    places: list[CandidatePlace], top_n: int = 5
) -> tuple[list[CandidatePlace], list[CandidatePlace]]:
    ranked = sorted(places, key=lambda place: place.score, reverse=True)
    sunny = ranked[:top_n]
    shady = sorted(places, key=lambda place: place.score)[:top_n]
    return sunny, shady
