from datetime import UTC, datetime

from sunny_places.models import CandidatePlace, SamplePoint, SearchResult, WeatherSnapshot
from sunny_places.services import (
    cached_compute_analysis_base,
    cached_fetch_weather_snapshot,
    cached_search_places,
)


def test_cached_search_places_returns_stable_results(monkeypatch: object) -> None:
    call_counter = {"count": 0}

    def fake_search_places(query: str, limit: int = 5) -> list[SearchResult]:
        call_counter["count"] += 1
        return [SearchResult(name=f"{query}-{limit}", latitude=43.263, longitude=-2.935)]

    monkeypatch.setattr("sunny_places.services.search_places", fake_search_places)
    cached_search_places.clear()

    first = cached_search_places("Bilbao", limit=3)
    second = cached_search_places("Bilbao", limit=3)

    assert first[0].name == "Bilbao-3"
    assert second[0].name == "Bilbao-3"
    assert call_counter["count"] == 1


def test_cached_fetch_weather_snapshot_returns_stable_snapshot(monkeypatch: object) -> None:
    call_counter = {"count": 0}

    def fake_fetch_weather_snapshot(
        latitude: float,
        longitude: float,
        target_datetime: datetime,
    ) -> WeatherSnapshot:
        call_counter["count"] += 1
        return WeatherSnapshot(
            cloud_cover=10.0,
            shortwave_radiation=700.0,
            direct_radiation=500.0,
            diffuse_radiation=110.0,
            direct_normal_irradiance=760.0,
            utc_offset_seconds=3600,
        )

    monkeypatch.setattr(
        "sunny_places.services.fetch_weather_snapshot",
        fake_fetch_weather_snapshot,
    )
    cached_fetch_weather_snapshot.clear()

    target_datetime = datetime(2026, 5, 1, 15, 0, tzinfo=UTC)
    first = cached_fetch_weather_snapshot(43.263, -2.935, target_datetime)
    second = cached_fetch_weather_snapshot(43.263, -2.935, target_datetime)

    assert first.direct_radiation == 500.0
    assert second.utc_offset_seconds == 3600
    assert call_counter["count"] == 1


def test_cached_compute_analysis_base_reuses_full_analysis(monkeypatch: object) -> None:
    call_counter = {
        "grid": 0,
        "elevations": 0,
        "weather": 0,
        "places": 0,
        "sun": 0,
        "wind": 0,
    }

    def fake_generate_sample_grid(
        latitude: float,
        longitude: float,
        radius_m: float,
        grid_size: int = 9,
    ) -> list[SamplePoint]:
        _ = radius_m
        _ = grid_size
        call_counter["grid"] += 1
        return [SamplePoint(latitude=latitude, longitude=longitude, distance_m=0.0)]

    def fake_cached_fetch_elevations(
        latitudes: tuple[float, ...],
        longitudes: tuple[float, ...],
    ) -> list[float]:
        _ = latitudes
        _ = longitudes
        call_counter["elevations"] += 1
        return [12.0]

    def fake_apply_terrain_metrics(samples: list[SamplePoint]) -> list[SamplePoint]:
        return samples

    def fake_cached_fetch_weather_snapshot(
        latitude: float,
        longitude: float,
        target_datetime: datetime,
    ) -> WeatherSnapshot:
        _ = latitude
        _ = longitude
        _ = target_datetime
        call_counter["weather"] += 1
        return WeatherSnapshot(
            cloud_cover=10.0,
            shortwave_radiation=700.0,
            direct_radiation=500.0,
            diffuse_radiation=110.0,
            direct_normal_irradiance=760.0,
            utc_offset_seconds=3600,
        )

    def fake_calculate_sun_score(
        latitude: float,
        longitude: float,
        localized_datetime: datetime,
        weather_snapshot: WeatherSnapshot,
        slope_deg: float = 0.0,
        aspect_deg: float = 180.0,
    ) -> float:
        _ = latitude, longitude, localized_datetime, weather_snapshot, slope_deg, aspect_deg
        call_counter["sun"] += 1
        return 60.0

    def fake_calculate_wind_score(
        weather_snapshot: WeatherSnapshot,
        slope_deg: float = 0.0,
        aspect_deg: float = 180.0,
    ) -> float:
        _ = weather_snapshot, slope_deg, aspect_deg
        call_counter["wind"] += 1
        return 30.0

    def fake_cached_fetch_nearby_places(
        latitude: float,
        longitude: float,
        radius_m: float,
    ) -> list[CandidatePlace]:
        _ = latitude, longitude, radius_m
        call_counter["places"] += 1
        return [
            CandidatePlace(
                name="Parque",
                latitude=43.263,
                longitude=-2.935,
                category="park",
                score=0.0,
            )
        ]

    monkeypatch.setattr("sunny_places.services.generate_sample_grid", fake_generate_sample_grid)
    monkeypatch.setattr(
        "sunny_places.services.cached_fetch_elevations", fake_cached_fetch_elevations
    )
    monkeypatch.setattr("sunny_places.services.apply_terrain_metrics", fake_apply_terrain_metrics)
    monkeypatch.setattr(
        "sunny_places.services.cached_fetch_weather_snapshot",
        fake_cached_fetch_weather_snapshot,
    )
    monkeypatch.setattr("sunny_places.services.calculate_sun_score", fake_calculate_sun_score)
    monkeypatch.setattr("sunny_places.services.calculate_wind_score", fake_calculate_wind_score)
    monkeypatch.setattr(
        "sunny_places.services.cached_fetch_nearby_places",
        fake_cached_fetch_nearby_places,
    )
    cached_compute_analysis_base.clear()

    first = cached_compute_analysis_base(43.263, -2.935, "2026-05-01T15:00:00", 1200.0)
    second = cached_compute_analysis_base(43.263, -2.935, "2026-05-01T15:00:00", 1200.0)

    assert len(first.samples) == 1
    assert len(second.places) == 1
    assert first.samples[0].sun_score == 60.0
    assert second.samples[0].wind_score == 30.0
    assert call_counter == {
        "grid": 1,
        "elevations": 1,
        "weather": 1,
        "places": 1,
        "sun": 1,
        "wind": 1,
    }
