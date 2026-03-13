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
from pantry_map.utilities.utility import validate_address, geocode_address, find_nearest_foodbanks

# 1. Load Data
foodbank_df = get_foodbank_df()

# 2. Setup Side Panel
sidebar_layout, sidebar_widgets = create_sidebar(foodbank_df)
resource_types = sidebar_widgets['resource_type_dropdown']
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

# 3. Callbacks
def update():
    """Update the side panel listing based on filters."""
    mask = get_foodbank_mask(foodbank_df, resource_types)
    filtered_df = foodbank_df[mask]
    location_list.text = format_foodbank_list(filtered_df.head(20))

def on_search_click():
    """Handle address search for side panel listing."""
    address = address_input.value
    is_valid, msg, cleaned_address = validate_address(address)

    if not is_valid:
        results_div.text = f"<p style='color:red'>{msg}</p>"
        return

    lat, lon = geocode_address(cleaned_address or address)
    if lat is None or lon is None:
        results_div.text = "<p style='color:red'>Could not find address.</p>"
        return

    # Show top 5 nearest in side panel
    nearest_df = find_nearest_foodbanks(foodbank_df, lat, lon, k=5)
    location_list.text = format_foodbank_list(nearest_df)
    results_div.text = (
        "<p style='color: #57606a; font-weight:600;'>Showing top 5 nearest food banks</p>"
    )

def on_clear_click():
    """Reset side panel filters."""
    address_input.value = ""
    results_div.text = ""
    update()

# 4. Initialization
resource_types.on_change("value", lambda attr, old, new: update())
search_button.on_click(on_search_click)
clear_button.on_click(on_clear_click)

# Initial population
update()

# 5. Assemble Layout
layout = create_layout(map_placeholder, sidebar_layout)
curdoc().add_root(layout)
curdoc().title = "PantryMap - Side Panel"
