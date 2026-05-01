from sunny_places.sampling import SamplePoint, generate_sample_grid


def test_generate_sample_grid_stays_inside_radius() -> None:
    samples = generate_sample_grid(43.2630, -2.9350, radius_m=500, grid_size=7)

    assert len(samples) > 0
    assert all(sample.distance_m <= 500 for sample in samples)


def test_generate_sample_grid_contains_center_point() -> None:
    samples = generate_sample_grid(43.2630, -2.9350, radius_m=500, grid_size=7)

    assert any(
        abs(sample.latitude - 43.2630) < 1e-9 and abs(sample.longitude + 2.9350) < 1e-9
        for sample in samples
    )


def test_sample_point_has_typed_score_slot() -> None:
    point = SamplePoint(latitude=43.2630, longitude=-2.9350, distance_m=0)

    assert point.score is None
