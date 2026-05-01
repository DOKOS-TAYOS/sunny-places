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
    by_position = sorted(samples, key=lambda sample: (-sample.latitude, sample.longitude))

    sample_rows: list[list[SamplePoint]] = []
    current_row: list[SamplePoint] = []
    previous_latitude: float | None = None
    for sample in by_position:
        if previous_latitude is None or abs(sample.latitude - previous_latitude) < 1e-10:
            current_row.append(sample)
        else:
            sample_rows.append(current_row)
            current_row = [sample]
        previous_latitude = sample.latitude
    if current_row:
        sample_rows.append(current_row)

    if not sample_rows:
        return samples

    for row in sample_rows:
        row.sort(key=lambda sample: sample.longitude)

    rows_count = len(sample_rows)
    columns_count = max(len(row) for row in sample_rows)
    if rows_count < 3 or columns_count < 3:
        return samples

    for row_index in range(1, rows_count - 1):
        previous_row = sample_rows[row_index - 1]
        current = sample_rows[row_index]
        next_row = sample_rows[row_index + 1]
        if len(previous_row) != len(current) or len(current) != len(next_row):
            continue

        for column_index in range(1, len(current) - 1):
            center = current[column_index]
            west = current[column_index - 1]
            east = current[column_index + 1]
            north = previous_row[column_index]
            south = next_row[column_index]

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
