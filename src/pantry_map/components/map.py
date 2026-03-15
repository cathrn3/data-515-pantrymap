"""
Map components for the PantryMap Bokeh application.

This module provides functions to create the Bokeh map figure and add
layers like markers and routes to the map.
"""

from bokeh.plotting import figure

def create_map(x_min, x_max, y_min, y_max):
    """
    Create a Bokeh figure with a Mercator tile background.

    Args:
        x_min (float): Minimum X coordinate (Mercator).
        x_max (float): Maximum X coordinate (Mercator).
        y_min (float): Minimum Y coordinate (Mercator).
        y_max (float): Maximum Y coordinate (Mercator).

    Returns:
        figure: A Bokeh figure object.
    """
    x_padding = (x_max - x_min) * 0.15
    y_padding = (y_max - y_min) * 0.15

    fig = figure(
        x_range=(x_min - x_padding, x_max + x_padding),
        y_range=(y_min - y_padding, y_max + y_padding),
        x_axis_type="mercator",
        y_axis_type="mercator",
        width=1000,
        height=550,
        tools="pan,wheel_zoom,box_zoom,reset,save,tap",
        active_scroll='wheel_zoom',
        toolbar_location="above",
        background_fill_color='#fafbfc',
        border_fill_color='#fafbfc',
        outline_line_color='#e5e7eb',
        sizing_mode="scale_width"
    )
    fig.add_tile("CartoDB Positron")

    return fig


def add_markers(fig, user_source, foodbank_highlight_source, foodbank_source, foodbank_view=None):
    """
    Add circle markers to the provided Bokeh figure.

    Args:
        fig (figure): The Bokeh figure to add markers to.
        user_source (ColumnDataSource): Data source for the user location marker.
        foodbank_highlight_source (ColumnDataSource): Data source for highlighted foodbank markers.
        foodbank_source (ColumnDataSource): Data source for all foodbank markers.
        foodbank_view (CDSView, optional): A view to filter the foodbank data source.

    Returns:
        GlyphRenderer: The foodbank marker glyph renderer.
    """
    _ = fig.circle(
        x="x",
        y="y",
        size=15,
        color="blue",
        fill_color="white",
        source=foodbank_highlight_source
    )

    foodbank_markers = fig.circle(
        x="x",
        y="y",
        size=10,
        alpha=0.85,
        source=foodbank_source,
        line_width=2,
        view=foodbank_view
    )

    _ = fig.circle(
        x="x",
        y="y",
        size=15,
        color="red",
        source=user_source
    )

    return foodbank_markers

def add_routes(fig, grouped_shapes_source, route_source):
    """
    Add multi-line routes to the provided Bokeh figure.

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
        alpha=.25
    )

    fig.multi_line(
        xs="xs",
        ys="ys",
        line_color="color",
        line_width=5,
        source=route_source
    )

def update_route(route, foodbank_loc, source, foodbank_highlight_source, route_source):
    foodbank_highlight_source.data = {
        "x": [foodbank_loc[0]],
        "y": [foodbank_loc[1]]
    }

    if not route:
        route_source.data = {"xs": [], "ys": [], "color": []} # TODO: render error
        return

    highlight_df = source[source["unique_key"].isin(route[1:-1])]
    grouped = highlight_df.groupby("route_id")

    xs = []
    ys = []
    colors = []

    # Render each route along the found path
    for _, group in grouped:
        # Select only the rows belonging to this route_id, without assuming
        # that they occupy a single contiguous index range in `source`.
        segment = source.loc[group.index].sort_index()

        xs.append(segment["x"].tolist())
        ys.append(segment["y"].tolist())
        colors.append(segment["color"].iloc[0])

    route_source.data = {
        "xs": xs,
        "ys": ys,
        "color": colors
    }

def clear_routes(foodbank_highlight_source, foodbank_source, route_source):
    foodbank_highlight_source.data = {"x": [], "y": []}
    foodbank_source.selected.indices = []
    route_source.data = {
        "xs": [],
        "ys": [],
        "color": []
    }