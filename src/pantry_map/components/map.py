"""Map components for the PantryMap Bokeh application."""

from bokeh.plotting import figure
import math


def create_map(foodbank_df):
    """Create a Bokeh figure centered on Seattle-area points with robust bounds."""
    # Default to a Seattle-area Web Mercator bounding box if data are missing/invalid.
    # These values approximate the Seattle metro region.
    default_x_min, default_x_max = -13650000, -13590000
    default_y_min, default_y_max = 6040000, 6090000

    # Drop NaNs before computing quantiles.
    x_series = foodbank_df["x"].dropna()
    y_series = foodbank_df["y"].dropna()

    def _compute_axis_bounds(series, default_min, default_max):
        """Compute robust low/high bounds for a coordinate axis."""
        if series.empty:
            return default_min, default_max

        q_low = series.quantile(0.02)
        q_high = series.quantile(0.98)

        # If quantiles are non-finite or degenerate, fall back to min/max.
        if (
            not (isinstance(q_low, (int, float)) and isinstance(q_high, (int, float)))
            or not (math.isfinite(q_low) and math.isfinite(q_high))
            or q_high <= q_low
        ):
            s_min = series.min()
            s_max = series.max()
            if (
                not (isinstance(s_min, (int, float)) and isinstance(s_max, (int, float)))
                or not (math.isfinite(s_min) and math.isfinite(s_max))
                or s_max <= s_min
            ):
                # If even min/max are unusable, fall back to defaults.
                return default_min, default_max

            span = s_max - s_min
            padding = span * 0.10 if span > 0 else max(abs(s_min), 1.0) * 0.05
            return s_min - padding, s_max + padding

        span = q_high - q_low
        padding = span * 0.10 if span > 0 else max(abs(q_low), 1.0) * 0.05
        return q_low - padding, q_high + padding

    x_min, x_max = _compute_axis_bounds(x_series, default_x_min, default_x_max)
    y_min, y_max = _compute_axis_bounds(y_series, default_y_min, default_y_max)

    fig = figure(
        x_range=(x_min, x_max),
        y_range=(y_min, y_max),
        x_axis_type="mercator",
        y_axis_type="mercator",
        width=1000,
        height=550,
        tools="pan,wheel_zoom,box_zoom,reset,save,tap",
        active_scroll="wheel_zoom",
        toolbar_location="above",
        background_fill_color="#fafbfc",
        border_fill_color="#fafbfc",
        outline_line_color="#e5e7eb",
        sizing_mode="scale_width",
    )
    fig.add_tile("CartoDB Positron")
    return fig


def add_markers(fig, user_source, foodbank_highlight_source, foodbank_source, foodbank_view=None):
    """Add food bank, highlight, and user location markers to the map figure.

    Args:
        fig (figure): The Bokeh figure to add markers to.
        user_source (ColumnDataSource): Data source for the user location marker.
        foodbank_highlight_source (ColumnDataSource): Data source for highlighted foodbank markers.
        foodbank_source (ColumnDataSource): Data source for all foodbank markers.
        foodbank_view (CDSView, optional): A view to filter the foodbank data source.

    Returns:
        GlyphRenderer: The foodbank marker glyph renderer (used for TapTool targeting).
    """
    fig.circle(
        x="x",
        y="y",
        size=15,
        color="blue",
        fill_color="white",
        source=foodbank_highlight_source,
    )

    foodbank_markers = fig.circle(
        x="x",
        y="y",
        size=10,
        alpha=0.85,
        source=foodbank_source,
        line_width=2,
        view=foodbank_view,
    )

    fig.circle(
        x="x",
        y="y",
        size=15,
        color="red",
        source=user_source,
    )

    return foodbank_markers


def add_routes(fig, grouped_shapes_source, route_source):
    """Add transit route polylines and calculated-route overlay to the map figure.

    Args:
        fig (figure): The Bokeh figure to add routes to.
        grouped_shapes_source (ColumnDataSource): Data source for transit shape routes.
        route_source (ColumnDataSource): Data source for the active calculated route.
    """
    fig.multi_line(
        xs="x",
        ys="y",
        color="color",
        source=grouped_shapes_source,
        line_width=2,
        alpha=0.25,
    )

    fig.multi_line(
        xs="xs",
        ys="ys",
        line_color="color",
        line_width=5,
        source=route_source,
    )


def update_route(route, foodbank_loc, shapes_df, foodbank_highlight_source, route_source):
    """Update the highlighted food bank marker and draw the transit route.

    Args:
        route (list): List of stop/node keys along the route.
        foodbank_loc (tuple): (x, y) Mercator coordinates of the destination food bank.
        shapes_df (pd.DataFrame): Full transit shapes dataframe for segment lookup.
        foodbank_highlight_source (ColumnDataSource): Data source for highlighted foodbank marker.
        route_source (ColumnDataSource): Data source for the drawn route polylines.
    """
    foodbank_highlight_source.data = {
        "x": [foodbank_loc[0]],
        "y": [foodbank_loc[1]],
    }

    if not route:
        route_source.data = {"xs": [], "ys": [], "color": []}
        return

    highlight_df = shapes_df[shapes_df["unique_key"].isin(route[1:-1])]
    grouped = highlight_df.groupby("route_id")

    xs = []
    ys = []
    colors = []

    for _, group in grouped:
        start_idx = group.index.min()
        end_idx = group.index.max()
        segment = shapes_df.loc[start_idx:end_idx]
        xs.append(segment["x"].tolist())
        ys.append(segment["y"].tolist())
        colors.append(segment["color"].iloc[0])

    route_source.data = {"xs": xs, "ys": ys, "color": colors}


def clear_routes(foodbank_highlight_source, foodbank_source, route_source):
    """Clear the highlighted food bank marker and any drawn route.

    Args:
        foodbank_highlight_source (ColumnDataSource): Data source for highlighted foodbank marker.
        foodbank_source (ColumnDataSource): Data source for all foodbank markers.
        route_source (ColumnDataSource): Data source for the drawn route polylines.
    """
    foodbank_highlight_source.data = {"x": [], "y": []}
    foodbank_source.selected.indices = []
    route_source.data = {"xs": [], "ys": [], "color": []}
