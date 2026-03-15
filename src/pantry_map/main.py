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
from bokeh.models import Div
from pantry_map.data.loader import get_foodbank_df
from pantry_map.components.layout import create_sidebar, create_layout, format_foodbank_list
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.utilities.utility import (
    validate_address,
    geocode_address,
)

# 1. Load Data
foodbank_df = get_foodbank_df()

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

# Placeholder for the Map (being worked on by teammate)
map_placeholder = Div(
    text="""
    <div style='display: flex; align-items: center; justify-content: center; height: 100%;
    background: #f0f2f5; border: 2px dashed #ccc; border-radius: 8px; color: #666;'>
        <h2>Map Component Placeholder</h2>
        <p style='margin-left: 20px;'>Map features are currently being developed by another teammate.</p>
    </div>""",
    sizing_mode="stretch_both"
)

user_location = {"lat": None, "lon": None}


def _selected_labels(checkbox_group):
    return [checkbox_group.labels[idx] for idx in checkbox_group.active]


# 3. Callbacks
def update():
    """Update the side panel listing based on filters."""
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
    filtered_df = foodbank_df[foodbank_mask]
    location_list.text = format_foodbank_list(filtered_df.head(20))


def on_search_click():
    """Handle address search for side panel listing."""
    address = address_input.value
    is_valid, msg, cleaned_address = validate_address(address)

    if not is_valid:
        results_div.text = f"<p style='color:red'>{msg}</p>"
        return

    sidebar_widgets["results_div"].text = ""

    # get lat and lon
    lat, lon = geocode_address(cleaned_address)
    if lat is None or lon is None:
        results_div.text = "<p style='color:red'>Could not find address.</p>"
        return

    user_location["lat"] = lat
    user_location["lon"] = lon

    update()
    sidebar_widgets["results_div"].text = (
        "<p style='color:green'>Address validated. Results updated.</p>"
    )


def on_address_change(attr, old, new):
    """Clear stored user location when the address text changes."""
    del attr, old, new
    # Clear stored user location when the address text changes so that
    # subsequent filter updates do not use a stale location.
    user_location["lat"] = None
    user_location["lon"] = None
    sidebar_widgets["results_div"].text = ""


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


# 4. Wire up callbacks
resource_type_selector.on_change("active", lambda attr, old, new: update())
distance_slider.on_change("value", lambda attr, old, new: update())
open_only_toggle.on_change("active", lambda attr, old, new: update())
eligibility_group.on_change("active", lambda attr, old, new: update())
day_group.on_change("active", lambda attr, old, new: update())
address_input.on_change("value", on_address_change)
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)

# Initial population
update()

# 5. Assemble Layout
layout = create_layout(map_placeholder, sidebar_layout)
curdoc().add_root(layout)
curdoc().title = "PantryMap - Side Panel"
