from __future__ import annotations

from sunny_places.models import CandidatePlace

RELAX_FRIENDLY_CATEGORIES = {
    "park",
    "garden",
    "nature_reserve",
    "viewpoint",
    "picnic_site",
    "attraction",
    "beach",
    "wood",
    "scrub",
    "grassland",
    "peak",
    "meadow",
    "grass",
    "recreation_ground",
    "marketplace",
    "fountain",
    "bench",
    "shelter",
    "pedestrian",
    "footway",
    "path",
    "square",
    "neighbourhood",
    "suburb",
    "quarter",
    "locality",
}


def _rankable_places(places: list[CandidatePlace], top_n: int) -> list[CandidatePlace]:
    relax_friendly = [place for place in places if place.category in RELAX_FRIENDLY_CATEGORIES]
    if len(relax_friendly) >= top_n:
        return relax_friendly
    return places


def split_ranked_places(
    places: list[CandidatePlace], top_n: int = 5
) -> tuple[list[CandidatePlace], list[CandidatePlace]]:
    rankable = _rankable_places(places, top_n)
    ranked = sorted(rankable, key=lambda place: place.score, reverse=True)
    sunny = ranked[:top_n]
    shady = sorted(rankable, key=lambda place: place.score)[:top_n]
    return sunny, shady
