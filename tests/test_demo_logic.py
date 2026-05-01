from sunny_places.demo_logic import (
    build_fallback_places,
    compute_grid_size_for_radius,
    compute_zoom_for_radius,
    format_data_error_message,
)
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
        retry_message="Please try again in a moment.",
        timeout_message="The providers took too long to respond.",
    )

    assert message == "Some external data could not be loaded. Please try again in a moment."


def test_format_data_error_message_can_return_localized_timeout_message() -> None:
    message = format_data_error_message(
        "No se pudieron cargar algunos datos externos.",
        RuntimeError("Request timeout from upstream provider"),
        retry_message="Vuelve a intentarlo dentro de un momento.",
        timeout_message="Los proveedores han tardado demasiado en responder.",
    )

    assert (
        message == "No se pudieron cargar algunos datos externos. "
        "Los proveedores han tardado demasiado en responder."
    )


def test_compute_grid_size_for_radius_keeps_cells_at_or_below_200m() -> None:
    grid_size = compute_grid_size_for_radius(5000.0)

    assert grid_size == 51
    assert (2 * 5000.0) / (grid_size - 1) <= 200.0


def test_compute_grid_size_for_radius_returns_odd_grid() -> None:
    grid_size = compute_grid_size_for_radius(20.0)

    assert grid_size == 11
    assert grid_size % 2 == 1


def test_compute_grid_size_for_radius_keeps_minimum_visual_density() -> None:
    grid_size = compute_grid_size_for_radius(400.0)

    assert grid_size == 11


def test_compute_zoom_for_radius_zooms_out_for_larger_radius() -> None:
    close_zoom = compute_zoom_for_radius(100.0, latitude=43.263)
    far_zoom = compute_zoom_for_radius(5000.0, latitude=43.263)

    assert close_zoom > far_zoom


def test_compute_zoom_for_radius_stays_within_leaflet_bounds() -> None:
    zoom = compute_zoom_for_radius(100.0, latitude=43.263)

    assert 1 <= zoom <= 18
