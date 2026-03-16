"""
Main entry point for the PantryMap Bokeh application.

This module initializes the application, loads data, sets up the sidebar widgets,
and defines the callbacks for user interactions like filtering and searching.
"""

import os
import sys

import numpy as np

# Add the 'src' directory to the path so that imports work regardless of where you run it
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

# pylint: disable=wrong-import-position
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, TapTool
from pantry_map.data.loader import get_foodbank_df, get_transit_df, get_shapes_df, get_transfers_df
from pantry_map.components.map import (
    add_markers, add_routes, create_map, update_route, clear_routes
)
from pantry_map.services.route import CalculateRoute
from pantry_map.components.layout import (
    create_filter_bar,
    create_search_bar,
    create_nearby_panel,
    create_layout,
    format_nearby_foodbanks,
)
from pantry_map.filters.mask import get_foodbank_mask
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

# Initialize drawn sources
user_source = ColumnDataSource({"x": [], "y": []})
foodbank_highlight_source = ColumnDataSource({"x": [], "y": []})
route_source = ColumnDataSource({
    "xs": [],
    "ys": [],
    "color": []
})

route_planner = CalculateRoute(foodbank_df, transit_df, transfers_df)

# 2. Build Map
map_fig = create_map(foodbank_df)
add_routes(map_fig, grouped_shapes_source, route_source)
# Highlight circle rendered beneath food bank markers; user marker rendered on top
map_fig.circle(
    x="x", y="y", size=15, color="blue", fill_color="white",
    source=foodbank_highlight_source
)
foodbank_markers = add_markers(map_fig, foodbank_source, view=foodbank_view)
map_fig.circle(x="x", y="y", size=15, color="red", source=user_source)

taptool = map_fig.select_one(TapTool)
if taptool is not None:
    taptool.renderers = [foodbank_markers]

# 3. Setup Panels
filter_bar, filter_widgets = create_filter_bar()
search_bar, search_widgets = create_search_bar()
nearby_panel, nearby_widgets = create_nearby_panel()

resource_type_selector = filter_widgets['resource_type_selector']
distance_slider = search_widgets['distance_slider']
open_only_toggle = filter_widgets['open_only_toggle']
eligibility_group = filter_widgets['eligibility_group']
day_group = filter_widgets['day_group']
address_input = search_widgets['address_input']
search_button = search_widgets['search_button']
clear_button = search_widgets['clear_button']

user_location = {"lat": None, "lon": None}


def _selected_labels(checkbox_group):
    return [checkbox_group.labels[idx] for idx in checkbox_group.active]


def _safe_calculate_distance(user_lat, user_lon, row_lat, row_lon):
    """
    Safely compute distance, returning np.inf for any invalid/missing coordinates.
    """
    try:
        lat1 = float(user_lat)
        lon1 = float(user_lon)
        lat2 = float(row_lat)
        lon2 = float(row_lon)
    except (TypeError, ValueError):
        return np.inf

    if not (
        np.isfinite(lat1)
        and np.isfinite(lon1)
        and np.isfinite(lat2)
        and np.isfinite(lon2)
    ):
        return np.inf

    try:
        return calculate_distance(lat1, lon1, lat2, lon2)
    except (TypeError, ValueError, OverflowError):
        return np.inf


# 4. Callbacks
def update():
    """Update the map view and sidebar list based on all active filters."""
    labels = list(resource_type_selector.labels)
    active = resource_type_selector.active
    if active is None:
        resource_type = "Both" if "Both" in labels else (labels[0] if labels else None)
    else:
        resource_type = labels[int(active)]
    open_only = bool(open_only_toggle.active)
    selected_eligibility = list(eligibility_group.value)
    selected_days = list(day_group.value)

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

    # Clear highlight and route if the selected food bank is no longer visible
    selected = foodbank_source.selected.indices
    if selected and not foodbank_mask[selected[0]]:
        clear_routes(foodbank_highlight_source, foodbank_source, route_source)

    # Optionally refine by distance from the user, computing distances once
    distances = None
    if (
        user_location["lat"] is not None
        and user_location["lon"] is not None
        and not foodbank_df.empty
    ):
        distances = foodbank_df.apply(
            lambda row: _safe_calculate_distance(
                user_location["lat"],
                user_location["lon"],
                row["Latitude"],
                row["Longitude"],
            ),
            axis=1,
        )
        distance_mask = distances <= distance_slider.value
        combined_mask = foodbank_mask & distance_mask
    else:
        combined_mask = foodbank_mask

    foodbank_view.filter = BooleanFilter(combined_mask.tolist())

    # Don't overwrite the sidebar when a marker is selected — marker_callback owns it then
    if foodbank_source.selected.indices:
        return

    filtered_df = foodbank_df[combined_mask].copy()
    if distances is not None and not filtered_df.empty:
        filtered_df["distance"] = distances[combined_mask]
        filtered_df = filtered_df.sort_values("distance")
    else:
        filtered_df = filtered_df.sort_values("Agency")

    nearby_widgets["location_list"].text = format_nearby_foodbanks(filtered_df)


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
        search_widgets["results_div"].text = f"<p style='color:red'>{msg}</p>"
        return

    search_widgets["results_div"].text = ""

    lat, lon = geocode_address(validated_address)
    if lat is None or lon is None:
        search_widgets["results_div"].text = (
            "<p style='color:red'>Could not find this address. Please try again.</p>"
        )
        return

    clear_routes(foodbank_highlight_source, foodbank_source, route_source)
    user_x, user_y = lat_lon_to_mercator(lat, lon)
    user_source.data = {"x": [user_x], "y": [user_y]}

    user_location["lat"] = lat
    user_location["lon"] = lon
    route_planner.set_user_location((lat, lon))
    update()

    search_widgets["results_div"].text = (
        "<p style='color:green'>Address validated. Results updated.</p>"
    )


def on_address_change(attr, old, new):
    """Clear stored user location when the address text changes."""
    del attr, old, new
    user_location["lat"] = None
    user_location["lon"] = None
    search_widgets["results_div"].text = ""


def on_clear_click():
    """Handle click event for clear.

    1. Resets map
    2. Clears input in search bar
    """
    user_location["lat"] = None
    user_location["lon"] = None
    route_planner.set_user_location(None)
    user_source.data = {"x": [], "y": []}
    clear_routes(foodbank_highlight_source, foodbank_source, route_source)
    address_input.value = ""
    search_widgets["results_div"].text = ""
    update()


def marker_callback(attr, old, new):
    """Handle tap selection on a food bank marker."""
    del attr, old
    if not new:
        clear_routes(foodbank_highlight_source, foodbank_source, route_source)
        nearby_widgets["location_list"].text = format_nearby_foodbanks(
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
    _, route = route_planner.get_route_to_destination(foodbank_id)

    update_route(route, foodbank_loc, shapes_df, foodbank_highlight_source, route_source)

    selected_rows = foodbank_df.iloc[new]
    nearby_widgets["location_list"].text = format_nearby_foodbanks(selected_rows)


# 5. Wire up callbacks
resource_type_selector.on_change("active", lambda attr, old, new: update())
distance_slider.on_change("value", lambda attr, old, new: update())
open_only_toggle.on_change("active", lambda attr, old, new: update())
eligibility_group.on_change("value", lambda attr, old, new: update())
day_group.on_change("value", lambda attr, old, new: update())
address_input.on_change("value", on_address_change)
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)
foodbank_source.selected.on_change("indices", marker_callback)  # pylint: disable=no-member

# Initial population
update()

# 6. Assemble Layout
layout = create_layout(map_fig, filter_bar, search_bar, nearby_panel)
curdoc().add_root(layout)
curdoc().title = "PantryMap"
