from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GeoPoint:
    latitude: float
    longitude: float


@dataclass(slots=True)
class SearchResult:
    name: str
    latitude: float
    longitude: float


@dataclass(slots=True)
class WeatherSnapshot:
    cloud_cover: float
    shortwave_radiation: float
    direct_radiation: float
    diffuse_radiation: float
    direct_normal_irradiance: float
    wind_speed_10m: float = 0.0
    wind_gusts_10m: float = 0.0
    wind_direction_10m: float = 0.0
    timezone_name: str = "UTC"
    utc_offset_seconds: int = 0


@dataclass(slots=True)
class SolarPosition:
    elevation_deg: float
    azimuth_deg: float


@dataclass(slots=True)
class SamplePoint:
    latitude: float
    longitude: float
    distance_m: float
    elevation_m: float | None = None
    slope_deg: float = 0.0
    aspect_deg: float = 180.0
    sun_score: float | None = None
    wind_score: float | None = None
    score: float | None = None


@dataclass(slots=True)
class CandidatePlace:
    name: str
    latitude: float
    longitude: float
    category: str
    score: float
    distance_m: float | None = None
    metadata: dict[str, float | str] = field(default_factory=dict)


@dataclass(slots=True)
class AnalysisBasePayload:
    samples: list[SamplePoint]
    places: list[CandidatePlace]
    weather_snapshot: WeatherSnapshot
    warnings: list[str]
