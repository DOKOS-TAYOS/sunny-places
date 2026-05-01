from __future__ import annotations

from math import atan2, cos, degrees, hypot, radians, sin, sqrt

from sunny_places.models import SamplePoint

EARTH_RADIUS_M = 6_371_000.0


def meters_to_latitude_delta(distance_m: float) -> float:
    return degrees(distance_m / EARTH_RADIUS_M)


def meters_to_longitude_delta(distance_m: float, latitude: float) -> float:
    latitude_cos = max(cos(radians(latitude)), 1e-6)
    return degrees(distance_m / (EARTH_RADIUS_M * latitude_cos))


def great_circle_distance_m(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    lat1 = radians(latitude_a)
    lon1 = radians(longitude_a)
    lat2 = radians(latitude_b)
    lon2 = radians(longitude_b)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    haversine = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(haversine), sqrt(max(1 - haversine, 0.0)))


def generate_sample_grid(
    latitude: float,
    longitude: float,
    radius_m: float,
    grid_size: int = 9,
) -> list[SamplePoint]:
    if grid_size < 3 or grid_size % 2 == 0:
        raise ValueError("grid_size must be an odd number greater than or equal to 3")

    step_m = (radius_m * 2) / (grid_size - 1)
    samples: list[SamplePoint] = []
    center_index = grid_size // 2

    for row_index in range(grid_size):
        north_m = (center_index - row_index) * step_m
        for column_index in range(grid_size):
            east_m = (column_index - center_index) * step_m
            distance_m = hypot(east_m, north_m)
            if distance_m > radius_m:
                continue

            sample_latitude = latitude + meters_to_latitude_delta(north_m)
            sample_longitude = longitude + meters_to_longitude_delta(east_m, latitude)
            samples.append(
                SamplePoint(
                    latitude=sample_latitude,
                    longitude=sample_longitude,
                    distance_m=round(distance_m, 6),
                )
            )
    return samples


def apply_terrain_metrics(samples: list[SamplePoint]) -> list[SamplePoint]:
    if not samples:
        return samples

    latitudes = sorted({sample.latitude for sample in samples}, reverse=True)
    longitudes = sorted({sample.longitude for sample in samples})
    if len(latitudes) < 3 or len(longitudes) < 3:
        return samples

    sample_lookup = {
        (round(sample.latitude, 10), round(sample.longitude, 10)): sample for sample in samples
    }

    if len(sample_lookup) < 5:
        return samples

    for row_index in range(1, len(latitudes) - 1):
        for column_index in range(1, len(longitudes) - 1):
            center = sample_lookup.get(
                (round(latitudes[row_index], 10), round(longitudes[column_index], 10))
            )
            west = sample_lookup.get(
                (round(latitudes[row_index], 10), round(longitudes[column_index - 1], 10))
            )
            east = sample_lookup.get(
                (round(latitudes[row_index], 10), round(longitudes[column_index + 1], 10))
            )
            north = sample_lookup.get(
                (round(latitudes[row_index - 1], 10), round(longitudes[column_index], 10))
            )
            south = sample_lookup.get(
                (round(latitudes[row_index + 1], 10), round(longitudes[column_index], 10))
            )

            if any(point is None for point in (center, west, east, north, south)):
                continue

            assert center is not None
            assert west is not None
            assert east is not None
            assert north is not None
            assert south is not None

            elevations = (
                center.elevation_m,
                west.elevation_m,
                east.elevation_m,
                north.elevation_m,
                south.elevation_m,
            )
            if any(elevation is None for elevation in elevations):
                continue

            dx = great_circle_distance_m(
                center.latitude,
                west.longitude,
                center.latitude,
                east.longitude,
            )
            dy = great_circle_distance_m(
                north.latitude,
                center.longitude,
                south.latitude,
                center.longitude,
            )
            if dx == 0 or dy == 0:
                continue

            dz_dx = ((east.elevation_m or 0.0) - (west.elevation_m or 0.0)) / dx
            dz_dy = ((north.elevation_m or 0.0) - (south.elevation_m or 0.0)) / dy

            slope_rad = atan2(sqrt(dz_dx * dz_dx + dz_dy * dz_dy), 1.0)
            aspect_rad = atan2(-dz_dx, dz_dy)
            center.slope_deg = degrees(slope_rad)
            center.aspect_deg = (degrees(aspect_rad) + 360.0) % 360.0

    return samples
