# Third-Party Licenses

This project's own source code is licensed under the [MIT License](LICENSE).

This file documents the main third-party software and service terms that matter when publishing the repository and deploying the app publicly.

## Compatibility Summary

- Good news: no GPL, AGPL, SSPL, or other strong copyleft software license was found in the Python dependency set used by this app.
- Your own repository can remain `MIT`.
- The most relevant non-MIT obligations come from:
  - `Apache-2.0` packages: keep copyright/license notices when redistributing.
  - `BSD` and similar permissive packages: keep the required notices.
  - `MPL-2.0` in `certifi`: weak copyleft at file level. This is generally compatible with an MIT project, but the original notices must be preserved when redistributing that package.
- The biggest restrictions are not from the Python package licenses, but from the external services and data sources:
  - `Open-Meteo` free API terms for non-commercial use.
  - `OpenStreetMap` data and public infrastructure usage policies.

## Direct Runtime Dependencies

These are the app-level dependencies declared for deployment.

| Package | Tested version | License |
| --- | ---: | --- |
| `folium` | `0.20.0` | MIT |
| `numpy` | `2.4.4` | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| `pandas` | `2.3.3` | BSD-3-Clause |
| `requests` | `2.33.1` | Apache-2.0 |
| `streamlit` | `1.57.0` | Apache-2.0 |
| `streamlit-folium` | `0.25.3` | MIT |

Notes:

- `streamlit-folium` does not expose its license cleanly in the installed wheel metadata used in this environment, but its official GitHub repository declares `MIT`.
- `numpy` bundles several permissive upstream license notices in its distribution; none of them are strong copyleft.

## Development Tooling

| Package | Tested version | License |
| --- | ---: | --- |
| `pytest` | `8.4.2` | MIT |
| `ruff` | `0.11.13` | MIT |

## Important Transitive Runtime Dependencies

These are notable runtime dependencies pulled in indirectly, especially through `streamlit`.

| Package | Tested version | License |
| --- | ---: | --- |
| `altair` | `6.1.0` | BSD-style |
| `anyio` | `4.13.0` | MIT |
| `branca` | `0.8.2` | MIT |
| `certifi` | `2026.4.22` | MPL-2.0 |
| `click` | `8.3.3` | BSD-3-Clause |
| `GitPython` | `3.1.49` | BSD-3-Clause |
| `Jinja2` | `3.1.6` | BSD-style |
| `jsonschema` | `4.26.0` | MIT |
| `narwhals` | `2.20.0` | MIT |
| `packaging` | `26.2` | Apache-2.0 OR BSD-2-Clause |
| `pillow` | `12.2.0` | MIT-CMU |
| `protobuf` | `7.34.1` | BSD-3-Clause |
| `pyarrow` | `24.0.0` | Apache-2.0 |
| `pydeck` | `0.9.2` | Apache-2.0 |
| `python-dateutil` | `2.9.0.post0` | BSD / Apache dual license |
| `starlette` | `1.0.0` | BSD-3-Clause |
| `tenacity` | `9.1.4` | Apache-2.0 |
| `typing_extensions` | `4.15.0` | PSF-2.0 |
| `uvicorn` | `0.46.0` | BSD-3-Clause |
| `watchdog` | `6.0.0` | Apache-2.0 |
| `websockets` | `16.0` | BSD-3-Clause |
| `xyzservices` | `2026.3.0` | BSD-3-Clause |

## External Services, Data, and Public API Constraints

These are operational/legal constraints that matter for a public Streamlit deployment even though they are not Python package licenses.

### Open-Meteo

- Official terms page: [open-meteo.com/en/terms](https://open-meteo.com/en/terms)
- Relevant points checked on 2026-05-01:
  - the free API is described as `non-commercial use`;
  - usage limits are documented;
  - use is tied to `CC-BY 4.0` attribution requirements.

Practical meaning for this repository:

- Fine for a personal/public demo or non-commercial public app, assuming you respect attribution and rate limits.
- If you want to commercialize the app or deploy it as part of a paid product/service, review Open-Meteo's current commercial terms first.

### OpenStreetMap / Nominatim

- Official usage policy: [operations.osmfoundation.org/policies/nominatim](https://operations.osmfoundation.org/policies/nominatim/)
- Relevant points checked on 2026-05-01:
  - public API use must be light;
  - maximum public rate is documented as `1 request per second`;
  - a valid identifying `User-Agent` or `Referer` is required;
  - attribution is required;
  - OSM data is under `ODbL`.

Practical meaning:

- Good for modest public usage.
- Not appropriate to treat the public Nominatim instance as a heavy production geocoding backend.

### Overpass API

- Public instance guidance: [dev.overpass-api.de/overpass-doc/en/preface/commons.html](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html)
- Relevant points checked on 2026-05-01:
  - public instances defend themselves against overuse;
  - heavy users are expected to self-host or use another solution;
  - rate limiting and load shedding can happen.

Practical meaning:

- Reasonable for a personal/public app with moderate traffic.
- If traffic grows, plan to replace the public Overpass backend or precompute/cache more aggressively.

### OpenStreetMap Data License

- OSM data is generally provided under `ODbL`.
- That is not a blocker for your repository being MIT, but it does mean data attribution is required and share-alike obligations can matter depending on how much data is extracted, stored, transformed, or redistributed.

### CARTO Basemap Tiles

- The map UI already includes visible tile attribution for `OpenStreetMap` and `CARTO`.
- If the deployment becomes popular, review CARTO's current basemap terms and quotas before treating the public basemap endpoint as guaranteed infrastructure.

## Recommendation

For an MIT public GitHub repository and a public Streamlit demo app:

- `Software licensing`: acceptable.
- `Most restrictive software item found`: `certifi` under `MPL-2.0`, which is usually manageable and compatible in this context.
- `Main real-world constraints`: external service terms, attribution, and public API rate limits.

If you want the safest long-term public posture, especially for a higher-traffic or commercial deployment, the next steps would be:

1. keep visible attribution in the app and README;
2. keep this file updated when dependency versions change;
3. consider replacing public Nominatim/Overpass with your own backend or a commercial provider if traffic grows;
4. review Open-Meteo terms again before any commercial launch.
