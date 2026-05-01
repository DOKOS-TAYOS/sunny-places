from __future__ import annotations

# ruff: noqa: E402
import sys
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd
import streamlit as st
from requests import RequestException
from streamlit_folium import st_folium

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sunny_places.app_state import DEFAULT_CENTER, DEFAULT_LOCALE
from sunny_places.demo_logic import (
    build_fallback_places,
    compute_zoom_for_radius,
    format_data_error_message,
)
from sunny_places.i18n import get_text
from sunny_places.map_folium import build_folium_map
from sunny_places.models import CandidatePlace, SamplePoint
from sunny_places.ranking import split_ranked_places
from sunny_places.services import (
    apply_active_layer_scores,
    build_weather_context,
    cached_compute_analysis_base,
    cached_fetch_nearby_bars,
    cached_search_places,
)
from sunny_places.theme import build_streamlit_css
from sunny_places.ui_state import (
    build_place_key,
    determine_map_click_action,
    extract_clicked_coordinates,
    extract_selected_key_from_map_event,
    find_clicked_sample_key,
    find_place_by_key,
    is_sample_key,
)


def ensure_session_state() -> None:
    st.session_state.setdefault("locale", DEFAULT_LOCALE)
    st.session_state.setdefault("center_latitude", DEFAULT_CENTER.latitude)
    st.session_state.setdefault("center_longitude", DEFAULT_CENTER.longitude)
    st.session_state.setdefault("center_name", "Bilbao")
    st.session_state.setdefault("radius_m", 1200.0)
    st.session_state.setdefault("pending_radius_m", 1200)
    st.session_state.setdefault("selected_place_key", None)
    st.session_state.setdefault("layer_mode", "sun")
    st.session_state.setdefault("show_bars", False)
    st.session_state.setdefault("pending_precise_sample_key", None)
    st.session_state.setdefault("map_center_latitude", DEFAULT_CENTER.latitude)
    st.session_state.setdefault("map_center_longitude", DEFAULT_CENTER.longitude)
    st.session_state["radius_m"] = max(float(st.session_state["radius_m"]), 100.0)
    st.session_state["pending_radius_m"] = max(int(st.session_state["pending_radius_m"]), 100)


def translate(key: str) -> str:
    return get_text(st.session_state.get("locale", "es"), key)


def set_center(latitude: float, longitude: float, name: str) -> None:
    st.session_state["center_latitude"] = latitude
    st.session_state["center_longitude"] = longitude
    st.session_state["center_name"] = name
    st.session_state["map_center_latitude"] = latitude
    st.session_state["map_center_longitude"] = longitude
    st.session_state["pending_precise_sample_key"] = None


def build_custom_point_name(latitude: float, longitude: float) -> str:
    return f"{translate('custom_point_name')} ({latitude:.5f}, {longitude:.5f})"


def current_score_label() -> str:
    if st.session_state.get("layer_mode") == "wind":
        return translate("wind_score_label")
    if st.session_state.get("layer_mode") == "comfort":
        return translate("comfort_score_label")
    return translate("score_label")


def current_table_score_label() -> str:
    if st.session_state.get("layer_mode") == "wind":
        return translate("table_score_wind")
    if st.session_state.get("layer_mode") == "comfort":
        return translate("table_score_comfort")
    return translate("table_score")


def current_rank_title_keys() -> tuple[str, str]:
    if st.session_state.get("layer_mode") == "wind":
        return "most_windy", "least_windy"
    if st.session_state.get("layer_mode") == "comfort":
        return "most_comfortable", "least_comfortable"
    return "most_sunny", "least_sunny"


def render_sidebar() -> tuple[str, date, time, float, bool, bool, bool]:
    st.sidebar.markdown(f"### {translate('app_title')}")
    locale_label = st.sidebar.segmented_control(
        translate("language_label"),
        options=["ES", "EN"],
        selection_mode="single",
        default="ES" if st.session_state["locale"] == "es" else "EN",
    )
    st.session_state["locale"] = "es" if locale_label == "ES" else "en"
    layer_choice = st.sidebar.segmented_control(
        translate("layer_label"),
        options=[
            translate("layer_sun"),
            translate("layer_wind"),
            translate("layer_comfort"),
        ],
        selection_mode="single",
        default=(
            translate("layer_wind")
            if st.session_state.get("layer_mode") == "wind"
            else (
                translate("layer_comfort")
                if st.session_state.get("layer_mode") == "comfort"
                else translate("layer_sun")
            )
        ),
    )
    if layer_choice == translate("layer_wind"):
        st.session_state["layer_mode"] = "wind"
    elif layer_choice == translate("layer_comfort"):
        st.session_state["layer_mode"] = "comfort"
    else:
        st.session_state["layer_mode"] = "sun"
    show_bars = st.sidebar.toggle(
        translate("show_bars_label"),
        value=bool(st.session_state.get("show_bars", False)),
    )
    st.session_state["show_bars"] = show_bars

    with st.sidebar.form("search_form"):
        search_query = st.text_input(
            translate("search_label"),
            value=st.session_state.get("center_name", "Bilbao"),
            placeholder=translate("search_placeholder"),
        )
        search_clicked = st.form_submit_button(translate("search_button"), width="stretch")
    target_date = st.sidebar.date_input(translate("date_label"))
    target_time = st.sidebar.time_input(translate("time_label"), value=time(hour=16, minute=0))
    radius_m = float(
        st.sidebar.slider(
            translate("radius_label"),
            min_value=100,
            max_value=5000,
            value=int(st.session_state["pending_radius_m"]),
            step=20,
            key="pending_radius_m",
        )
    )
    recalculate_clicked = st.sidebar.button(translate("recompute_button"), width="stretch")
    return (
        search_query,
        target_date,
        target_time,
        radius_m,
        search_clicked,
        recalculate_clicked,
        show_bars,
    )


def maybe_update_search_location(search_query: str, search_clicked: bool) -> None:
    if not search_clicked or not search_query.strip():
        return

    results = cached_search_places(search_query.strip())
    if not results:
        raise ValueError(translate("search_error"))

    top_result = results[0]
    set_center(top_result.latitude, top_result.longitude, top_result.name)
    st.session_state["selected_place_key"] = None
    st.session_state["pending_precise_sample_key"] = None


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
                current_table_score_label(): round(place.score, 1),
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
        st.session_state["pending_precise_sample_key"] = None
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
        <div class="sunny-kpi">{current_score_label()}: {selected_place.score:.1f}</div>
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
    layer_mode: str,
) -> tuple[list[SamplePoint], dict[str, float], list[CandidatePlace], list[str]]:
    target_datetime = datetime.combine(target_date, target_time)
    analysis_base = cached_compute_analysis_base(
        st.session_state["center_latitude"],
        st.session_state["center_longitude"],
        target_datetime.isoformat(),
        radius_m,
    )
    samples, scored_places = apply_active_layer_scores(
        analysis_base.samples,
        analysis_base.places,
        layer_mode,
    )
    context = build_weather_context(analysis_base.weather_snapshot, radius_m, layer_mode)
    warnings = [translate(warning_key) for warning_key in analysis_base.warnings]

    if not scored_places:
        st.info(translate("no_places_found"))
        scored_places = build_fallback_places(samples, translate("fallback_points"))
    return samples, context, scored_places, warnings


def render_map(
    samples: list[SamplePoint],
    places: list[CandidatePlace],
    bar_places: list[CandidatePlace],
    selected_key: str | None,
    weather_context: dict[str, float],
    radius_m: float,
) -> CandidatePlace | None:
    center_latitude = st.session_state["map_center_latitude"]
    center_longitude = st.session_state["map_center_longitude"]
    selected_place = find_place_by_key(places, selected_key)
    zoom_level = compute_zoom_for_radius(radius_m, latitude=center_latitude)

    folium_map = build_folium_map(
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        samples=samples,
        places=places,
        bar_places=bar_places,
        selected_key=selected_key,
        weather_context=weather_context,
        sample_label=translate("sample_point"),
        score_label=current_score_label(),
        coordinates_label=translate("coordinates_label"),
        bars_label=translate("bars_label"),
        cloud_cover_label=translate("cloud_cover_label"),
        shortwave_radiation_label=translate("shortwave_radiation_label"),
        direct_radiation_label=translate("direct_radiation_label"),
        diffuse_radiation_label=translate("diffuse_radiation_label"),
        dni_label=translate("dni_label"),
        wind_speed_label=translate("wind_speed_label"),
        wind_gusts_label=translate("wind_gusts_label"),
        wind_direction_label=translate("wind_direction_label"),
        elevation_label=translate("elevation_label"),
        slope_label=translate("slope_label"),
        layer_mode=st.session_state.get("layer_mode", "sun"),
        zoom_start=zoom_level,
    )
    event = st_folium(
        folium_map,
        key="sunny_places_map",
        width=None,
        height=560,
        zoom=zoom_level,
        center=(center_latitude, center_longitude),
        returned_objects=["last_object_clicked", "last_object_clicked_popup", "last_clicked"],
    )

    should_rerun = False
    map_event = event if isinstance(event, dict) else None
    clicked_coordinates = extract_clicked_coordinates(map_event)
    map_selected_key = extract_selected_key_from_map_event(map_event)
    inferred_sample_key = find_clicked_sample_key(samples, clicked_coordinates)
    effective_clicked_key = map_selected_key or inferred_sample_key
    click_action = determine_map_click_action(
        effective_clicked_key,
        st.session_state.get("pending_precise_sample_key"),
    )

    if click_action == "arm_sample" and effective_clicked_key:
        st.session_state["selected_place_key"] = effective_clicked_key
        st.session_state["pending_precise_sample_key"] = effective_clicked_key
        should_rerun = True

    if clicked_coordinates is not None:
        if click_action == "recenter" and (
            st.session_state["center_latitude"] != clicked_coordinates[0]
            or st.session_state["center_longitude"] != clicked_coordinates[1]
        ):
            set_center(
                clicked_coordinates[0],
                clicked_coordinates[1],
                build_custom_point_name(clicked_coordinates[0], clicked_coordinates[1]),
            )
            st.session_state["selected_place_key"] = None
            should_rerun = True

    if effective_clicked_key and click_action == "select_object" and not should_rerun:
        st.session_state["pending_precise_sample_key"] = None
        if st.session_state.get("selected_place_key") != effective_clicked_key:
            st.session_state["selected_place_key"] = effective_clicked_key
            should_rerun = True
        selected_place = find_place_by_key(places, effective_clicked_key)
        if selected_place is not None:
            if (
                st.session_state["map_center_latitude"] != selected_place.latitude
                or st.session_state["map_center_longitude"] != selected_place.longitude
            ):
                st.session_state["map_center_latitude"] = selected_place.latitude
                st.session_state["map_center_longitude"] = selected_place.longitude
                should_rerun = True

    if click_action == "recenter" and not is_sample_key(effective_clicked_key):
        st.session_state["pending_precise_sample_key"] = None

    if should_rerun:
        st.rerun()
    return selected_place


def main() -> None:
    st.set_page_config(page_title="Sunny Places", page_icon="Sun", layout="wide")
    ensure_session_state()
    st.markdown(build_streamlit_css(), unsafe_allow_html=True)

    st.title(translate("app_title"))
    st.caption(translate("app_subtitle"))

    (
        search_query,
        target_date,
        target_time,
        pending_radius_m,
        search_clicked,
        recalculate_clicked,
        show_bars,
    ) = render_sidebar()

    try:
        maybe_update_search_location(search_query, search_clicked)
        if recalculate_clicked:
            st.session_state["radius_m"] = pending_radius_m
            st.session_state["selected_place_key"] = None
            st.session_state["pending_precise_sample_key"] = None
        with st.spinner(translate("loading_data")):
            samples, context, scored_places, warnings = compute_demo_payload(
                target_date,
                target_time,
                st.session_state["radius_m"],
                st.session_state["layer_mode"],
            )
            bar_places: list[CandidatePlace] = []
            if show_bars:
                try:
                    bar_places = cached_fetch_nearby_bars(
                        st.session_state["center_latitude"],
                        st.session_state["center_longitude"],
                        radius_m=st.session_state["radius_m"],
                    )
                except RequestException:
                    warnings.append(translate("provider_warning"))
    except Exception as exc:  # noqa: BLE001
        st.error(
            format_data_error_message(
                translate("data_error"),
                exc,
                retry_message=translate("retry_message"),
                timeout_message=translate("timeout_message"),
            )
        )
        samples = []
        context = {
            "cloud_cover": 0.0,
            "shortwave_radiation": 0.0,
            "direct_radiation": 0.0,
            "diffuse_radiation": 0.0,
            "direct_normal_irradiance": 0.0,
            "wind_speed_10m": 0.0,
            "wind_gusts_10m": 0.0,
            "wind_direction_10m": 0.0,
        }
        scored_places = []
        bar_places = []
        warnings = []

    sunny_places, shady_places = split_ranked_places(scored_places)
    selected_place = find_place_by_key(scored_places, st.session_state.get("selected_place_key"))

    for warning_message in dict.fromkeys(warnings):
        st.warning(warning_message)

    left_column, right_column = st.columns([2.2, 1.0], gap="large")

    with right_column:
        sunny_title_key, shady_title_key = current_rank_title_keys()
        table_card = (
            "<div class='sunny-card'>"
            f"<strong>{translate('table_title')}</strong><br/>"
            f"<span class='sunny-muted'>{translate('best_spots_hint')}</span>"
            "</div>"
        )
        st.markdown(table_card, unsafe_allow_html=True)
        selected_from_sunny = render_places_table(sunny_title_key, sunny_places, "sunny")
        selected_from_shady = render_places_table(shady_title_key, shady_places, "shady")
        selected_place = selected_from_sunny or selected_from_shady or selected_place
        render_selected_place_card(selected_place)

    with left_column:
        st.subheader(translate("map_title"))
        st.caption(
            translate("map_intro_wind")
            if st.session_state.get("layer_mode") == "wind"
            else (
                translate("map_intro_comfort")
                if st.session_state.get("layer_mode") == "comfort"
                else translate("map_intro")
            )
        )
        st.caption(translate("hover_hint"))
        if samples:
            selected_from_map = render_map(
                samples=samples,
                places=scored_places,
                bar_places=bar_places,
                selected_key=st.session_state.get("selected_place_key"),
                weather_context=context,
                radius_m=st.session_state["radius_m"],
            )
            selected_place = selected_from_map or selected_place
        else:
            st.info(translate("data_error"))

        summary_active_score = max((sample.score or 0.0) for sample in samples) if samples else 0.0

        summary_card = f"""
        <div class="sunny-card">
            <strong>{
            translate("wind_summary")
            if st.session_state.get("layer_mode") == "wind"
            else (
                translate("comfort_summary")
                if st.session_state.get("layer_mode") == "comfort"
                else translate("sun_summary")
            )
        }</strong><br/>
            <span class="sunny-kpi">
                {
            translate("wind_speed_label")
            if st.session_state.get("layer_mode") == "wind"
            else (
                translate("cloud_cover_label")
                if st.session_state.get("layer_mode") == "sun"
                else current_score_label()
            )
        }: {
            f"{context['wind_speed_10m']:.1f} km/h"
            if st.session_state.get("layer_mode") == "wind"
            else (
                f"{context['cloud_cover']:.0f}%"
                if st.session_state.get("layer_mode") == "sun"
                else f"{summary_active_score:.1f}"
            )
        }
            </span>
            <span class="sunny-kpi">
                {
            translate("wind_gusts_label")
            if st.session_state.get("layer_mode") == "wind"
            else (
                translate("direct_radiation_label")
                if st.session_state.get("layer_mode") == "sun"
                else translate("wind_speed_label")
            )
        }: {
            f"{context['wind_gusts_10m']:.1f} km/h"
            if st.session_state.get("layer_mode") == "wind"
            else (
                f"{context['direct_radiation']:.0f} W/m2"
                if st.session_state.get("layer_mode") == "sun"
                else f"{context['wind_speed_10m']:.1f} km/h"
            )
        }
            </span>
            <span class="sunny-kpi">
                {
            translate("wind_direction_label")
            if st.session_state.get("layer_mode") == "wind"
            else (
                translate("diffuse_radiation_label")
                if st.session_state.get("layer_mode") == "sun"
                else translate("direct_radiation_label")
            )
        }: {
            f"{context['wind_direction_10m']:.0f} deg"
            if st.session_state.get("layer_mode") == "wind"
            else (
                f"{context['diffuse_radiation']:.0f} W/m2"
                if st.session_state.get("layer_mode") == "sun"
                else f"{context['direct_radiation']:.0f} W/m2"
            )
        }
            </span>
        </div>
        """
        st.markdown(summary_card, unsafe_allow_html=True)
        st.caption(translate("data_sources_caption"))


if __name__ == "__main__":
    main()
