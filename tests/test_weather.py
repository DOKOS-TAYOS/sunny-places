import pytest
import requests

from sunny_places.weather import (
    _get_with_ssl_fallback,
    get_request_verify_path,
    parse_weather_snapshot,
    split_coordinate_batches,
)


def test_parse_weather_snapshot_extracts_requested_hour() -> None:
    payload = {
        "hourly": {
            "time": ["2026-05-01T10:00", "2026-05-01T11:00"],
            "cloud_cover": [40.0, 20.0],
            "shortwave_radiation": [500.0, 700.0],
            "direct_radiation": [200.0, 450.0],
            "diffuse_radiation": [130.0, 110.0],
            "direct_normal_irradiance": [300.0, 700.0],
            "wind_speed_10m": [12.0, 18.0],
            "wind_gusts_10m": [20.0, 28.0],
            "wind_direction_10m": [90.0, 120.0],
        }
    }

    snapshot = parse_weather_snapshot(payload, "2026-05-01T11:00")

    assert snapshot.cloud_cover == 20.0
    assert snapshot.direct_normal_irradiance == 700.0
    assert snapshot.wind_speed_10m == 18.0
    assert snapshot.wind_gusts_10m == 28.0


def test_get_request_verify_path_returns_certificate_bundle() -> None:
    verify_path = get_request_verify_path()

    assert verify_path
    assert verify_path.endswith(".pem")


def test_get_with_ssl_fallback_does_not_retry_with_disabled_tls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verify_values: list[str | bool] = []

    def fake_get(
        url: str,
        *,
        params: dict[str, str | float],
        timeout: float,
        verify: str | bool,
    ) -> requests.Response:
        verify_values.append(verify)
        raise requests.exceptions.SSLError("certificate verify failed")

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(requests.exceptions.SSLError):
        _get_with_ssl_fallback(
            "https://example.invalid",
            params={"latitude": 43.0},
            timeout_s=1.0,
        )

    assert verify_values == [get_request_verify_path()]


def test_split_coordinate_batches_limits_batch_size() -> None:
    latitudes = [float(index) for index in range(205)]
    longitudes = [float(index) for index in range(205)]

    batches = split_coordinate_batches(latitudes, longitudes, max_batch_size=100)

    assert [len(batch[0]) for batch in batches] == [100, 100, 5]
    assert [len(batch[1]) for batch in batches] == [100, 100, 5]
