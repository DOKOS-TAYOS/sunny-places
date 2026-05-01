# Sunny Places

Sunny Places is a bilingual `Streamlit` app that helps people find nearby sunny spots where they can relax. It starts centered on Bilbao, lets you search anywhere in the world, and combines solar geometry, Open-Meteo weather data, and local terrain to estimate how pleasant the sun should feel around you.

The repository itself is licensed under `MIT`. Third-party software and service terms are summarized in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Features

- Dark-mode UI from the first load.
- Spanish and English UI with an in-app toggle.
- Worldwide place search.
- Date and local-time controls.
- Nearby solar heatmap with low opacity so the basemap stays readable.
- Clickable heatmap cells with coordinates and score details.
- Ranked lists of the most and least sunny nearby places.
- Fallback to computed sample points when named places are scarce.

## How It Works

The V1 focuses on being useful rather than pretending to model every building shadow:

- Solar position is calculated locally for the selected place, date, and time.
- Real atmospheric conditions come from `Open-Meteo`.
- Nearby terrain orientation is inferred from sampled elevations, which adds meaningful variation across hillsides and slopes.
- Real nearby places are pulled from OpenStreetMap services and scored from the nearest sampled terrain point.

This means the app is especially helpful for identifying sunny slopes, parks, viewpoints, and open spots, while keeping the project lightweight enough for `Streamlit Community Cloud`.

## Run Locally

On Windows PowerShell:

```powershell
.\.venv\Scripts\pip.exe install -e .[dev]
.\.venv\Scripts\streamlit.exe run app.py
```

On Linux:

```bash
source .venv/bin/activate
pip install -e .[dev]
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

This repository is ready to deploy as a public app on `Streamlit Community Cloud`.

Recommended deployment settings:

1. Use `app.py` as the entrypoint.
2. Let Community Cloud install dependencies from [requirements.txt](requirements.txt).
3. Use the same Python major/minor version you develop with locally when possible.

Official Streamlit deployment docs:

- [Community Cloud overview](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

## Quality Checks

Before finishing Python work in this repo, run:

```powershell
.\.venv\Scripts\ruff.exe check . --fix
.\.venv\Scripts\ruff.exe format .
.\.venv\Scripts\pytest.exe
```

If `pyright` is later added to the project, run it before pushing as well.

## Project Structure

```text
app.py
src/sunny_places/
tests/
.streamlit/config.toml
```

Key modules:

- `i18n.py`: Spanish/English strings.
- `theme.py`: dark theme styling.
- `sampling.py`: local sampling grid and terrain metrics.
- `solar.py`: solar position and sun score.
- `weather.py`: Open-Meteo adapters.
- `geocoding.py`: place search and nearby named places.
- `map_folium.py`: Folium map rendering and interactive overlays.

## Licensing and External Services

The project code is `MIT`, but the live app depends on third-party data/services with their own rules.

- `Open-Meteo`: the free API terms are the main commercial caution point. At the time checked for this repo, the free tier is described for `non-commercial use` and tied to `CC-BY 4.0` attribution.
- `OpenStreetMap / Nominatim / Overpass`: attribution is required, usage of the public infrastructure must stay moderate, and OSM data is generally under `ODbL`.
- `CARTO` basemap tiles: attribution is already shown on the map; if usage grows, review their current public basemap terms.

See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for the detailed dependency and service summary.

## Deployment Notes

- The app is designed for `Streamlit Community Cloud`.
- No paid APIs are required for the first version.
- Public external services should be used politely and may impose rate limits.

## Limitations

- V1 does not model exact shadows from buildings or trees.
- Nearby-place quality depends on available OpenStreetMap data.
- Weather quality depends on Open-Meteo coverage and model resolution.
