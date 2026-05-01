from sunny_places.demo_logic import build_fallback_places, format_data_error_message
from sunny_places.models import SamplePoint


def test_build_fallback_places_creates_ranked_demo_points() -> None:
    samples = [
        SamplePoint(latitude=43.26, longitude=-2.93, distance_m=50.0, score=25.0),
        SamplePoint(latitude=43.27, longitude=-2.94, distance_m=80.0, score=80.0),
        SamplePoint(latitude=43.28, longitude=-2.95, distance_m=120.0, score=55.0),
    ]

    places = build_fallback_places(samples, prefix_label="Computed point")

    assert [place.name for place in places] == [
        "Computed point 1",
        "Computed point 2",
        "Computed point 3",
    ]
    assert [place.score for place in places] == [80.0, 55.0, 25.0]


def test_format_data_error_message_hides_raw_provider_exceptions() -> None:
    message = format_data_error_message(
        "Some external data could not be loaded.",
        RuntimeError("429 Too Many Requests from upstream provider"),
    )

    assert message == "Some external data could not be loaded. Please try again in a moment."
