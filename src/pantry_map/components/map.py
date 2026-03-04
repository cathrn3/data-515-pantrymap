from bokeh.plotting import figure

def create_map(x_min, x_max, y_min, y_max):
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
    return fig.multi_line(
        xs="x",
        ys="y",
        color="color",
        source=source,
        line_width=2
    )