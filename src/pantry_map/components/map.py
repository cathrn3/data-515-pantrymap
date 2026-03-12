from bokeh.plotting import figure
from bokeh.models import HoverTool
from pantry_map.utilities.utility import lat_lon_to_mercator

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
    markers = fig.circle(
        x='x',
        y='y',
        size=10,
        alpha=0.85,
        source=source,
        line_width=2,
        view=view
    )
    
    # Add a hover tool to show the 'id' field
    hover = HoverTool(
        tooltips=[
            ("bank_id", "@bank_id") 
        ],
        renderers=[markers]
    )
    
    fig.add_tools(hover)
    return markers

def add_routes(fig, source):
    return fig.multi_line(
        xs="x",
        ys="y",
        color="color",
        source=source,
        line_width=2,
        alpha=.25
    )


def add_stops(fig, user_location, route, foodbank_loc, source):
    # Plot user and food bank
    circle_x, circle_y = lat_lon_to_mercator(user_location[0], user_location[1]) # TODO: remove
    food_x, food_y = lat_lon_to_mercator(foodbank_loc[0], foodbank_loc[1])
    fig.circle(circle_x, circle_y, size=20, color='red')
    fig.circle(food_x, food_y, size=20, color='green')
    if not route:
        return fig #TODO: Display error

    highlight_df = source[
        source['unique_key'].isin(route[1:-1])
    ]

    grouped = highlight_df.groupby(['route_id'])

    xs = []
    ys = []
    colors = []

    for _, group in grouped:
        start_idx = group.index.min()
        end_idx = group.index.max()
        segment = source.loc[start_idx:end_idx].copy()

        xs.append(segment['x'].tolist())
        ys.append(segment['y'].tolist())
        colors.append(segment['color'].values[0])

    fig.multi_line(
        xs=xs,
        ys=ys,
        line_color=colors,
        line_width=5
    )
    return fig

