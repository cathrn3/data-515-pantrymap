from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
from pantry_map.data.loader import get_foodbank_df, get_transit_df
from pantry_map.components.map import add_markers, add_routes, create_map
from pantry_map.components.layout import create_sidebar, create_layout
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.utilities.utility import (
    validate_address,
    geocode_address,
)

transit_df = get_transit_df()
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
resource_type_selector = sidebar_widgets['resource_type_selector']
distance_slider = sidebar_widgets['distance_slider']
open_only_toggle = sidebar_widgets['open_only_toggle']
eligibility_group = sidebar_widgets['eligibility_group']
day_group = sidebar_widgets['day_group']
address_input = sidebar_widgets['address_input']
search_button = sidebar_widgets['search_button']
clear_button = sidebar_widgets['clear_button']

user_location = {"lat": None, "lon": None}


def _selected_labels(checkbox_group):
    return [checkbox_group.labels[idx] for idx in checkbox_group.active]


def update():
    resource_type = resource_type_selector.labels[resource_type_selector.active]
    open_only = 0 in open_only_toggle.active
    selected_eligibility = _selected_labels(eligibility_group)
    selected_days = _selected_labels(day_group)

    foodbank_mask = get_foodbank_mask(
        foodbank_df,
        resource_type=resource_type,
        open_only=open_only,
        selected_eligibility=selected_eligibility,
        selected_days=selected_days,
        user_lat=user_location["lat"],
        user_lon=user_location["lon"],
        max_distance_miles=distance_slider.value,
    )
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
    is_valid, msg, normalized_address = validate_address(address)

    if not is_valid:
        sidebar_widgets["results_div"].text = f"<p style='color:red'>{msg}</p>"
        return

    sidebar_widgets["results_div"].text = ""

    # get lat and lon
    lat, lon = geocode_address(normalized_address)
    if lat is None or lon is None:
        sidebar_widgets["results_div"].text = "<p style='color:red'>Could not find this address. Please try again.</p>"
        return

    user_location["lat"] = lat
    user_location["lon"] = lon

    update()
    sidebar_widgets["results_div"].text = "<p style='color:green'>Address validated. Results updated.</p>"


def on_address_change(attr, old, new):
    del attr, old, new
    sidebar_widgets["results_div"].text = ""

def on_clear_click():
    """Handle click event for clear.
    
    1. Resets map
    2. Clears input in search bar
    """

    # Reset map markers to show all foodbanks
    user_location["lat"] = None
    user_location["lon"] = None
    update()

    # Clear the address input box
    address_input.value = ""

    # Clear results message
    sidebar_widgets["results_div"].text = ""

resource_type_selector.on_change("active", lambda attr, old, new: update())
distance_slider.on_change("value", lambda attr, old, new: update())
open_only_toggle.on_change("active", lambda attr, old, new: update())
eligibility_group.on_change("active", lambda attr, old, new: update())
day_group.on_change("active", lambda attr, old, new: update())
address_input.on_change("value", on_address_change)
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)

layout = create_layout(
    map_fig,
    sidebar_layout
)

curdoc().add_root(layout)
curdoc().title = "PantryMap"
