from datetime import UTC, datetime

from sunny_places.models import WeatherSnapshot
from sunny_places.solar import calculate_solar_position, calculate_sun_score


def test_midday_has_higher_score_than_sunrise_for_same_weather() -> None:
    weather = WeatherSnapshot(
        cloud_cover=10.0,
        shortwave_radiation=800.0,
        direct_radiation=650.0,
        diffuse_radiation=120.0,
        direct_normal_irradiance=850.0,
    )

    sunrise = datetime(2026, 6, 21, 5, 0, tzinfo=UTC)
    midday = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)

    sunrise_score = calculate_sun_score(
        43.2630, -2.9350, sunrise, weather, slope_deg=0, aspect_deg=180
    )
    midday_score = calculate_sun_score(
        43.2630, -2.9350, midday, weather, slope_deg=0, aspect_deg=180
    )

    assert midday_score > sunrise_score


def test_night_time_returns_zero_score() -> None:
    weather = WeatherSnapshot(
        cloud_cover=0.0,
        shortwave_radiation=0.0,
        direct_radiation=0.0,
        diffuse_radiation=0.0,
        direct_normal_irradiance=0.0,
    )

    night = datetime(2026, 6, 21, 1, 0, tzinfo=UTC)

    assert calculate_sun_score(43.2630, -2.9350, night, weather, slope_deg=0, aspect_deg=180) == 0.0


def test_cloudier_conditions_reduce_sun_score() -> None:
    clear_weather = WeatherSnapshot(
        cloud_cover=5.0,
        shortwave_radiation=900.0,
        direct_radiation=700.0,
        diffuse_radiation=100.0,
        direct_normal_irradiance=900.0,
    )
    cloudy_weather = WeatherSnapshot(
        cloud_cover=95.0,
        shortwave_radiation=250.0,
        direct_radiation=60.0,
        diffuse_radiation=190.0,
        direct_normal_irradiance=100.0,
    )
    instant = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)

    clear_score = calculate_sun_score(
        43.2630, -2.9350, instant, clear_weather, slope_deg=0, aspect_deg=180
    )
    cloudy_score = calculate_sun_score(
        43.2630, -2.9350, instant, cloudy_weather, slope_deg=0, aspect_deg=180
    )

    assert clear_score > cloudy_score


def test_calculate_solar_position_returns_daylight_elevation() -> None:
    midday = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)

    position = calculate_solar_position(43.2630, -2.9350, midday)

    assert position.elevation_deg > 0
    assert 0 <= position.azimuth_deg <= 360
