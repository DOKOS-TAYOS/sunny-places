from __future__ import annotations

from math import cos, radians

from sunny_places.models import WeatherSnapshot


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _smallest_relative_angle(angle_a: float, angle_b: float) -> float:
    return abs(((angle_a - angle_b + 180.0) % 360.0) - 180.0)


def calculate_wind_score(
    weather: WeatherSnapshot,
    slope_deg: float,
    aspect_deg: float,
) -> float:
    base_wind = 0.72 * weather.wind_speed_10m + 0.28 * weather.wind_gusts_10m
    relative_angle = _smallest_relative_angle(weather.wind_direction_10m, aspect_deg)
    directional_exposure = 0.78 + 0.34 * max(cos(radians(relative_angle)), -0.55)
    slope_boost = 1.0 + 0.18 * clamp(slope_deg / 25.0, 0.0, 1.0)
    score = base_wind * directional_exposure * slope_boost
    return round(max(score, 0.0), 2)
