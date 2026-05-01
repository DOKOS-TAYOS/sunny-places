from sunny_places.geocoding import build_overpass_query, parse_nearby_places, parse_search_results


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

    assert "nwr(around:1200,43.263,-2.935)[name]" in query
    assert "relation" not in query
    assert "out center;" in query
