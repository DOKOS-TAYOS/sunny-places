from sunny_places.geocoding import (
    build_overpass_bar_query,
    build_overpass_query,
    parse_nearby_places,
    parse_search_results,
    search_places,
)


def test_parse_search_results_extracts_named_places() -> None:
    payload = [
        {
            "display_name": "Bilbao, Biscay, Basque Country, Spain",
            "lat": "43.2630",
            "lon": "-2.9350",
        }
    ]

    results = parse_search_results(payload)

    assert len(results) == 1
    assert results[0].name == "Bilbao, Biscay, Basque Country, Spain"


def test_parse_nearby_places_understands_overpass_elements() -> None:
    payload = {
        "elements": [
            {
                "type": "node",
                "lat": 43.2640,
                "lon": -2.9340,
                "tags": {"name": "Doña Casilda Park", "leisure": "park"},
            }
        ]
    }

    places = parse_nearby_places(payload)

    assert len(places) == 1
    assert places[0].category == "park"


def test_build_overpass_query_requests_named_elements_and_relations() -> None:
    query = build_overpass_query(43.2630, -2.9350, 1200)

    assert "nwr(around:1200,43.263,-2.935)[name][!building]" in query
    assert "leisure~" in query
    assert "out center;" in query


def test_build_overpass_bar_query_targets_bars_and_pubs() -> None:
    query = build_overpass_bar_query(43.2630, -2.9350, 1200)

    assert 'amenity~"bar|pub"' in query
    assert "out center;" in query


def test_search_places_uses_helper_timeout_signature(monkeypatch: object) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return [
                {
                    "display_name": "Madrid, Comunidad de Madrid, España",
                    "lat": "40.4167",
                    "lon": "-3.7033",
                }
            ]

    def fake_get_with_ssl_fallback(
        url: str,
        *,
        params: dict[str, str | int],
        headers: dict[str, str],
        timeout_s: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout_s"] = timeout_s
        return FakeResponse()

    monkeypatch.setattr("sunny_places.geocoding._get_with_ssl_fallback", fake_get_with_ssl_fallback)

    results = search_places("Madrid", limit=3, timeout_s=9.0)

    assert results[0].name == "Madrid, Comunidad de Madrid, España"
    assert captured["timeout_s"] == 9.0
