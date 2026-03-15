"""
Layout components for the PantryMap Bokeh application.

This module provides functions to create the sidebar, header, analytics panel,
and the main layout of the application. It also includes helper functions
for formatting food bank information in HTML.
"""

import html
from datetime import datetime
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import Div, TextInput, Button, Slider, CheckboxGroup, RadioButtonGroup, LayoutDOM
from pantry_map.utilities.constants import COLORS

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

def format_foodbank_list(foodbank_data):
    """
    Generate HTML for the list of food banks.

    Args:
        foodbank_data (pd.DataFrame): Dataframe containing food bank information.

    Returns:
        str: HTML string representing the list of food banks.
    """
    if foodbank_data is None or foodbank_data.empty:
        return ("<div style='padding: 20px; text-align: center; color: #666;'>"
                "No food banks found.</div>")

    cards = []
    show_distance = 'distance' in foodbank_data.columns

    for _, row_data in foodbank_data.iterrows():
        phone = row_data['Phone Number'] if pd.notna(row_data['Phone Number']) else "Not available"
        dist_html = (
            f"<div style='margin-top: 8px; font-size: 13px; font-weight: 600; color: #6a737d;'>"
            f"● {row_data['distance']} miles away</div>"
            if show_distance else ""
        )

        # Escape dataset-derived text fields before inserting into HTML
        agency = html.escape(str(row_data['Agency']), quote=True)
        location = html.escape(str(row_data['Location']), quote=True)
        address = html.escape(str(row_data['Address']), quote=True)
        phone_display = html.escape(str(phone), quote=True)
        resource_type = html.escape(str(row_data['Food Resource Type']), quote=True)

        # Detection
        is_open = is_open_today(row_data.get('Days/Hours', ''))
        if is_open is True:
            status_badge = ("<span style='background: #dafbe1; color: #1a7f37; padding: 2px 6px; "
                            "border-radius: 4px; font-size: 10px; font-weight: 700; "
                            "margin-left: 10px;'>OPEN TODAY</span>")
        elif is_open is False:
            status_badge = ("<span style='background: #ffebe9; color: #cf222e; padding: 2px 6px; "
                            "border-radius: 4px; font-size: 10px; font-weight: 700; "
                            "margin-left: 10px;'>CLOSED TODAY</span>")
        else:
            status_badge = ""

        card = f"""
        <div style='padding: 16px; border: 1px solid #e1e4e8; border-radius: 8px;
        margin-bottom: 15px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
            <div style='display: flex; justify-content: space-between; align-items: start;
            margin-bottom: 8px;'>
                <h3 style='margin: 0; font-size: 16px; color: #24292e; line-height: 1.3;'>
                    {agency}
                </h3>
                {status_badge}
            </div>
            <div style='font-size: 13px; color: #586069;'>
                <p style='margin: 4px 0;'>{location}</p>
                <p style='margin: 2px 0;'>{address}</p>
                <p style='margin: 2px 0;'>{phone_display}</p>
            </div>
            {dist_html}
            <div style='margin-top: 12px; padding-top: 10px; border-top: 1px solid #f6f8fa;'>
                <span style='background: #f1f8ff; color: #0366d6; padding: 3px 8px;
                border-radius: 12px; font-size: 10px; font-weight: 600;'>
                    {resource_type}
                </span>
            </div>
        </div>
        """
        cards.append(card)

    cards_joined = "".join(cards)
    return (f"<div style='max-height: 520px; overflow-y: auto; padding: 10px; "
            f"background: #fafbfc;'>{cards_joined}</div>")

def create_sidebar():
    """
    Create the sidebar layout and widgets.

    Returns:
        tuple: (sidebar_layout, dict_of_widgets)
    """
    resource_type_selector = RadioButtonGroup(
        labels=["Both", "Food Bank", "Meal"],
        active=0,
        width=360,
    )

    distance_slider = Slider(title="Distance (miles)", start=1, end=25, value=10, step=1, width=360)
    open_only_toggle = CheckboxGroup(labels=["Open locations only"], active=[])
    eligibility_group = CheckboxGroup(
        labels=["General Public", "Seniors", "Youth"],
        active=[],
    )
    day_group = CheckboxGroup(
        labels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        active=[],
    )

    # Text input and search button for address input
    address_input = TextInput(value="", title="Enter your address:")
    search_button = Button(label="Search", button_type="primary")
    clear_button = Button(label="Clear", button_type="default")

    # Placeholder for results / location list
    results_div = Div(text="", width=360)
    location_list = Div(
        text="<p style='color: #666;'>Loading list...</p>", sizing_mode="stretch_width")

    sidebar_layout = column(
        Div(
            text="""
            <div style='padding: 5px 0; font-size: 12px; font-weight: 700; text-transform: uppercase;
            color: #57606a; letter-spacing: 0.5px;'>
                Search & Filters
            </div>""",
            sizing_mode="stretch_width"
        ),
        Div(text="<div style='font-size:12px; font-weight:600; margin: 4px 0;'>"
            "Food resource type</div>"),
        resource_type_selector,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>"
            "Distance from address</div>"),
        distance_slider,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>"
            "Operational status</div>"),
        open_only_toggle,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>"
            "Eligibility</div>"),
        eligibility_group,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>"
            "Available days</div>"),
        day_group,
        address_input,
        row(search_button, clear_button, width=360),
        results_div,
        Div(
            text="""
            <hr style='border: 0; border-top: 1px solid #e1e4e8; margin: 15px 0;'>
            <div style='font-size: 12px; font-weight: 700; text-transform: uppercase;
            color: #57606a; letter-spacing: 0.5px; margin-bottom: 10px;'>
                Nearby Food Banks
            </div>""",
            sizing_mode="stretch_width"
        ),
        location_list,
        width=380,
        sizing_mode="fixed"
    )

    return sidebar_layout, {
        "resource_type_selector": resource_type_selector,
        "distance_slider": distance_slider,
        "open_only_toggle": open_only_toggle,
        "eligibility_group": eligibility_group,
        "day_group": day_group,
        "address_input": address_input,
        "search_button": search_button,
        "clear_button": clear_button,
        "results_div": results_div,
        "location_list": location_list,
    }

def create_analytics_panel():
    """
    Create the HTML for the analytics panel.

    Returns:
        str: HTML string for the analytics dashboard widgets.
    """
    return f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']};
        border-radius: 6px; border-left: 3px solid {COLORS['accent_blue']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px;
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Locations</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']};
            margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">across Seattle</div>
        </div>

        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']};
        border-radius: 6px; border-left: 3px solid {COLORS['accent_green']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px;
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Transit Accessible</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']};
            margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">100% coverage</div>
        </div>

        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']};
        border-radius: 6px; border-left: 3px solid {COLORS['accent_orange']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px;
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Avg Accessibility</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']};
            margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">out of 100</div>
        </div>

        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']};
        border-radius: 6px; border-left: 3px solid {COLORS['accent_green']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px;
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Weekly Reach</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']};
            margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">unique visitors</div>
        </div>
    </div>
    """

def create_header():
    """
    Create the header component with a Div.

    Returns:
        Div: Bokeh Div component containing the header HTML.
    """
    header_div = Div(text=f"""
        <div style="background: {COLORS['bg']}; border-bottom: 1px solid {COLORS['border']}; padding: 28px 40px;">
            <div style="max-width: 1600px; margin: 0 auto;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 style="margin: 0 0 8px 0; font-size: 32px; font-weight: 600; color: {COLORS['text_primary']}; letter-spacing: -0.5px;">
                            PantryMap
                        </h1>
                        <p style="margin: 0; font-size: 14px; color: {COLORS['text_secondary']}; font-weight: 400;">
                            Food bank accessibility and public transit network
                        </p>
                    </div>
                    <div style="text-align: right; font-size: 12px;">
                        <div style="color: {COLORS['text_secondary']}; margin-bottom: 2px;">
                            <span style="color: {COLORS['accent_green']}; font-weight: 600;">●</span> System Active
                        </div>
                        <div style="color: {COLORS['text_tertiary']};">Updated today at 18:30 UTC</div>
                    </div>
                </div>
            </div>
        </div>
        """, sizing_mode="stretch_width")
    return header_div

def create_layout(fig: LayoutDOM, sidebar: LayoutDOM) -> LayoutDOM:
    """
    Assemble the final application layout.

    Args:
        fig (LayoutDOM): The main content component (e.g., map figure or placeholder Div).
        sidebar (LayoutDOM): The sidebar layout component.

    Returns:
        LayoutDOM: The final assembled column layout.
    """
    analytics_div = Div(text=create_analytics_panel(), sizing_mode="stretch_width")
    header_div = create_header()

    # Use stretch_width and a fixed min_height to ensure it displays correctly
    main_row = row(
        sidebar,
        fig,
        sizing_mode="stretch_width",
        min_height=600
    )

    final_layout = column(
        header_div,
        analytics_div,
        main_row,
        sizing_mode="stretch_width"
    )
    return final_layout
