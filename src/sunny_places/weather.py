from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

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
]


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

    response = requests.get(url, params=params, timeout=timeout_s)
    response.raise_for_status()
    return parse_weather_snapshot(response.json(), target_time)


def fetch_elevations(
    latitudes: list[float], longitudes: list[float], timeout_s: float = 18.0
) -> list[float]:
    response = requests.get(
        ELEVATION_URL,
        params={
            "latitude": ",".join(f"{latitude:.6f}" for latitude in latitudes),
            "longitude": ",".join(f"{longitude:.6f}" for longitude in longitudes),
        },
        timeout=timeout_s,
    )
    response.raise_for_status()
    elevations = response.json().get("elevation", [])
    return [float(value) for value in elevations]
