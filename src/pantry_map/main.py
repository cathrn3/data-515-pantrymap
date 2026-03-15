from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, TapTool
from pantry_map.data.loader import get_foodbank_df, get_shapes_df, get_transit_df, get_transfers_df
from pantry_map.components.map import add_markers, add_routes, create_map, update_route, clear_routes
from pantry_map.components.layout import create_sidebar, create_layout
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.services.route import calculateRoute
from pantry_map.utilities.utility import validate_address, geocode_address, find_nearest_foodbanks, lat_lon_to_mercator

shapes_df, grouped_shapes_df = get_shapes_df()
grouped_shapes_source = ColumnDataSource(grouped_shapes_df)

transit_df = get_transit_df()
transfers_df = get_transfers_df()

foodbank_df = get_foodbank_df()
foodbank_initial_mask = [True] * len(foodbank_df)
foodbank_source = ColumnDataSource(foodbank_df)
foodbank_view = CDSView(filter=BooleanFilter(foodbank_initial_mask))

# Initialize drawn sources
user_source = ColumnDataSource({"x": [], "y": []})
foodbank_highlight_source = ColumnDataSource({"x": [], "y": []})
route_source = ColumnDataSource({
    "xs": [],
    "ys": [],
    "color": []
})

route_planner = calculateRoute(foodbank_df, transit_df, transfers_df)

x_min, x_max = foodbank_df['x'].min(), foodbank_df['x'].max()
y_min, y_max = foodbank_df['y'].min(), foodbank_df['y'].max()

map_fig = create_map(x_min, x_max, y_min, y_max)
add_routes(map_fig, grouped_shapes_source, route_source)
foodbank_markers = add_markers(map_fig, user_source, foodbank_highlight_source, foodbank_source, foodbank_view)
taptool = TapTool(renderers=[foodbank_markers])
map_fig.add_tools(taptool)

sidebar_layout, sidebar_widgets = create_sidebar(foodbank_df)
resource_types = sidebar_widgets['resource_type_dropdown']
address_input = sidebar_widgets['address_input']
search_button = sidebar_widgets['search_button']
clear_button = sidebar_widgets['clear_button']

def update():
    # Update the displayed view instead of modifying the underlying data
    foodbank_mask = get_foodbank_mask(foodbank_df, resource_types)
    foodbank_view.filter = BooleanFilter(foodbank_mask.tolist())

# Search button callback
def on_search_click():
    """
    Handle click event for the search button.
    
    1. Validate address input
    2. Geocode address to find longitude and latitude
    3. Highlight user's location
    4. Calculate 5 nearest foodbanks
    """

    # validate address input
    address = address_input.value
    is_valid, msg, validated_address = validate_address(address)

    if not is_valid:
        sidebar_widgets["results_div"].text = f"<p style='color:red'>{msg}</p>"
        return
    
    # get lat and lon
    lat, lon = geocode_address(validated_address)
    if lat is None or lon is None:
        sidebar_widgets["results_div"].text = "<p style='color:red'>Could not find this address. Please try again.</p>"
        return

    clear_routes(foodbank_highlight_source, foodbank_source, route_source)
    user_x, user_y = lat_lon_to_mercator(lat, lon)
    user_source.data = {
        "x": [user_x],
        "y": [user_y]
    }
    
    # calc nearest foodbanks
    nearest_df = find_nearest_foodbanks(foodbank_df, lat, lon, k=30)
    
    # highlight nearest markers on the map
    nearest_mask = foodbank_df.index.isin(nearest_df.index)
    foodbank_view.filter = BooleanFilter(nearest_mask.tolist())

    route_planner.set_user_location((lat, lon))

def on_clear_click():
    """Handle click event for clear.
    
    1. Resets map
    2. Clears input in search bar
    """

    # Reset map markers to show all foodbanks
    reset_mask = [True] * len(foodbank_df)
    foodbank_view.filter = BooleanFilter(reset_mask)

    # Clear the address input box
    address_input.value = ""

    # Clear results message
    sidebar_widgets["results_div"].text = ""

    # Clear rendered routes from user to food bank
    route_planner.set_user_location(None)
    user_source.data = {"x": [], "y": []}
    clear_routes(foodbank_highlight_source, foodbank_source, route_source)

def marker_callback(attr, old, new):
    if not new:
        clear_routes(foodbank_highlight_source, foodbank_source, route_source)
        return

    # Only get one marker if multiple were selected
    idx = new[0]

    foodbank_loc = (
        foodbank_source.data["x"][idx],
        foodbank_source.data["y"][idx]
    )
    foodbank_id = foodbank_source.data["bank_id"][idx]
    est_time, route = route_planner.get_route_to_destination(foodbank_id)
    print(est_time) # TODO: render this
    update_route(route, foodbank_loc, shapes_df, foodbank_highlight_source, route_source)


resource_types.on_change("value", lambda attr, old, new: update())
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)
foodbank_source.selected.on_change("indices", marker_callback)

layout = create_layout(
    map_fig,
    sidebar_layout
)

curdoc().add_root(layout)
curdoc().title = "PantryMap"
