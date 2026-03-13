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
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll='wheel_zoom',
        toolbar_location="above",
        background_fill_color='#fafbfc',
        border_fill_color='#fafbfc',
        outline_line_color='#e5e7eb',
        sizing_mode="scale_width"
    )
    fig.add_tile("CartoDB Positron")

    return fig

def add_markers(fig, source, view=None):
    """
    Add circle markers to the provided Bokeh figure.

    Args:
        fig (figure): The Bokeh figure to add markers to.
        source (ColumnDataSource): The data source for the markers.
        view (CDSView, optional): A view to filter the data source.

    Returns:
        GlyphRenderer: The resulting Bokeh glyph renderer.
    """
    return fig.circle(
        x='x',
        y='y',
        size=10,
        alpha=0.85,
        source=source,
        line_width=2,
        view=view
    )

def add_routes(fig, source):
    """
    Add multi-line routes to the provided Bokeh figure.

    Args:
        fig (figure): The Bokeh figure to add routes to.
        source (ColumnDataSource): The data source for the routes.

    Returns:
        GlyphRenderer: The resulting Bokeh glyph renderer.
    """
    return fig.multi_line(
        xs="x",
        ys="y",
        color="color",
        source=source,
        line_width=2
    )
