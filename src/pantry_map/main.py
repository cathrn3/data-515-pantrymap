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

from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
from pantry_map.data.loader import get_foodbank_df, get_transit_df
from pantry_map.components.map import add_markers, add_routes, create_map
from pantry_map.components.layout import (
    create_filter_bar,
    create_nearby_panel,
    create_layout,
    format_nearby_foodbanks,
)

from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, TapTool
from pantry_map.data.loader import get_foodbank_df, get_shapes_df, get_transit_df, get_transfers_df
from pantry_map.components.map import (
    add_markers, add_routes, create_map, update_route, clear_routes
)
from pantry_map.components.layout import create_sidebar, create_layout, format_foodbank_list
main
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.services.route import CalculateRoute
from pantry_map.utilities.utility import (
    calculate_distance,
    validate_address,
    geocode_address,
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

map_fig = create_map(foodbank_df)
add_routes(map_fig, transit_source)
add_markers(map_fig, foodbank_source, view=foodbank_view)

filter_bar, filter_widgets = create_filter_bar()
nearby_panel, nearby_widgets = create_nearby_panel()

resource_type_selector = filter_widgets['resource_type_selector']
distance_slider = filter_widgets['distance_slider']
open_only_toggle = filter_widgets['open_only_toggle']
eligibility_group = filter_widgets['eligibility_group']
day_group = filter_widgets['day_group']
address_input = filter_widgets['address_input']
search_button = filter_widgets['search_button']
clear_button = filter_widgets['clear_button']
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
foodbank_markers = add_markers(
    map_fig, user_source, foodbank_highlight_source, foodbank_source, foodbank_view
)
taptool = map_fig.select_one(TapTool)
if taptool is not None:
    taptool.renderers = [foodbank_markers]


# 2. Setup Side Panel
sidebar_layout, sidebar_widgets = create_sidebar()
resource_type_selector = sidebar_widgets['resource_type_selector']
distance_slider = sidebar_widgets['distance_slider']
open_only_toggle = sidebar_widgets['open_only_toggle']
eligibility_group = sidebar_widgets['eligibility_group']
day_group = sidebar_widgets['day_group']
address_input = sidebar_widgets['address_input']
search_button = sidebar_widgets['search_button']
clear_button = sidebar_widgets['clear_button']
location_list = sidebar_widgets['location_list']
results_div = sidebar_widgets['results_div']
main

user_location = {"lat": None, "lon": None}

def _selected_labels(checkbox_group):
    return [checkbox_group.labels[idx] for idx in checkbox_group.active]


# 3. Callbacks
def update():
    """Update the map view and sidebar list based on all active filters."""
    labels = list(resource_type_selector.labels)
    active = resource_type_selector.active
    if active is None:
        if "Both" in labels:
            resource_type = "Both"
        elif labels:
            resource_type = labels[0]
        else:
            resource_type = None
    else:
        resource_type = labels[int(active)]
    open_only = bool(open_only_toggle.active)
    selected_eligibility = _selected_labels(eligibility_group)
    selected_days = _selected_labels(day_group)

    # First, apply non-distance-based filters.
    # We intentionally do not pass user_lat/user_lon/max_distance_miles here
    # so that distance is not recomputed inside get_foodbank_mask.
    foodbank_mask = get_foodbank_mask(
        foodbank_df,
        resource_type=resource_type,
        open_only=open_only,
        selected_eligibility=selected_eligibility,
        selected_days=selected_days,
        user_lat=None,
        user_lon=None,
        max_distance_miles=None,
    )

    # Optionally refine by distance from the user, computing distances once.
    distances = None
    if (
        user_location["lat"] is not None
        and user_location["lon"] is not None
        and not foodbank_df.empty
    ):
        # Compute distance for all rows once.
        distances = foodbank_df.apply(
            lambda row: calculate_distance(
                user_location["lat"],
                user_location["lon"],
                row["Latitude"],
                row["Longitude"],
            ),
            axis=1,
        )
        # Apply distance threshold from the slider.
        distance_mask = distances <= distance_slider.value
        combined_mask = foodbank_mask & distance_mask
    else:
        combined_mask = foodbank_mask

    foodbank_view.filter = BooleanFilter(combined_mask.tolist())

    filtered_df = foodbank_df[combined_mask].copy()

    if (
        distances is not None
        and not filtered_df.empty
    ):
        # Attach precomputed distances for the filtered rows and sort by distance.
        filtered_df["distance"] = distances[combined_mask]
        filtered_df = filtered_df.sort_values("distance")
    else:
        filtered_df = filtered_df.sort_values("Agency")

    nearby_widgets["location_list"].text = format_nearby_foodbanks(filtered_df)
    foodbank_view.filter = BooleanFilter(foodbank_mask.tolist())
    location_list.text = format_foodbank_list(foodbank_df[foodbank_mask].head(20))

    # Clear highlight and route if the selected food bank is no longer visible
    selected = foodbank_source.selected.indices
    if selected and not foodbank_mask[selected[0]]:
        clear_routes(foodbank_highlight_source, foodbank_source, route_source)

main

def on_search_click():
    """Handle click event for the search button.

    1. Validate address input
    2. Geocode address to find longitude and latitude
    3. Place user marker on the map
    4. Apply all filters including distance from the entered address
    """
    address = address_input.value
    is_valid, msg, validated_address = validate_address(address)

    if not is_valid:

        filter_widgets["results_div"].text = f"<p style='color:red'>{msg}</p>"

        results_div.text = f"<p style='color:red'>{msg}</p>"
main
        return

    filter_widgets["results_div"].text = ""

    lat, lon = geocode_address(validated_address)
    if lat is None or lon is None:

        filter_widgets["results_div"].text = "<p style='color:red'>Could not find this address. Please try again.</p>"

        results_div.text = "<p style='color:red'>Could not find this address. Please try again.</p>"
 main
        return

    clear_routes(foodbank_highlight_source, foodbank_source, route_source)
    user_x, user_y = lat_lon_to_mercator(lat, lon)
    user_source.data = {
        "x": [user_x],
        "y": [user_y]
    }

    user_location["lat"] = lat
    user_location["lon"] = lon
    route_planner.set_user_location((lat, lon))
    update()

    filter_widgets["results_div"].text = "<p style='color:green'>Address validated. Results updated.</p>"


    sidebar_widgets["results_div"].text = (
        "<p style='color:green'>Address validated. Results updated.</p>"
    )
main


def on_address_change(attr, old, new):
    """Clear stored user location when the address text changes."""
    del attr, old, new
    # Clear stored user location when the address text changes so that
    # subsequent filter updates do not use a stale location.
    user_location["lat"] = None
    user_location["lon"] = None
    filter_widgets["results_div"].text = ""


def on_clear_click():
    """Handle click event for clear.

    1. Resets map
    2. Clears input in search bar
    """
    # Reset map markers to show all foodbanks
    user_location["lat"] = None
    user_location["lon"] = None

    # Clear the address input box
    address_input.value = ""
    results_div.text = ""
    update()

    # Clear results message
    filter_widgets["results_div"].text = ""

    # Clear rendered routes from user to food bank
    route_planner.set_user_location(None)
    user_location["lat"] = None
    user_location["lon"] = None
    user_source.data = {"x": [], "y": []}
    clear_routes(foodbank_highlight_source, foodbank_source, route_source)


def marker_callback(attr, old, new):
    """Handle tap selection on a food bank marker."""
    del attr, old
    if not new:
        clear_routes(foodbank_highlight_source, foodbank_source, route_source)
        location_list.text = format_foodbank_list(
            foodbank_df[foodbank_view.filter.booleans].head(20)
        )
        return

    # Route to the first selected marker; show all selected in the sidebar
    idx = new[0]

    foodbank_loc = (
        foodbank_source.data["x"][idx],
        foodbank_source.data["y"][idx]
    )
    foodbank_id = foodbank_source.data["bank_id"][idx]
    est_time, route = route_planner.get_route_to_destination(foodbank_id)
    sidebar_widgets["results_div"].text = f"Estimated travel time: {est_time}"
    update_route(route, foodbank_loc, shapes_df, foodbank_highlight_source, route_source)

    selected_rows = foodbank_df.iloc[new]
    location_list.text = format_foodbank_list(selected_rows)


# 4. Wire up callbacks
resource_type_selector.on_change("active", lambda attr, old, new: update())
distance_slider.on_change("value", lambda attr, old, new: update())
open_only_toggle.on_change("active", lambda attr, old, new: update())
eligibility_group.on_change("active", lambda attr, old, new: update())
day_group.on_change("active", lambda attr, old, new: update())
address_input.on_change("value", on_address_change)
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)
foodbank_source.selected.on_change("indices", marker_callback)  # pylint: disable=no-member

update()

layout = create_layout(map_fig, filter_bar, nearby_panel)

# Initial population
update()
 main

# 5. Assemble Layout
layout = create_layout(map_fig, sidebar_layout)
curdoc().add_root(layout)
curdoc().title = "PantryMap"
