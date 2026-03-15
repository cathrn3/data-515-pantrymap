"""Map components for the PantryMap Bokeh application."""

from bokeh.plotting import figure


def create_map(foodbank_df):
    """Create a Bokeh figure centered on Seattle-area points with robust bounds."""
    x_q_low = foodbank_df["x"].quantile(0.02)
    x_q_high = foodbank_df["x"].quantile(0.98)
    y_q_low = foodbank_df["y"].quantile(0.02)
    y_q_high = foodbank_df["y"].quantile(0.98)

    x_padding = (x_q_high - x_q_low) * 0.10
    y_padding = (y_q_high - y_q_low) * 0.10

    fig = figure(
        x_range=(x_q_low - x_padding, x_q_high + x_padding),
        y_range=(y_q_low - y_padding, y_q_high + y_padding),
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
