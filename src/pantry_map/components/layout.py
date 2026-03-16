"""Layout components for the PantryMap Bokeh application."""

import html
from bokeh.layouts import column, row, Spacer
from bokeh.models import Div, TextInput, Button, Slider, CheckboxGroup, RadioButtonGroup
from pantry_map.utilities.constants import COLORS


def _label(text):
    return Div(
        text=(
            "<div style='font-size:12px; font-weight:700; margin:0 0 8px; "
            "color:#4b5563; letter-spacing:0.2px;'>"
            f"{text}</div>"
        )
    )


def create_filter_bar():
    """Create top filter toolbar and return widgets for callbacks."""
    resource_type_selector = RadioButtonGroup(
        labels=["Both", "Food Bank", "Meal"],
        active=0,
        width=260,
    )

    distance_slider = Slider(title="Distance (miles)", start=1, end=25, value=10, step=1, width=260)
    open_only_toggle = CheckboxGroup(labels=["Open locations only"], active=[])
    eligibility_group = CheckboxGroup(labels=["General Public", "Seniors", "Youth"], active=[])
    day_group = CheckboxGroup(
        labels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        active=[],
    )

    address_input = TextInput(value="", title="Address", width=350)
    search_button = Button(label="Search", button_type="primary")
    clear_button = Button(label="Clear", button_type="default")
    results_div = Div(text="", width=520)

    toolbar = column(
        Div(
            text="""
            <div style='padding:6px 0 12px; font-size:11px; font-weight:700; text-transform:uppercase;
            color:#6b7280; letter-spacing:0.6px;'>Search & Filters</div>
            """
        ),
        row(
            column(
                _label("Resource type"),
                resource_type_selector,
                width=270,
                styles={"padding": "12px", "border": "1px solid #dbe2ea", "border-radius": "10px", "background": "#ffffff", "box-shadow": "0 1px 2px rgba(16,24,40,0.04)"},
            ),
            column(
                _label("Operational status"),
                open_only_toggle,
                width=190,
                styles={"padding": "12px", "border": "1px solid #dbe2ea", "border-radius": "10px", "background": "#ffffff", "box-shadow": "0 1px 2px rgba(16,24,40,0.04)"},
            ),
            column(
                _label("Distance"),
                distance_slider,
                width=270,
                styles={"padding": "12px", "border": "1px solid #dbe2ea", "border-radius": "10px", "background": "#ffffff", "box-shadow": "0 1px 2px rgba(16,24,40,0.04)"},
            ),
            column(
                _label("Eligibility"),
                eligibility_group,
                width=210,
                styles={"padding": "12px", "border": "1px solid #dbe2ea", "border-radius": "10px", "background": "#ffffff", "box-shadow": "0 1px 2px rgba(16,24,40,0.04)"},
            ),
            column(
                _label("Available days"),
                day_group,
                width=220,
                styles={"padding": "12px", "border": "1px solid #dbe2ea", "border-radius": "10px", "background": "#ffffff", "box-shadow": "0 1px 2px rgba(16,24,40,0.04)"},
            ),
            column(
                _label("Address"),
                address_input,
                row(search_button, clear_button),
                width=350,
                styles={"padding": "12px", "border": "1px solid #dbe2ea", "border-radius": "10px", "background": "#ffffff", "box-shadow": "0 1px 2px rgba(16,24,40,0.04)"},
            ),
            sizing_mode="scale_width",
        ),
        results_div,
        width=1500,
        sizing_mode="stretch_width",
        styles={"padding": "8px 18px 14px", "background": "#f8fafc", "border-bottom": "1px solid #e5e7eb"},
    )

    return toolbar, {
        "resource_type_selector": resource_type_selector,
        "distance_slider": distance_slider,
        "open_only_toggle": open_only_toggle,
        "eligibility_group": eligibility_group,
        "day_group": day_group,
        "address_input": address_input,
        "search_button": search_button,
        "clear_button": clear_button,
        "results_div": results_div,
    }


def create_nearby_panel():
    """Create left nearby results panel."""
    location_list = Div(
        text=(
            "<div style='padding:12px; color:#6a737d;'>"
            "Apply filters or search an address to view nearby food banks."
            "</div>"
        ),
        width=360,
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
        styles={"padding": "10px", "background": "#f8fafc", "border-right": "1px solid #e5e7eb"},
    )

    return panel, {"location_list": location_list}


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
        phone_display = html.escape(str(phone), quote=True) if phone else "Not available"
        resource_type = html.escape(str(row_data.get("Food Resource Type", "")), quote=True)

        status = str(row_data.get("Operational Status", "")).strip().lower()
        if status == "open":
            status_badge = (
                "<span style='background:#dafbe1; color:#1a7f37; padding:2px 7px; border-radius:4px; "
                "font-size:10px; font-weight:700;'>OPEN</span>"
            )
        else:
            status_badge = (
                "<span style='background:#ffebe9; color:#cf222e; padding:2px 7px; border-radius:4px; "
                "font-size:10px; font-weight:700;'>CLOSED</span>"
            )

        distance_html = ""
        if show_distance:
            distance_html = (
                f"<div style='margin-top:8px; font-size:12px; color:#6a737d; font-weight:600;'>"
                f"{row_data['distance']} miles away</div>"
            )

        cards.append(
            f"""
            <div style='padding:14px; border:1px solid #d8dee4; border-radius:10px; margin-bottom:10px; background:white; box-shadow:0 1px 2px rgba(0,0,0,0.04);'>
                <div style='display:flex; justify-content:space-between; gap:10px; margin-bottom:6px;'>
                    <div style='font-size:16px; font-weight:700; color:#24292f; line-height:1.3;'>{agency}</div>
                    {status_badge}
                </div>
                <div style='font-size:13px; color:#57606a;'>
                    <div>{location}</div>
                    <div style='margin-top:2px;'>{address}</div>
                    <div style='margin-top:2px;'>{phone_display}</div>
                    {distance_html}
                </div>
                <div style='margin-top:10px; padding-top:8px; border-top:1px solid #f0f2f4;'>
                    <span style='background:#f1f8ff; color:#0969da; padding:3px 8px; border-radius:12px; font-size:10px; font-weight:700;'>{resource_type}</span>
                </div>
            </div>
            """
        )

    return "<div style='max-height:640px; overflow-y:auto; padding-right:6px;'>" + "".join(cards) + "</div>"


def create_header():
    """Create page header."""
    header_content = Div(
        text=f"""
        <div style="padding: 26px 0 20px; text-align:center;">
            <h1 style="margin: 0 0 8px 0; font-size: 32px; font-weight: 600; color: {COLORS['text_primary']}; letter-spacing: -0.5px; text-align:center;">
                PantryMap
            </h1>
            <p style="margin: 0; font-size: 14px; color: {COLORS['text_secondary']}; font-weight: 400; text-align:center;">
                Food bank accessibility and public transit network
            </p>
            <p style="margin:6px 0 0; font-size:12px; color: {COLORS['text_tertiary']}; text-align:center;">Updated today</p>
        </div>
        """,
        width=620,
        sizing_mode="stretch_width",
        styles={"display": "block", "text-align": "center"},
    )

    return column(
        row(
            Spacer(sizing_mode="stretch_width"),
            header_content,
            Spacer(sizing_mode="stretch_width"),
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
        styles={
            "background": COLORS["bg"],
            "border-bottom": f"1px solid {COLORS['border']}",
        },
    )


def create_layout(fig, filter_bar, nearby_panel):
    """Create overall page layout."""
    fig.styles = {"border-left": "1px solid #e5e7eb", "background": "#ffffff"}
    main_content = row(nearby_panel, fig, sizing_mode="stretch_both")
    return column(create_header(), filter_bar, main_content, sizing_mode="stretch_both", styles={"background": "#ffffff"})


def create_sidebar(foodbank_df=None):
    """Backward-compatible alias used by older callers."""
    del foodbank_df
    return create_filter_bar()


def format_foodbank_list(foodbank_data):
    """Backward-compatible alias for existing call sites."""
    return format_nearby_foodbanks(foodbank_data)

