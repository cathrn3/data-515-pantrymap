"""
Main entry point for the PantryMap Bokeh application.

This module initializes the application, loads data, sets up the sidebar widgets,
and defines the callbacks for user interactions like filtering and searching.
"""

import os
import sys

# Add the 'src' directory to the path so that imports work regardless of where you run it
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

# pylint: disable=wrong-import-position
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, TapTool
from pantry_map.data.loader import get_foodbank_df, get_shapes_df, get_transit_df, get_transfers_df
from pantry_map.components.map import add_markers, add_routes, create_map, update_route, clear_routes
from pantry_map.components.layout import create_sidebar, create_layout, format_foodbank_list
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.services.route import CalculateRoute
from pantry_map.utilities.utility import (
    validate_address,
    geocode_address,
    find_nearest_foodbanks,
    lat_lon_to_mercator,
)

# 1. Load Data
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

route_planner = CalculateRoute(foodbank_df, transit_df, transfers_df)

x_min, x_max = foodbank_df['x'].min(), foodbank_df['x'].max()
y_min, y_max = foodbank_df['y'].min(), foodbank_df['y'].max()

map_fig = create_map(x_min, x_max, y_min, y_max)
add_routes(map_fig, grouped_shapes_source, route_source)
foodbank_markers = add_markers(map_fig, user_source, foodbank_highlight_source, foodbank_source, foodbank_view)
taptool = map_fig.select_one(TapTool)
if taptool is not None:
    taptool.renderers = [foodbank_markers]

# 2. Setup Side Panel
sidebar_layout, sidebar_widgets = create_sidebar()
resource_types = sidebar_widgets['resource_type_selector']
distance_slider = sidebar_widgets['distance_slider']
open_only_toggle = sidebar_widgets['open_only_toggle']
eligibility_group = sidebar_widgets['eligibility_group']
day_group = sidebar_widgets['day_group']
address_input = sidebar_widgets['address_input']
search_button = sidebar_widgets['search_button']
clear_button = sidebar_widgets['clear_button']
results_div = sidebar_widgets['results_div']
location_list = sidebar_widgets['location_list']

user_location = {"lat": None, "lon": None}


# 3. Callbacks
def update():
    """Update the map view and sidebar list based on all active filters."""
    labels = list(resource_types.labels)
    active = resource_types.active
    resource_type = labels[int(active)] if active is not None else "Both"
    open_only = bool(open_only_toggle.active)
    selected_eligibility = [eligibility_group.labels[i] for i in eligibility_group.active]
    selected_days = [day_group.labels[i] for i in day_group.active]

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
    location_list.text = format_foodbank_list(foodbank_df[foodbank_mask].head(20))


def on_search_click():
    """Handle click event for the search button.

    1. Validate address input
    2. Geocode address to find longitude and latitude
    3. Highlight user's location on the map
    4. Calculate 30 nearest foodbanks
    """
    address = address_input.value
    is_valid, msg, validated_address = validate_address(address)

    if not is_valid:
        results_div.text = f"<p style='color:red'>{msg}</p>"
        return

    sidebar_widgets["results_div"].text = ""

    lat, lon = geocode_address(validated_address)
    if lat is None or lon is None:
        results_div.text = "<p style='color:red'>Could not find this address. Please try again.</p>"
        return

    clear_routes(foodbank_highlight_source, foodbank_source, route_source)
    user_x, user_y = lat_lon_to_mercator(lat, lon)
    user_source.data = {
        "x": [user_x],
        "y": [user_y]
    }

    # Highlight nearest markers on the map
    nearest_df = find_nearest_foodbanks(foodbank_df, lat, lon, k=30)
    nearest_mask = foodbank_df.index.isin(nearest_df.index)
    foodbank_view.filter = BooleanFilter(nearest_mask.tolist())

    user_location["lat"] = lat
    user_location["lon"] = lon
    route_planner.set_user_location((lat, lon))


def on_address_change(attr, old, new):
    """Clear stored user location when the address text changes."""
    del attr, old, new
    user_location["lat"] = None
    user_location["lon"] = None
    sidebar_widgets["results_div"].text = ""


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
    user_location["lat"] = None
    user_location["lon"] = None
    user_source.data = {"x": [], "y": []}
    clear_routes(foodbank_highlight_source, foodbank_source, route_source)


def marker_callback(attr, old, new):
    """Handle tap selection on a food bank marker."""
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
    sidebar_widgets["results_div"].text = f"Estimated travel time: {est_time}"
    update_route(route, foodbank_loc, shapes_df, foodbank_highlight_source, route_source)


# 4. Wire up callbacks
resource_types.on_change("active", lambda attr, old, new: update())
distance_slider.on_change("value", lambda attr, old, new: update())
open_only_toggle.on_change("active", lambda attr, old, new: update())
eligibility_group.on_change("active", lambda attr, old, new: update())
day_group.on_change("active", lambda attr, old, new: update())
address_input.on_change("value", on_address_change)
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)
foodbank_source.selected.on_change("indices", marker_callback)

# Initial population
update()

# 5. Assemble Layout
layout = create_layout(map_fig, sidebar_layout)
curdoc().add_root(layout)
curdoc().title = "PantryMap"
