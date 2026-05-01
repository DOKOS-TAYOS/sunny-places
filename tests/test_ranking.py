from sunny_places.models import CandidatePlace
from sunny_places.ranking import split_ranked_places


def test_split_ranked_places_orders_descending_and_ascending() -> None:
    places = [
        CandidatePlace(name="A", latitude=0.0, longitude=0.0, category="park", score=20.0),
        CandidatePlace(name="B", latitude=0.0, longitude=0.0, category="park", score=80.0),
        CandidatePlace(name="C", latitude=0.0, longitude=0.0, category="park", score=50.0),
    ]

    sunny, shady = split_ranked_places(places, top_n=2)

    assert [place.name for place in sunny] == ["B", "C"]
    assert [place.name for place in shady] == ["A", "C"]


def test_split_ranked_places_prefers_relax_friendly_categories() -> None:
    places = [
        CandidatePlace(name="Bank", latitude=0.0, longitude=0.0, category="bank", score=90.0),
        CandidatePlace(name="Park", latitude=0.0, longitude=0.0, category="park", score=70.0),
        CandidatePlace(name="Square", latitude=0.0, longitude=0.0, category="square", score=60.0),
    ]

    sunny, shady = split_ranked_places(places, top_n=2)

    assert [place.name for place in sunny] == ["Park", "Square"]
