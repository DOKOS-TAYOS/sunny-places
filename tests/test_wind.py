from sunny_places.models import WeatherSnapshot
from sunny_places.wind import calculate_wind_score


def test_stronger_wind_produces_higher_score() -> None:
    gentle = WeatherSnapshot(
        cloud_cover=0.0,
        shortwave_radiation=0.0,
        direct_radiation=0.0,
        diffuse_radiation=0.0,
        direct_normal_irradiance=0.0,
        wind_speed_10m=10.0,
        wind_gusts_10m=16.0,
        wind_direction_10m=90.0,
    )
    breezy = WeatherSnapshot(
        cloud_cover=0.0,
        shortwave_radiation=0.0,
        direct_radiation=0.0,
        diffuse_radiation=0.0,
        direct_normal_irradiance=0.0,
        wind_speed_10m=24.0,
        wind_gusts_10m=34.0,
        wind_direction_10m=90.0,
    )

    assert calculate_wind_score(breezy, slope_deg=5.0, aspect_deg=90.0) > calculate_wind_score(
        gentle,
        slope_deg=5.0,
        aspect_deg=90.0,
    )


def test_wind_score_changes_with_terrain_exposure() -> None:
    weather = WeatherSnapshot(
        cloud_cover=0.0,
        shortwave_radiation=0.0,
        direct_radiation=0.0,
        diffuse_radiation=0.0,
        direct_normal_irradiance=0.0,
        wind_speed_10m=24.0,
        wind_gusts_10m=34.0,
        wind_direction_10m=90.0,
    )

    exposed = calculate_wind_score(weather, slope_deg=18.0, aspect_deg=90.0)
    sheltered = calculate_wind_score(weather, slope_deg=18.0, aspect_deg=270.0)

    assert exposed > sheltered
