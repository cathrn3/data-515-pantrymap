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

from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
#from pantry_map.data.loader import get_foodbank_df, get_transit_df, get_shapes_df
from pantry_map.data.loader import get_foodbank_df, get_shapes_df
from pantry_map.components.map import add_markers, add_routes, create_map
from pantry_map.components.layout import (
    create_filter_bar,
    create_nearby_panel,
    create_layout,
    format_nearby_foodbanks,
)
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.utilities.utility import (
    calculate_distance,
    validate_address,
    geocode_address,
)

# 1. Load Data
transit_shapes_df = get_shapes_df()
transit_source = ColumnDataSource(transit_shapes_df)

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

user_location = {"lat": None, "lon": None}

def _selected_labels(checkbox_group):
    return [checkbox_group.labels[idx] for idx in checkbox_group.active]


def _safe_calculate_distance(user_lat, user_lon, row_lat, row_lon):
    """
    Safely compute distance, returning np.inf for any invalid/missing coordinates.
    This mirrors the robustness of get_foodbank_mask's internal distance handling.
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
    #except Exception:
    except (TypeError, ValueError, OverflowError):
        # If calculate_distance itself fails for any reason, treat distance as infinite
        return np.inf


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
        # Compute distance for all rows once, with robust handling of invalid coordinates.
        distances = foodbank_df.apply(
            lambda row: _safe_calculate_distance(
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
        return

    filter_widgets["results_div"].text = ""

    lat, lon = geocode_address(validated_address)
    if lat is None or lon is None:
        filter_widgets["results_div"].text = (
            "<p style='color:red'>Could not find this address. Please try again.</p>"
        )
        return

    user_location["lat"] = lat
    user_location["lon"] = lon
    update()

    filter_widgets["results_div"].text = (
        "<p style='color:green'>Address validated. Results updated.</p>"
    )


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
    update()

    # Clear results message
    filter_widgets["results_div"].text = ""


# 4. Wire up callbacks
resource_type_selector.on_change("active", lambda attr, old, new: update())
distance_slider.on_change("value", lambda attr, old, new: update())
open_only_toggle.on_change("active", lambda attr, old, new: update())
eligibility_group.on_change("active", lambda attr, old, new: update())
day_group.on_change("active", lambda attr, old, new: update())
address_input.on_change("value", on_address_change)
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)
update()

layout = create_layout(map_fig, filter_bar, nearby_panel)
curdoc().add_root(layout)
curdoc().title = "PantryMap"
