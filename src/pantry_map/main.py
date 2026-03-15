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
from pantry_map.filters.mask import get_foodbank_mask
from pantry_map.utilities.utility import (
    calculate_distance,
    validate_address,
    geocode_address,
)

transit_df = get_transit_df()
transit_source = ColumnDataSource(transit_df)

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


def update():
    labels = resource_type_selector.labels
    active = resource_type_selector.active
    if active is None:
        # Treat None as "Both" if available, otherwise fall back to the first label
        if "Both" in labels:
            resource_type = "Both"
        elif labels:
            resource_type = labels[0]
        else:
            resource_type = None
    else:
        resource_type = labels[active]
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

    filtered_df = foodbank_df[foodbank_mask].copy()

    if user_location["lat"] is not None and user_location["lon"] is not None and not filtered_df.empty:
        filtered_df["distance"] = filtered_df.apply(
            lambda row: calculate_distance(
                user_location["lat"],
                user_location["lon"],
                row["Latitude"],
                row["Longitude"],
            ),
            axis=1,
        )
        filtered_df = filtered_df.sort_values("distance")
    else:
        filtered_df = filtered_df.sort_values("Agency")

    nearby_widgets["location_list"].text = format_nearby_foodbanks(filtered_df)

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
        filter_widgets["results_div"].text = f"<p style='color:red'>{msg}</p>"
        return

    filter_widgets["results_div"].text = ""

    # get lat and lon
    lat, lon = geocode_address(normalized_address)
    if lat is None or lon is None:
        filter_widgets["results_div"].text = "<p style='color:red'>Could not find this address. Please try again.</p>"
        return

    user_location["lat"] = lat
    user_location["lon"] = lon

    update()
    filter_widgets["results_div"].text = "<p style='color:green'>Address validated. Results updated.</p>"


def on_address_change(attr, old, new):
    del attr, old, new
    # Clear stored user location when the address text changes so that
    # subsequent filter updates do not use a stale location.
    user_location["lat"] = None
    user_location["lon"] = None
    filter_widgets["results_div"].text = ""
    update()

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
    filter_widgets["results_div"].text = ""

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
