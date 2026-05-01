from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "app_title": "Sunny Places",
        "app_subtitle": "Encuentra zonas cercanas con mejor sol para relajarte.",
        "search_label": "Buscar un lugar",
        "search_placeholder": "Bilbao, Barcelona, Bondi Beach...",
        "search_button": "Buscar",
        "recompute_button": "Recalcular mapa",
        "loading_data": "Calculando el mapa solar...",
        "layer_label": "Capa",
        "layer_sun": "Sol",
        "layer_wind": "Viento",
        "layer_comfort": "Confort",
        "show_bars_label": "Mostrar bares",
        "date_label": "Fecha",
        "time_label": "Hora local",
        "radius_label": "Radio de analisis (m)",
        "custom_point_name": "Punto personalizado",
        "retry_message": "Vuelve a intentarlo dentro de un momento.",
        "timeout_message": "Los proveedores han tardado demasiado en responder.",
        "language_label": "Idioma",
        "map_title": "Mapa solar",
        "map_intro": (
            "Las manchas calidas indican mejores zonas para tomar el sol cerca del punto buscado."
        ),
        "map_intro_wind": (
            "Las manchas mas intensas indican zonas mas expuestas al viento "
            "cerca del punto buscado."
        ),
        "map_intro_comfort": (
            "Las manchas mas agradables combinan buen sol y un viento mas llevadero."
        ),
        "table_title": "Lugares cercanos",
        "most_sunny": "Mas soleados",
        "least_sunny": "Menos soleados",
        "most_windy": "Mas ventosos",
        "least_windy": "Menos ventosos",
        "most_comfortable": "Mas confortables",
        "least_comfortable": "Menos confortables",
        "score_label": "Indice de sol",
        "wind_score_label": "Indice de viento",
        "comfort_score_label": "Indice de confort",
        "coordinates_label": "Coordenadas",
        "cloud_cover_label": "Nubosidad",
        "direct_radiation_label": "Radiacion directa",
        "diffuse_radiation_label": "Radiacion difusa",
        "shortwave_radiation_label": "Radiacion global",
        "dni_label": "Irradiancia normal directa",
        "wind_speed_label": "Velocidad del viento",
        "wind_gusts_label": "Rachas",
        "wind_direction_label": "Direccion del viento",
        "elevation_label": "Elevacion",
        "slope_label": "Pendiente",
        "selected_place": "Lugar seleccionado",
        "fallback_points": "Puntos calculados",
        "no_places_found": (
            "No se encontraron lugares con nombre cerca. Mostrando puntos calculados."
        ),
        "search_error": "No se pudo encontrar ese lugar.",
        "data_error": (
            "No se pudieron cargar algunos datos externos. "
            "Se muestran resultados parciales si es posible."
        ),
        "table_name": "Lugar",
        "table_category": "Tipo",
        "table_score": "Sol",
        "table_score_wind": "Viento",
        "table_score_comfort": "Confort",
        "table_distance": "Distancia (m)",
        "hover_hint": "Pulsa un punto del mapa o una fila para ver mas detalle.",
        "data_sources_caption": (
            "Fuentes: Open-Meteo, OpenStreetMap (Nominatim/Overpass) y CARTO."
        ),
        "sun_summary": (
            "Cuanto mayor el indice, mas agradable deberia sentirse el sol en ese punto."
        ),
        "wind_summary": (
            "Cuanto mayor el indice, mas expuesto al viento deberia sentirse ese punto."
        ),
        "comfort_summary": (
            "Cuanto mayor el indice, mas agradable deberia sentirse el equilibrio "
            "entre sol y viento."
        ),
        "provider_warning": "Se ha usado un fallback para mantener la app util durante la demo.",
        "sample_point": "Punto de muestra",
        "bars_label": "Bar",
        "selected_none": "Todavia no hay un lugar seleccionado.",
        "best_spots_hint": "Puedes pulsar una fila para centrar y resaltar ese sitio.",
    },
    "en": {
        "app_title": "Sunny Places",
        "app_subtitle": "Find nearby spots with better sunshine to relax.",
        "search_label": "Search a place",
        "search_placeholder": "Bilbao, Barcelona, Bondi Beach...",
        "search_button": "Search",
        "recompute_button": "Recompute map",
        "loading_data": "Computing the solar map...",
        "layer_label": "Layer",
        "layer_sun": "Sun",
        "layer_wind": "Wind",
        "layer_comfort": "Comfort",
        "show_bars_label": "Show bars",
        "date_label": "Date",
        "time_label": "Local time",
        "radius_label": "Analysis radius (m)",
        "custom_point_name": "Custom point",
        "retry_message": "Please try again in a moment.",
        "timeout_message": "The providers took too long to respond.",
        "language_label": "Language",
        "map_title": "Solar map",
        "map_intro": (
            "Warmer areas show better nearby spots to enjoy the sun around the searched place."
        ),
        "map_intro_wind": (
            "Stronger areas show nearby spots that should feel windier around the searched place."
        ),
        "map_intro_comfort": (
            "More pleasant areas combine good sunshine with a more comfortable breeze."
        ),
        "table_title": "Nearby places",
        "most_sunny": "Most sunny",
        "least_sunny": "Least sunny",
        "most_windy": "Most windy",
        "least_windy": "Least windy",
        "most_comfortable": "Most comfortable",
        "least_comfortable": "Least comfortable",
        "score_label": "Sun score",
        "wind_score_label": "Wind score",
        "comfort_score_label": "Comfort score",
        "coordinates_label": "Coordinates",
        "cloud_cover_label": "Cloud cover",
        "direct_radiation_label": "Direct radiation",
        "diffuse_radiation_label": "Diffuse radiation",
        "shortwave_radiation_label": "Global radiation",
        "dni_label": "Direct normal irradiance",
        "wind_speed_label": "Wind speed",
        "wind_gusts_label": "Wind gusts",
        "wind_direction_label": "Wind direction",
        "elevation_label": "Elevation",
        "slope_label": "Slope",
        "selected_place": "Selected place",
        "fallback_points": "Computed points",
        "no_places_found": ("No named places were found nearby. Showing computed points instead."),
        "search_error": "That place could not be found.",
        "data_error": (
            "Some external data could not be loaded. Partial results are shown when possible."
        ),
        "table_name": "Place",
        "table_category": "Type",
        "table_score": "Sun",
        "table_score_wind": "Wind",
        "table_score_comfort": "Comfort",
        "table_distance": "Distance (m)",
        "hover_hint": "Click a map point or a ranked row to inspect it.",
        "data_sources_caption": (
            "Sources: Open-Meteo, OpenStreetMap (Nominatim/Overpass), and CARTO."
        ),
        "sun_summary": "The higher the score, the more pleasant the sun should feel there.",
        "wind_summary": "The higher the score, the windier that spot should feel.",
        "comfort_summary": (
            "The higher the score, the more balanced the sun and breeze should feel."
        ),
        "provider_warning": "A fallback was used so the demo stays usable.",
        "sample_point": "Sample point",
        "bars_label": "Bar",
        "selected_none": "There is no selected place yet.",
        "best_spots_hint": "Click a row to center and highlight that spot.",
    },
}


def get_text(locale: str, key: str) -> str:
    if locale in TRANSLATIONS and key in TRANSLATIONS[locale]:
        return TRANSLATIONS[locale][key]
    if key in TRANSLATIONS["es"]:
        return TRANSLATIONS["es"][key]
    return key
