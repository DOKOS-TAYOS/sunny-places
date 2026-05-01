from sunny_places.weather import parse_weather_snapshot


def test_parse_weather_snapshot_extracts_requested_hour() -> None:
    payload = {
        "hourly": {
            "time": ["2026-05-01T10:00", "2026-05-01T11:00"],
            "cloud_cover": [40.0, 20.0],
            "shortwave_radiation": [500.0, 700.0],
            "direct_radiation": [200.0, 450.0],
            "diffuse_radiation": [130.0, 110.0],
            "direct_normal_irradiance": [300.0, 700.0],
        }
    }

    snapshot = parse_weather_snapshot(payload, "2026-05-01T11:00")

    assert snapshot.cloud_cover == 20.0
    assert snapshot.direct_normal_irradiance == 700.0
