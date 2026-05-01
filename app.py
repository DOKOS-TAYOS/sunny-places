from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
import streamlit as st
from requests import RequestException
from streamlit_folium import st_folium

from sunny_places.app_state import get_default_view_state
from sunny_places.demo_logic import build_fallback_places, format_data_error_message
from sunny_places.i18n import get_text
from sunny_places.map_folium import build_folium_map
from sunny_places.models import CandidatePlace, SamplePoint, WeatherSnapshot
from sunny_places.ranking import split_ranked_places
from sunny_places.sampling import (
    apply_terrain_metrics,
    generate_sample_grid,
    great_circle_distance_m,
)
from sunny_places.services import (
    cached_fetch_elevations,
    cached_fetch_nearby_places,
    cached_fetch_weather_snapshot,
    cached_search_places,
)
from sunny_places.solar import calculate_sun_score
from sunny_places.theme import build_streamlit_css
from sunny_places.ui_state import (
    build_place_key,
    extract_clicked_coordinates,
    extract_selected_key_from_map_event,
    find_place_by_key,
    find_sample_by_key,
)


def ensure_session_state() -> None:
    defaults = get_default_view_state()
    st.session_state.setdefault("locale", defaults.locale)
    st.session_state.setdefault("theme", defaults.theme)
    st.session_state.setdefault("center_latitude", defaults.center.latitude)
    st.session_state.setdefault("center_longitude", defaults.center.longitude)
    st.session_state.setdefault("center_name", "Bilbao")
    st.session_state.setdefault("radius_m", 1200.0)
    st.session_state.setdefault("selected_place_key", None)
    st.session_state.setdefault("map_center_latitude", defaults.center.latitude)
    st.session_state.setdefault("map_center_longitude", defaults.center.longitude)


def translate(key: str) -> str:
    return get_text(st.session_state.get("locale", "es"), key)


def build_local_datetime(target_date: date, target_time: time, offset_seconds: int) -> datetime:
    offset = timezone(timedelta(seconds=offset_seconds))
    return datetime.combine(target_date, target_time, tzinfo=offset)


def fallback_weather_snapshot() -> WeatherSnapshot:
    return WeatherSnapshot(
        cloud_cover=20.0,
        shortwave_radiation=700.0,
        direct_radiation=520.0,
        diffuse_radiation=120.0,
        direct_normal_irradiance=760.0,
        timezone_name="UTC",
        utc_offset_seconds=0,
    )


def render_sidebar() -> tuple[str, date, time, float, bool]:
    st.sidebar.markdown(f"### {translate('app_title')}")
    locale_label = st.sidebar.segmented_control(
        translate("language_label"),
        options=["ES", "EN"],
        selection_mode="single",
        default="ES" if st.session_state["locale"] == "es" else "EN",
    )
    st.session_state["locale"] = "es" if locale_label == "ES" else "en"

    search_query = st.sidebar.text_input(
        translate("search_label"),
        value=st.session_state.get("center_name", "Bilbao"),
        placeholder=translate("search_placeholder"),
    )
    search_clicked = st.sidebar.button(translate("search_button"), width="stretch")
    target_date = st.sidebar.date_input(translate("date_label"))
    target_time = st.sidebar.time_input(translate("time_label"), value=time(hour=16, minute=0))
    radius_m = float(
        st.sidebar.slider(
            translate("radius_label"),
            min_value=400,
            max_value=5000,
            value=int(st.session_state["radius_m"]),
            step=100,
        )
    )
    return search_query, target_date, target_time, radius_m, search_clicked


def maybe_update_search_location(search_query: str, search_clicked: bool) -> None:
    if not search_clicked or not search_query.strip():
        return

    results = cached_search_places(search_query.strip())
    if not results:
        raise ValueError(translate("search_error"))

    top_result = results[0]
    st.session_state["center_latitude"] = top_result.latitude
    st.session_state["center_longitude"] = top_result.longitude
    st.session_state["center_name"] = top_result.name
    st.session_state["selected_place_key"] = None
    st.session_state["map_center_latitude"] = top_result.latitude
    st.session_state["map_center_longitude"] = top_result.longitude


def enrich_samples_with_sun(
    samples: list[SamplePoint],
    target_datetime: datetime,
    radius_m: float,
    warnings: list[str],
) -> tuple[list[SamplePoint], dict[str, float]]:
    try:
        elevations = cached_fetch_elevations(
            tuple(sample.latitude for sample in samples),
            tuple(sample.longitude for sample in samples),
        )
        for sample, elevation in zip(samples, elevations, strict=True):
            sample.elevation_m = elevation
        samples = apply_terrain_metrics(samples)
    except RequestException:
        warnings.append(translate("provider_warning"))

    try:
        weather = cached_fetch_weather_snapshot(
            samples[0].latitude,
            samples[0].longitude,
            target_datetime,
        )
    except RequestException:
        weather = fallback_weather_snapshot()
        warnings.append(translate("provider_warning"))

    localized_datetime = build_local_datetime(
        target_datetime.date(),
        target_datetime.time(),
        weather.utc_offset_seconds,
    )
    for sample in samples:
        sample.score = calculate_sun_score(
            sample.latitude,
            sample.longitude,
            localized_datetime,
            weather,
            slope_deg=sample.slope_deg,
            aspect_deg=sample.aspect_deg,
        )

    context = {
        "cloud_cover": weather.cloud_cover,
        "direct_radiation": weather.direct_radiation,
        "diffuse_radiation": weather.diffuse_radiation,
        "radius_m": radius_m,
    }
    return samples, context


def score_places(
    places: list[CandidatePlace],
    samples: list[SamplePoint],
) -> list[CandidatePlace]:
    for place in places:
        nearest_sample = min(
            samples,
            key=lambda sample: great_circle_distance_m(
                place.latitude,
                place.longitude,
                sample.latitude,
                sample.longitude,
            ),
        )
        place.score = nearest_sample.score or 0.0
        place.metadata["nearest_sample_latitude"] = nearest_sample.latitude
        place.metadata["nearest_sample_longitude"] = nearest_sample.longitude
        place.metadata["place_key"] = build_place_key(place)
    return places


def render_places_table(
    title_key: str,
    places: list[CandidatePlace],
    selection_prefix: str,
) -> CandidatePlace | None:
    st.subheader(translate(title_key))
    dataframe = pd.DataFrame(
        [
            {
                translate("table_name"): place.name,
                translate("table_category"): place.category,
                translate("table_score"): round(place.score, 1),
                translate("table_distance"): round(place.distance_m or 0.0, 1),
            }
            for place in places
        ]
    )

    if dataframe.empty:
        st.caption("-")
        return None

    event = st.dataframe(
        dataframe,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"{selection_prefix}_table",
    )
    selection_rows = list(getattr(getattr(event, "selection", None), "rows", []))
    if selection_rows:
        selected = places[int(selection_rows[0])]
        st.session_state["selected_place_key"] = build_place_key(selected)
        st.session_state["map_center_latitude"] = selected.latitude
        st.session_state["map_center_longitude"] = selected.longitude
        return selected
    return None


def render_selected_place_card(selected_place: CandidatePlace | None) -> None:
    if selected_place is None:
        st.caption(translate("selected_none"))
        return

    card_html = f"""
    <div class="sunny-card sunny-card-strong">
        <strong>{translate("selected_place")}</strong><br/>
        <div>{selected_place.name}</div>
        <div class="sunny-kpi">{translate("score_label")}: {selected_place.score:.1f}</div>
        <div class="sunny-kpi">{translate("table_category")}: {selected_place.category}</div>
        <div class="sunny-kpi">
            {translate("table_distance")}: {selected_place.distance_m or 0.0:.0f} m
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def compute_demo_payload(
    target_date: date,
    target_time: time,
    radius_m: float,
) -> tuple[list[SamplePoint], dict[str, float], list[CandidatePlace], list[str]]:
    warnings: list[str] = []
    target_datetime = datetime.combine(target_date, target_time)
    samples = generate_sample_grid(
        st.session_state["center_latitude"],
        st.session_state["center_longitude"],
        radius_m=radius_m,
        grid_size=9,
    )
    samples, context = enrich_samples_with_sun(samples, target_datetime, radius_m, warnings)

    try:
        nearby_places = cached_fetch_nearby_places(
            st.session_state["center_latitude"],
            st.session_state["center_longitude"],
            radius_m=radius_m,
        )
        scored_places = score_places(nearby_places, samples)
    except RequestException:
        scored_places = []
        warnings.append(translate("provider_warning"))

    if not scored_places:
        st.info(translate("no_places_found"))
        scored_places = build_fallback_places(samples, translate("fallback_points"))
    return samples, context, scored_places, warnings


def render_map(
    samples: list[SamplePoint],
    places: list[CandidatePlace],
    selected_key: str | None,
    weather_context: dict[str, float],
) -> CandidatePlace | None:
    selected_place = find_place_by_key(places, selected_key)
    selected_sample = find_sample_by_key(samples, selected_key)

    center_latitude = st.session_state["map_center_latitude"]
    center_longitude = st.session_state["map_center_longitude"]
    if selected_place is not None:
        center_latitude = selected_place.latitude
        center_longitude = selected_place.longitude
    elif selected_sample is not None:
        center_latitude = selected_sample.latitude
        center_longitude = selected_sample.longitude

    folium_map = build_folium_map(
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        samples=samples,
        places=places,
        selected_key=selected_key,
        weather_context=weather_context,
        sample_label=translate("sample_point"),
        score_label=translate("score_label"),
        coordinates_label=translate("coordinates_label"),
        cloud_cover_label=translate("cloud_cover_label"),
        direct_radiation_label=translate("direct_radiation_label"),
        diffuse_radiation_label=translate("diffuse_radiation_label"),
    )
    event = st_folium(
        folium_map,
        key="sunny_places_map",
        width=None,
        height=560,
        returned_objects=["last_object_clicked_popup", "last_clicked"],
    )

    clicked_coordinates = extract_clicked_coordinates(event if isinstance(event, dict) else None)
    if clicked_coordinates is not None:
        st.session_state["map_center_latitude"] = clicked_coordinates[0]
        st.session_state["map_center_longitude"] = clicked_coordinates[1]

    map_selected_key = extract_selected_key_from_map_event(
        event if isinstance(event, dict) else None
    )
    if map_selected_key:
        st.session_state["selected_place_key"] = map_selected_key
        selected_place = find_place_by_key(places, map_selected_key)
        selected_sample = find_sample_by_key(samples, map_selected_key)
        if selected_place is not None:
            st.session_state["map_center_latitude"] = selected_place.latitude
            st.session_state["map_center_longitude"] = selected_place.longitude
        elif selected_sample is not None:
            st.session_state["map_center_latitude"] = selected_sample.latitude
            st.session_state["map_center_longitude"] = selected_sample.longitude
    return selected_place


def main() -> None:
    st.set_page_config(page_title="Sunny Places", page_icon="Sun", layout="wide")
    ensure_session_state()
    st.markdown(build_streamlit_css(), unsafe_allow_html=True)

    st.title(translate("app_title"))
    st.caption(translate("app_subtitle"))

    search_query, target_date, target_time, radius_m, search_clicked = render_sidebar()

    try:
        maybe_update_search_location(search_query, search_clicked)
        st.session_state["radius_m"] = radius_m
        with st.spinner(translate("loading_data")):
            samples, context, scored_places, warnings = compute_demo_payload(
                target_date,
                target_time,
                radius_m,
            )
    except Exception as exc:  # noqa: BLE001
        st.error(format_data_error_message(translate("data_error"), exc))
        samples = []
        context = {"cloud_cover": 0.0, "direct_radiation": 0.0, "diffuse_radiation": 0.0}
        scored_places = []
        warnings = []

    sunny_places, shady_places = split_ranked_places(scored_places)
    selected_place = find_place_by_key(scored_places, st.session_state.get("selected_place_key"))

    for warning_message in dict.fromkeys(warnings):
        st.warning(warning_message)

    left_column, right_column = st.columns([2.2, 1.0], gap="large")

    with right_column:
        table_card = (
            "<div class='sunny-card'>"
            f"<strong>{translate('table_title')}</strong><br/>"
            f"<span class='sunny-muted'>{translate('best_spots_hint')}</span>"
            "</div>"
        )
        st.markdown(table_card, unsafe_allow_html=True)
        selected_from_sunny = render_places_table("most_sunny", sunny_places, "sunny")
        selected_from_shady = render_places_table("least_sunny", shady_places, "shady")
        selected_place = selected_from_sunny or selected_from_shady or selected_place
        render_selected_place_card(selected_place)

    with left_column:
        st.subheader(translate("map_title"))
        st.caption(translate("map_intro"))
        st.caption(translate("hover_hint"))
        if samples:
            selected_from_map = render_map(
                samples=samples,
                places=scored_places,
                selected_key=st.session_state.get("selected_place_key"),
                weather_context=context,
            )
            selected_place = selected_from_map or selected_place
        else:
            st.info(translate("data_error"))

        summary_card = f"""
        <div class="sunny-card">
            <strong>{translate("sun_summary")}</strong><br/>
            <span class="sunny-kpi">
                {translate("cloud_cover_label")}: {context["cloud_cover"]:.0f}%
            </span>
            <span class="sunny-kpi">
                {translate("direct_radiation_label")}: {context["direct_radiation"]:.0f} W/m2
            </span>
            <span class="sunny-kpi">
                {translate("diffuse_radiation_label")}: {context["diffuse_radiation"]:.0f} W/m2
            </span>
        </div>
        """
        st.markdown(summary_card, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
