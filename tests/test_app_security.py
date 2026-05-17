from __future__ import annotations

import pytest

import app
from sunny_places.models import CandidatePlace


def test_selected_place_card_escapes_external_place_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered_html: list[str] = []

    def fake_markdown(body: str, *, unsafe_allow_html: bool) -> None:
        rendered_html.append(body)

    monkeypatch.setattr(app.st, "markdown", fake_markdown)
    monkeypatch.setattr(app.st, "caption", lambda text: None)
    monkeypatch.setattr(app, "translate", lambda key: key)
    monkeypatch.setattr(app, "current_score_label", lambda: "Score")

    place = CandidatePlace(
        name="<img src=x onerror=alert(1)>",
        latitude=43.0,
        longitude=-2.0,
        category="<script>alert(1)</script>",
        score=50.0,
        distance_m=12.0,
    )

    app.render_selected_place_card(place)

    assert rendered_html
    assert "<img src=x onerror=alert(1)>" not in rendered_html[0]
    assert "<script>alert(1)</script>" not in rendered_html[0]
    assert "&lt;img src=x onerror=alert(1)&gt;" in rendered_html[0]
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered_html[0]
