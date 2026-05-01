from __future__ import annotations

from datetime import datetime
from math import acos, atan2, cos, degrees, pi, radians, sin

from sunny_places.models import SolarPosition, WeatherSnapshot


def calculate_solar_position(latitude: float, longitude: float, instant: datetime) -> SolarPosition:
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("instant must be timezone-aware")

    day_of_year = instant.timetuple().tm_yday
    hour_decimal = (
        instant.hour
        + instant.minute / 60.0
        + instant.second / 3600.0
        + instant.microsecond / 3_600_000_000.0
    )
    gamma = 2.0 * pi / 365.0 * (day_of_year - 1 + (hour_decimal - 12.0) / 24.0)

    declination = (
        0.006918
        - 0.399912 * cos(gamma)
        + 0.070257 * sin(gamma)
        - 0.006758 * cos(2 * gamma)
        + 0.000907 * sin(2 * gamma)
        - 0.002697 * cos(3 * gamma)
        + 0.00148 * sin(3 * gamma)
    )
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * cos(gamma)
        - 0.032077 * sin(gamma)
        - 0.014615 * cos(2 * gamma)
        - 0.040849 * sin(2 * gamma)
    )

    timezone_offset_minutes = (instant.utcoffset() or instant.utcoffset()).total_seconds() / 60.0
    true_solar_time = (
        hour_decimal * 60.0 + equation_of_time + 4.0 * longitude - timezone_offset_minutes
    ) % 1440.0
    hour_angle_deg = true_solar_time / 4.0 - 180.0
    if hour_angle_deg < -180.0:
        hour_angle_deg += 360.0

    latitude_rad = radians(latitude)
    hour_angle_rad = radians(hour_angle_deg)

    cos_zenith = sin(latitude_rad) * sin(declination) + cos(latitude_rad) * cos(declination) * cos(
        hour_angle_rad
    )
    cos_zenith = min(1.0, max(-1.0, cos_zenith))
    zenith_rad = acos(cos_zenith)
    elevation_deg = 90.0 - degrees(zenith_rad)

    azimuth_rad = atan2(
        sin(hour_angle_rad),
        cos(hour_angle_rad) * sin(latitude_rad) - tan_safe(declination) * cos(latitude_rad),
    )
    azimuth_deg = (degrees(azimuth_rad) + 180.0) % 360.0

    return SolarPosition(elevation_deg=elevation_deg, azimuth_deg=azimuth_deg)


def tan_safe(value: float) -> float:
    return sin(value) / max(cos(value), 1e-9)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def calculate_sun_score(
    latitude: float,
    longitude: float,
    instant: datetime,
    weather: WeatherSnapshot,
    slope_deg: float,
    aspect_deg: float,
) -> float:
    position = calculate_solar_position(latitude, longitude, instant)
    if position.elevation_deg <= 0:
        return 0.0

    elevation_rad = radians(position.elevation_deg)
    azimuth_rad = radians(position.azimuth_deg)
    slope_rad = radians(slope_deg)
    aspect_rad = radians(aspect_deg)

    sun_east = cos(elevation_rad) * sin(azimuth_rad)
    sun_north = cos(elevation_rad) * cos(azimuth_rad)
    sun_up = sin(elevation_rad)

    normal_east = -sin(slope_rad) * sin(aspect_rad)
    normal_north = -sin(slope_rad) * cos(aspect_rad)
    normal_up = cos(slope_rad)

    incidence = max(0.0, sun_east * normal_east + sun_north * normal_north + sun_up * normal_up)
    base_clear_sky = max(0.0, sin(elevation_rad))

    direct_factor = clamp(weather.direct_normal_irradiance / 900.0, 0.0, 1.0)
    global_factor = clamp(weather.shortwave_radiation / 1000.0, 0.0, 1.0)
    diffuse_factor = clamp(weather.diffuse_radiation / 350.0, 0.0, 1.0)
    cloud_bonus = clamp(1.0 - weather.cloud_cover / 100.0, 0.0, 1.0)

    terrain_factor = 0.2 + 0.8 * incidence
    atmosphere_factor = clamp(
        0.45 * direct_factor + 0.25 * global_factor + 0.15 * diffuse_factor + 0.15 * cloud_bonus,
        0.0,
        1.0,
    )

    score = 100.0 * clamp(base_clear_sky * terrain_factor * atmosphere_factor, 0.0, 1.0)
    return round(score, 2)
