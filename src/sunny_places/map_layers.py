from __future__ import annotations

from typing import Any

import pydeck as pdk

from sunny_places.models import CandidatePlace, SamplePoint
from sunny_places.theme import build_map_style


def build_map_layers(
    samples: list[SamplePoint],
    selected_place: CandidatePlace | None,
) -> list[pdk.Layer]:
    style = build_map_style()
    points_data = [
        {
            "latitude": sample.latitude,
            "longitude": sample.longitude,
            "weight": sample.score or 0.0,
            "score": sample.score or 0.0,
            "coordinates": f"{sample.latitude:.5f}, {sample.longitude:.5f}",
        }
        for sample in samples
    ]

    layers: list[pdk.Layer] = [
        pdk.Layer(
            "HeatmapLayer",
            data=points_data,
            get_position="[longitude, latitude]",
            get_weight="weight",
            opacity=style["heatmap_alpha"],
            radiusPixels=55,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=points_data,
            get_position="[longitude, latitude]",
            get_radius=28,
            get_fill_color=style["point_fill"],
            pickable=True,
        ),
    ]

    if selected_place is not None:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=[
                    {
                        "latitude": selected_place.latitude,
                        "longitude": selected_place.longitude,
                    }
                ],
                get_position="[longitude, latitude]",
                get_radius=70,
                get_fill_color=style["selected_fill"],
                pickable=False,
            )
        )
    return layers


def build_deck(
    latitude: float,
    longitude: float,
    zoom: float,
    samples: list[SamplePoint],
    selected_place: CandidatePlace | None,
) -> pdk.Deck:
    layers = build_map_layers(samples, selected_place)
    tooltip: dict[str, Any] = {
        "html": "<b>Score:</b> {score}<br/><b>Coords:</b> {coordinates}",
        "style": {"backgroundColor": "#0f1b2d", "color": "#f5f7fb"},
    }
    return pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=latitude,
            longitude=longitude,
            zoom=zoom,
            pitch=35,
        ),
        tooltip=tooltip,
        map_style=build_map_style()["basemap_style"],
    )
