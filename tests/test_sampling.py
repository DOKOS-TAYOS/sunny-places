from sunny_places.sampling import SamplePoint, apply_terrain_metrics, generate_sample_grid


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


def test_apply_terrain_metrics_computes_slope_on_trimmed_grid() -> None:
    samples = generate_sample_grid(43.2630, -2.9350, radius_m=500, grid_size=7)
    for sample in samples:
        sample.elevation_m = 100.0 + (sample.latitude * 10_000.0) + (sample.longitude * 4_000.0)

    enriched = apply_terrain_metrics(samples)

    non_zero_slopes = [sample.slope_deg for sample in enriched if sample.slope_deg > 0.0]
    assert non_zero_slopes
    center_sample = min(enriched, key=lambda sample: sample.distance_m)
    assert center_sample.slope_deg > 0.0
