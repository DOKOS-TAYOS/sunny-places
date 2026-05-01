from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "app_title": "Sunny Places",
        "app_subtitle": "Encuentra zonas cercanas con mejor sol para relajarte.",
        "search_label": "Buscar un lugar",
        "search_placeholder": "Bilbao, Barcelona, Bondi Beach...",
        "search_button": "Buscar",
        "loading_data": "Calculando el mapa solar...",
        "date_label": "Fecha",
        "time_label": "Hora local",
        "radius_label": "Radio de analisis (m)",
        "language_label": "Idioma",
        "map_title": "Mapa solar",
        "map_intro": (
            "Las manchas calidas indican mejores zonas para tomar el sol cerca del punto buscado."
        ),
        "table_title": "Lugares cercanos",
        "most_sunny": "Mas soleados",
        "least_sunny": "Menos soleados",
        "score_label": "Indice de sol",
        "coordinates_label": "Coordenadas",
        "cloud_cover_label": "Nubosidad",
        "direct_radiation_label": "Radiacion directa",
        "diffuse_radiation_label": "Radiacion difusa",
        "selected_place": "Lugar seleccionado",
        "fallback_points": "Puntos calculados",
        "named_places": "Lugares reales",
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
        "table_distance": "Distancia (m)",
        "hover_hint": "Pulsa un punto del mapa o una fila para ver mas detalle.",
        "weather_context": "Condiciones reales con Open-Meteo y relieve local.",
        "sun_summary": (
            "Cuanto mayor el indice, mas agradable deberia sentirse el sol en ese punto."
        ),
        "provider_warning": "Se ha usado un fallback para mantener la app util durante la demo.",
        "sample_point": "Punto de muestra",
        "map_popup_hint": "Detalle del mapa",
        "selected_none": "Todavia no hay un lugar seleccionado.",
        "best_spots_hint": "Puedes pulsar una fila para centrar y resaltar ese sitio.",
    },
    "en": {
        "app_title": "Sunny Places",
        "app_subtitle": "Find nearby spots with better sunshine to relax.",
        "search_label": "Search a place",
        "search_placeholder": "Bilbao, Barcelona, Bondi Beach...",
        "search_button": "Search",
        "loading_data": "Computing the solar map...",
        "date_label": "Date",
        "time_label": "Local time",
        "radius_label": "Analysis radius (m)",
        "language_label": "Language",
        "map_title": "Solar map",
        "map_intro": (
            "Warmer areas show better nearby spots to enjoy the sun around the searched place."
        ),
        "table_title": "Nearby places",
        "most_sunny": "Most sunny",
        "least_sunny": "Least sunny",
        "score_label": "Sun score",
        "coordinates_label": "Coordinates",
        "cloud_cover_label": "Cloud cover",
        "direct_radiation_label": "Direct radiation",
        "diffuse_radiation_label": "Diffuse radiation",
        "selected_place": "Selected place",
        "fallback_points": "Computed points",
        "named_places": "Named places",
        "no_places_found": ("No named places were found nearby. Showing computed points instead."),
        "search_error": "That place could not be found.",
        "data_error": (
            "Some external data could not be loaded. Partial results are shown when possible."
        ),
        "table_name": "Place",
        "table_category": "Type",
        "table_score": "Sun",
        "table_distance": "Distance (m)",
        "hover_hint": "Click a map point or a ranked row to inspect it.",
        "weather_context": "Real conditions with Open-Meteo and local terrain.",
        "sun_summary": "The higher the score, the more pleasant the sun should feel there.",
        "provider_warning": "A fallback was used so the demo stays usable.",
        "sample_point": "Sample point",
        "map_popup_hint": "Map detail",
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
