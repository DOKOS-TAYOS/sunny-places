from sunny_places.comfort import calculate_comfort_score, calculate_wind_comfort_factor


def test_comfort_score_rewards_good_sun_with_moderate_wind() -> None:
    pleasant = calculate_comfort_score(78.0, 12.0)
    windy = calculate_comfort_score(78.0, 32.0)

    assert pleasant > windy


def test_comfort_score_penalizes_low_sun_even_with_good_wind() -> None:
    low_sun = calculate_comfort_score(12.0, 12.0)
    high_sun = calculate_comfort_score(78.0, 12.0)

    assert high_sun > low_sun


def test_wind_comfort_factor_prefers_midrange_breeze() -> None:
    assert calculate_wind_comfort_factor(12.0) > calculate_wind_comfort_factor(2.0)
    assert calculate_wind_comfort_factor(12.0) > calculate_wind_comfort_factor(30.0)
