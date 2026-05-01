from __future__ import annotations


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def calculate_wind_comfort_factor(wind_score: float) -> float:
    preferred_center = 12.0
    tolerance = 18.0
    comfort = 1.0 - abs(wind_score - preferred_center) / tolerance
    return clamp(comfort, 0.0, 1.0)


def calculate_comfort_score(sun_score: float, wind_score: float) -> float:
    sun_factor = clamp(sun_score / 100.0, 0.0, 1.0)
    wind_comfort = calculate_wind_comfort_factor(wind_score)
    blended = 0.75 * sun_factor + 0.25 * wind_comfort
    sun_gate = 0.35 + 0.65 * sun_factor
    return round(100.0 * clamp(blended * sun_gate, 0.0, 1.0), 2)
