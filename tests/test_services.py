from datetime import UTC, datetime

from sunny_places.models import SearchResult, WeatherSnapshot
from sunny_places.services import cached_fetch_weather_snapshot, cached_search_places


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
