from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
from pantry_map.data.loader import get_foodbank_df, get_shapes_df
from pantry_map.components.map import add_markers, add_routes, create_map
from pantry_map.components.layout import create_sidebar, create_layout
from pantry_map.filters.mask import get_foodbank_mask

transit_df = get_shapes_df()
transit_source = ColumnDataSource(transit_df)

foodbank_df = get_foodbank_df()
foodbank_initial_mask = [True] * len(foodbank_df)
foodbank_source = ColumnDataSource(foodbank_df)
foodbank_view = CDSView(filter=BooleanFilter(foodbank_initial_mask))

x_min, x_max = foodbank_df['x'].min(), foodbank_df['x'].max()
y_min, y_max = foodbank_df['y'].min(), foodbank_df['y'].max()

map_fig = create_map(x_min, x_max, y_min, y_max)
add_routes(map_fig, transit_source)
add_markers(map_fig, foodbank_source, view=foodbank_view)

sidebar_layout, sidebar_widgets = create_sidebar(foodbank_df)
resource_types = sidebar_widgets['resource_type_dropdown']

def update():
    # Update the displayed view instead of modifying the underlying data
    foodbank_mask = get_foodbank_mask(foodbank_df, resource_types)
    foodbank_view.filter = BooleanFilter(foodbank_mask.tolist())

resource_types.on_change("value", lambda attr, old, new: update())

layout = create_layout(
    map_fig,
    sidebar_layout
)

curdoc().add_root(layout)
curdoc().title = "PantryMap"
