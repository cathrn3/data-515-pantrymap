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
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        toolbar_location="above",
        background_fill_color="#fafbfc",
        border_fill_color="#fafbfc",
        outline_line_color="#e5e7eb",
        sizing_mode="scale_width",
    )
    fig.add_tile("CartoDB Positron")
    return fig


def add_markers(fig, source, view=None):
    """Add food bank markers."""
    return fig.circle(
        x="x",
        y="y",
        size=10,
        alpha=0.85,
        source=source,
        line_width=2,
        view=view,
    )


def add_routes(fig, source):
    """Add transit route polylines."""
    return fig.multi_line(
        xs="x",
        ys="y",
        color="color",
        source=source,
        line_width=2,
    )
