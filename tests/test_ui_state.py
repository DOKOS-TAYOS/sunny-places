from sunny_places.models import CandidatePlace
from sunny_places.ui_state import (
    build_place_key,
    build_sample_key,
    determine_map_click_action,
    extract_clicked_coordinates,
    extract_selected_key_from_map_event,
    find_clicked_sample_key,
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


def test_extract_selected_key_from_map_event_strips_trailing_html() -> None:
    event = {
        "last_object_clicked_popup": (
            "<div>Score: 42.0<br/><span style='display:none'>"
            "place_key=sample-43.264000--2.944000</span></div>"
        ),
    }

    assert extract_selected_key_from_map_event(event) == "sample-43.264000--2.944000"


def test_extract_clicked_coordinates_reads_last_clicked_point() -> None:
    event = {"last_clicked": {"lat": 43.264, "lng": -2.944}}

    assert extract_clicked_coordinates(event) == (43.264, -2.944)


def test_extract_clicked_coordinates_prefers_last_object_clicked_point() -> None:
    event = {
        "last_clicked": {"lat": 43.264, "lng": -2.944},
        "last_object_clicked": {"lat": 43.265, "lng": -2.945},
    }

    assert extract_clicked_coordinates(event) == (43.265, -2.945)


def test_find_sample_by_key_returns_matching_sample() -> None:
    from sunny_places.models import SamplePoint

    first = SamplePoint(latitude=43.26, longitude=-2.93, distance_m=10.0, score=11.0)
    second = SamplePoint(latitude=43.27, longitude=-2.94, distance_m=20.0, score=22.0)

    selected = find_sample_by_key([first, second], build_sample_key(second))

    assert selected is second


def test_determine_map_click_action_arms_first_sample_click() -> None:
    assert determine_map_click_action("sample-43.264000--2.944000", None) == "arm_sample"


def test_determine_map_click_action_recenters_on_second_sample_click() -> None:
    assert (
        determine_map_click_action(
            "sample-43.264000--2.944000",
            "sample-43.264000--2.944000",
        )
        == "recenter"
    )


def test_determine_map_click_action_recenters_background_click() -> None:
    assert determine_map_click_action(None, "sample-43.264000--2.944000") == "recenter"


def test_find_clicked_sample_key_detects_click_inside_sample_cell() -> None:
    from sunny_places.models import SamplePoint

    samples = [
        SamplePoint(latitude=43.2640, longitude=-2.9440, distance_m=0.0, score=10.0),
        SamplePoint(latitude=43.2640, longitude=-2.9420, distance_m=100.0, score=20.0),
        SamplePoint(latitude=43.2620, longitude=-2.9440, distance_m=100.0, score=30.0),
    ]

    clicked_key = find_clicked_sample_key(samples, (43.2643, -2.9437))

    assert clicked_key == "sample-43.264000--2.944000"


def test_find_clicked_sample_key_returns_none_outside_heatmap_cells() -> None:
    from sunny_places.models import SamplePoint

    samples = [
        SamplePoint(latitude=43.2640, longitude=-2.9440, distance_m=0.0, score=10.0),
        SamplePoint(latitude=43.2640, longitude=-2.9420, distance_m=100.0, score=20.0),
        SamplePoint(latitude=43.2620, longitude=-2.9440, distance_m=100.0, score=30.0),
    ]

    clicked_key = find_clicked_sample_key(samples, (43.2600, -2.9500))

    assert clicked_key is None
