"""
Layout components for the PantryMap Bokeh application.

This module provides functions to create the filter bar, search bar, nearby panel,
header, and the main layout of the application. It also includes helper functions
for formatting food bank and route information in HTML.
"""

import html
from datetime import datetime

import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import (
    Div, TextInput, Button, Slider, RadioButtonGroup, MultiChoice
)
import re

def is_open_today(hours_str):
    """
    Check if today's day is mentioned in the hours string.

    Args:
        hours_str (str): The opening hours string from the dataset.

    Returns:
        bool or None: True if open today, False if closed, None if data is missing.
    """
    if pd.isna(hours_str) or not hours_str:
        return None

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    short_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    today_idx = datetime.now().weekday()
    today_full = days[today_idx]
    today_short = short_days[today_idx]

    hours_lower = str(hours_str).lower()

    # Check for ranges like "Monday-Friday"
    if any(range_str in hours_lower for range_str in ["monday-friday", "mon-fri", "mon - fri"]):
        if today_idx <= 4:
            return True

    # Check for specific day mentions or "Daily"
    if today_full in hours_lower or today_short in hours_lower or "daily" in hours_lower:
        return True

    return False


def _label(text):
    return Div(
        text=(
            "<div style='font-size:11px; font-weight:700; margin:0 0 6px; "
            "color:#6b7280; text-transform:uppercase; letter-spacing:0.4px;'>"
            f"{text}</div>"
        )
    )


def _divider():
    return Div(
        text="",
        width=2,
        styles={"border-left": "1px solid #e5e7eb", "align-self": "stretch",
                "margin": "0 20px"},
    )


def create_filter_bar():
    """Create the compact top filter strip and return widgets for callbacks."""
    resource_type_selector = RadioButtonGroup(
        labels=["Both", "Food Bank", "Meal"],
        active=0,
        width=230,
    )
    eligibility_group = MultiChoice(
        options=["General Public", "Seniors", "Youth"],
        value=[],
        width=280,
    )
    day_group = MultiChoice(
        options=["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"],
        value=[],
        width=480,

    )

    filter_row = row(
        column(_label("Resource type"), resource_type_selector),
        _divider(),
        column(_label("Eligibility"), eligibility_group),
        _divider(),
        column(_label("Available days"), day_group),
        align="start",
        styles={
            "background": "#ffffff",
            "border-bottom": "1px solid #e5e7eb",
            "padding": "10px 20px",
        },
    )

    return filter_row, {
        "resource_type_selector": resource_type_selector,
        "eligibility_group": eligibility_group,
        "day_group": day_group,
    }


def create_search_bar():
    """Create the address search bar and results area above the map.

    Returns:
        tuple: (search_layout, search_widgets dict)
    """
    address_input = TextInput(
        value="", placeholder="Enter your address...", sizing_mode="stretch_width"
    )
    search_button = Button(label="Search", button_type="primary")
    clear_button = Button(label="Clear", button_type="default")
    distance_slider = Slider(
        title="Distance (miles)", start=1, end=25, value=10, step=1, width=200,
    )
    results_div = Div(text="", sizing_mode="stretch_width")

    search_layout = column(
        row(
            address_input,
            search_button,
            clear_button,
            _divider(),
            distance_slider,
            sizing_mode="stretch_width",
        ),
        results_div,
        sizing_mode="stretch_width",
        styles={"background": "#ffffff", "padding": "8px 12px"},
    )

    return search_layout, {
        "address_input": address_input,
        "search_button": search_button,
        "clear_button": clear_button,
        "distance_slider": distance_slider,
        "results_div": results_div,
    }


def create_nearby_panel():
    """Create the fixed-width left panel showing nearby food bank cards."""
    location_list = Div(
        text=(
            "<div style='padding:12px; color:#6a737d;'>"
            "Apply filters or search an address to view nearby food banks."
            "</div>"
        ),
        width=360,
        sizing_mode="stretch_height",
        styles={"overflow-y": "auto"},
    )

    panel = column(
        Div(
            text=(
                "<div style='font-size:12px; font-weight:700; letter-spacing:0.5px; "
                "color:#57606a; margin:4px 0 10px;'>NEARBY FOOD BANKS</div>"
            )
        ),
        location_list,
        width=380,
        sizing_mode="stretch_height",
        styles={"padding": "10px", "background": "#f8fafc",
                "border-right": "1px solid #e5e7eb"},
    )

    return panel, {"location_list": location_list}


def _website_html(row_data):
    website = row_data.get("Website")
    website_str = "" if website is None else str(website).strip()
    if not website_str or website_str.lower() in {"nan", "na", "n/a", "not available", ""}:
        return ""
    website_url = html.escape(website_str, quote=True)
    return (
        f"<div style='margin-top:2px;'>"
        f"<a href='{website_url}' target='_blank' "
        f"style='color:#0969da; font-size:13px;'>Visit website</a>"
        f"</div>"
    )


def _status_badge(row_data):
    open_today = is_open_today(row_data.get("Days/Hours"))
    if open_today is True:
        return (
            "<span style='background:#dafbe1; color:#1a7f37; padding:2px 7px; "
            "border-radius:4px; font-size:10px; font-weight:700;'>Open Today</span>"
        )
    if open_today is False:
        return (
            "<span style='background:#ffebe9; color:#cf222e; padding:2px 7px; "
            "border-radius:4px; font-size:10px; font-weight:700;'>Closed Today</span>"
        )
    return ""


def format_nearby_foodbanks(foodbank_data):
    """Format filtered food bank rows as HTML cards for the nearby panel."""
    if foodbank_data is None or foodbank_data.empty:
        return "<div style='padding:12px; color:#6a737d;'>No matching food banks found.</div>"

    cards = []
    show_distance = "distance" in foodbank_data.columns

    for _, row_data in foodbank_data.head(12).iterrows():
        agency = html.escape(str(row_data.get("Agency", "Unknown")), quote=True)
        location = html.escape(str(row_data.get("Location", "")), quote=True)
        address = html.escape(str(row_data.get("Address", "")), quote=True)
        phone = row_data.get("Phone Number")
        phone_str = "" if phone is None else str(phone).strip()
        if not phone_str or phone_str.lower() in {"nan", "na", "n/a"}:
            phone_display = "Not available"
        else:
            phone_display = html.escape(phone_str, quote=True)
        resource_type = html.escape(str(row_data.get("Food Resource Type", "")), quote=True)
        website_html = _website_html(row_data)
        status_badge = _status_badge(row_data)

        distance_html = ""
        if show_distance:
            distance_html = (
                f"<div style='margin-top:8px; font-size:12px; color:#6a737d; font-weight:600;'>"
                f"{row_data['distance']} miles away</div>"
            )

        cards.append(
            f"""
            <div style='padding:14px; border:1px solid #d8dee4; border-radius:10px;
            margin-bottom:10px; background:white; box-shadow:0 1px 2px rgba(0,0,0,0.04);'>
                <div style='display:flex; justify-content:space-between; gap:10px;
                margin-bottom:6px;'>
                    <div style='font-size:15px; font-weight:700; color:#24292f;
                    line-height:1.3;'>{agency}</div>
                    {status_badge}
                </div>
                <div style='font-size:13px; color:#57606a;'>
                    <div>{location}</div>
                    <div style='margin-top:2px;'>{address}</div>
                    <div style='margin-top:2px;'>{phone_display}</div>
                    {website_html}
                    {distance_html}
                </div>
                <div style='margin-top:10px; padding-top:8px; border-top:1px solid #f0f2f4;'>
                    <span style='background:#f1f8ff; color:#0969da; padding:3px 8px;
                    border-radius:12px; font-size:10px; font-weight:700;'>{resource_type}</span>
                </div>
            </div>
            """
        )

    return "<div style='padding-right:6px;'>" + "".join(cards) + "</div>"


def _chip(content, bg_color, text_color="#ffffff", extra_style=""):
    return (
        f"<span style='display:inline-flex; flex-direction:column; align-items:center; "
        f"padding:6px 12px; border-radius:20px; background:{bg_color}; color:{text_color}; "
        f"font-size:12px; font-weight:600; white-space:nowrap; {extra_style}'>"
        f"{content}</span>"
    )


_ARROW = "<span style='color:#6a737d; font-size:12px; padding:0 4px;'>&#x2192;</span>"


_HEX_COLOR_RE = re.compile(r"^#([0-9a-f]{3}|[0-9a-f]{6})$", re.IGNORECASE)


def _normalize_hex_color(value, default="#374151"):
    """
    Normalize a CSS hex color value.

    Accepts #RGB or #RRGGBB; returns `default` if the value is missing or invalid.
    """
    if not isinstance(value, str):
        return default
    value = value.strip()
    if not value:
        return default
    if not _HEX_COLOR_RE.match(value):
        return default
    # Normalize to lowercase for consistency
    return value.lower()


def format_route_display(legs, total_minutes, destination_name):
    """Format a route leg list as an HTML horizontal chip timeline for results_div.

    Args:
        legs (list[dict]): Leg dicts from get_route_to_destination().
        total_minutes (int): Total estimated travel time in minutes (integer).
                             This function handles hr/min formatting internally.
        destination_name (str): Name of the destination food bank.

    Returns:
        str: HTML string for results_div.
    """
    if not legs:
        return ""

    if total_minutes >= 60:
        hours = total_minutes // 60
        mins = total_minutes % 60
        time_str = f"{hours} hr {mins} min" if mins else f"{hours} hr"
    else:
        time_str = f"{total_minutes} min"

    dest = html.escape(str(destination_name), quote=True)
    header = (
        f"<div style='font-size:13px; font-weight:700; color:#24292f; margin-bottom:8px;'>"
        f"To {dest} &mdash; Estimated time: {time_str}</div>"
    )

    chips = []
    for leg in legs:
        leg_type = leg["type"]
        if chips:
            chips.append(_ARROW)
        if leg_type == "walk":
            chips.append(_chip("Walk", "#f0f0f0", text_color="#24292f"))
        elif leg_type == "bus":
            raw_color = leg.get("color")
            color = _normalize_hex_color(raw_color, default="#374151")
            short = html.escape(str(leg["short_name"]), quote=True)
            chips.append(_chip(short, color))

    chips.append(_ARROW)
    chips.append(_chip("Arrive", "#f0f0f0", text_color="#24292f"))

    timeline = (
        "<div style='display:flex; align-items:center; flex-wrap:wrap; gap:2px; "
        "padding:4px 0;'>" + "".join(chips) + "</div>"
    )
    return "<div style='padding:6px 0;'>" + header + timeline + "</div>"


def create_header():
    """Create page header."""
    header_content = Div(
        text=(
            "<div style='padding:8px 24px;display:flex;align-items:baseline;gap:10px;'>"
            "<span style='font-size:20px;font-weight:700;color:#ffffff;"
            "letter-spacing:-0.3px;'>PantryMap</span>"
            "<span style='font-size:12px;color:#bfdbfe;font-weight:400;'>"
            "Food bank accessibility and public transit network</span>"
            "</div>"
        ),
        sizing_mode="stretch_width",
        styles={"display": "block"},
    )

    return column(
        header_content,
        sizing_mode="stretch_width",
        styles={
            "background": "#0e4c92",
            "border-bottom": "1px solid #1d4ed8",
        },
    )


def create_layout(fig, filter_bar, search_bar, nearby_panel):
    """Assemble the full application layout.

    Args:
        fig: The Bokeh map figure.
        filter_bar: Layout from create_filter_bar().
        search_bar: Layout from create_search_bar().
        nearby_panel: Layout from create_nearby_panel().

    Returns:
        LayoutDOM: The assembled page layout.
    """
    fig.styles = {"border-left": "1px solid #e5e7eb", "background": "#ffffff"}
    map_column = column(search_bar, fig, sizing_mode="stretch_both")
    main_row = row(
        nearby_panel,
        map_column,
        sizing_mode="stretch_both",
        min_height=600,
    )
    return column(
        create_header(),
        filter_bar,
        main_row,
        sizing_mode="stretch_both",
        styles={"background": "#ffffff"},
    )


def create_sidebar(foodbank_df=None):
    """Deprecated. Use create_filter_bar() directly."""
    del foodbank_df
    return column(), {}


def format_foodbank_list(foodbank_data):
    """Backward-compatible alias for existing call sites."""
    return format_nearby_foodbanks(foodbank_data)
