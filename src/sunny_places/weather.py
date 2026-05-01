from __future__ import annotations

from datetime import datetime
from typing import Any

import requests
import urllib3

from sunny_places.models import WeatherSnapshot

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"

WEATHER_FIELDS = [
    "cloud_cover",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
]


def get_request_verify_path() -> str:
    return requests.certs.where()


def split_coordinate_batches(
    latitudes: list[float],
    longitudes: list[float],
    max_batch_size: int = 100,
) -> list[tuple[list[float], list[float]]]:
    batches: list[tuple[list[float], list[float]]] = []
    for start_index in range(0, len(latitudes), max_batch_size):
        end_index = start_index + max_batch_size
        batches.append((latitudes[start_index:end_index], longitudes[start_index:end_index]))
    return batches


def _get_with_ssl_fallback(
    url: str,
    *,
    params: dict[str, str | float],
    timeout_s: float,
) -> requests.Response:
    try:
        return requests.get(
            url,
            params=params,
            timeout=timeout_s,
            verify=get_request_verify_path(),
        )
    except requests.exceptions.SSLError:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.get(
            url,
            params=params,
            timeout=timeout_s,
            verify=False,
        )


def parse_weather_snapshot(payload: dict[str, Any], target_time: str) -> WeatherSnapshot:
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    if target_time not in times:
        raise ValueError(f"Target time {target_time} is not present in weather payload")

    index = times.index(target_time)
    return WeatherSnapshot(
        cloud_cover=float(hourly["cloud_cover"][index]),
        shortwave_radiation=float(hourly["shortwave_radiation"][index]),
        direct_radiation=float(hourly["direct_radiation"][index]),
        diffuse_radiation=float(hourly["diffuse_radiation"][index]),
        direct_normal_irradiance=float(hourly["direct_normal_irradiance"][index]),
        wind_speed_10m=float(hourly["wind_speed_10m"][index]),
        wind_gusts_10m=float(hourly["wind_gusts_10m"][index]),
        wind_direction_10m=float(hourly["wind_direction_10m"][index]),
        timezone_name=str(payload.get("timezone", "UTC")),
        utc_offset_seconds=int(payload.get("utc_offset_seconds", 0)),
    )


def build_hour_key(target_datetime: datetime) -> str:
    return target_datetime.strftime("%Y-%m-%dT%H:00")


def fetch_weather_snapshot(
    latitude: float, longitude: float, target_datetime: datetime, timeout_s: float = 18.0
) -> WeatherSnapshot:
    target_date = target_datetime.date()
    today = datetime.utcnow().date()
    target_time = build_hour_key(target_datetime)

    params: dict[str, str | float] = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(WEATHER_FIELDS),
        "timezone": "auto",
    }

    if target_date < today:
        params["start_date"] = target_date.isoformat()
        params["end_date"] = target_date.isoformat()
        url = ARCHIVE_URL
    else:
        forecast_days = max(1, (target_date - today).days + 1)
        params["forecast_days"] = str(min(forecast_days, 16))
        url = FORECAST_URL

    response = _get_with_ssl_fallback(url, params=params, timeout_s=timeout_s)
    response.raise_for_status()
    return parse_weather_snapshot(response.json(), target_time)


def fetch_elevations(
    latitudes: list[float], longitudes: list[float], timeout_s: float = 18.0
) -> list[float]:
    elevations: list[float] = []
    for batch_latitudes, batch_longitudes in split_coordinate_batches(latitudes, longitudes):
        response = _get_with_ssl_fallback(
            ELEVATION_URL,
            params={
                "latitude": ",".join(f"{latitude:.6f}" for latitude in batch_latitudes),
                "longitude": ",".join(f"{longitude:.6f}" for longitude in batch_longitudes),
            },
            timeout_s=timeout_s,
        )
        response.raise_for_status()
        elevations.extend(float(value) for value in response.json().get("elevation", []))
    return elevations
