from sunny_places.models import GeoPoint, ViewState


def get_default_view_state() -> ViewState:
    return ViewState(
        center=GeoPoint(latitude=43.2630, longitude=-2.9350),
        zoom=12.0,
        locale="es",
        theme="dark",
    )
