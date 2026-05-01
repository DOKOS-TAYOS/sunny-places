from sunny_places.models import CandidatePlace
from sunny_places.ui_state import (
    build_place_key,
    build_sample_key,
    extract_clicked_coordinates,
    extract_selected_key_from_map_event,
    find_place_by_key,
    find_sample_by_key,
)


def test_build_place_key_is_stable_for_same_place() -> None:
    place = CandidatePlace(
        name="Doña Casilda Park",
        latitude=43.264,
        longitude=-2.944,
        category="park",
        score=77.0,
    )

    assert build_place_key(place) == build_place_key(place)


def test_find_place_by_key_returns_matching_place() -> None:
    first = CandidatePlace(name="A", latitude=1.0, longitude=2.0, category="park", score=20.0)
    second = CandidatePlace(name="B", latitude=3.0, longitude=4.0, category="park", score=40.0)

    selected = find_place_by_key([first, second], build_place_key(second))

    assert selected is second


def test_extract_selected_key_from_map_event_reads_leaflet_popup_payload() -> None:
    event = {
        "last_object_clicked_popup": "place_key=park-43.264000--2.944000-dona-casilda-park",
    }

    assert (
        extract_selected_key_from_map_event(event) == "park-43.264000--2.944000-dona-casilda-park"
    )


def test_extract_clicked_coordinates_reads_last_clicked_point() -> None:
    event = {"last_clicked": {"lat": 43.264, "lng": -2.944}}

    assert extract_clicked_coordinates(event) == (43.264, -2.944)


def test_find_sample_by_key_returns_matching_sample() -> None:
    from sunny_places.models import SamplePoint

    first = SamplePoint(latitude=43.26, longitude=-2.93, distance_m=10.0, score=11.0)
    second = SamplePoint(latitude=43.27, longitude=-2.94, distance_m=20.0, score=22.0)

    selected = find_sample_by_key([first, second], build_sample_key(second))

    assert selected is second
