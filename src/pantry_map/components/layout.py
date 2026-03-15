import html

from bokeh.layouts import column, row
from bokeh.models import Div, TextInput, Button, Slider, CheckboxGroup, RadioButtonGroup
from pantry_map.utilities.constants import COLORS


def _label(text):
    return Div(text=f"<div style='font-size:12px; font-weight:600; margin: 0 0 6px;'>{text}</div>")


def create_filter_bar():
    resource_type_selector = RadioButtonGroup(
        labels=["Both", "Food Bank", "Meal"],
        active=0,
        width=260,
    )

    distance_slider = Slider(title="Distance (miles)", start=1, end=25, value=10, step=1, width=260)
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
    address_input = TextInput(value="", title="Address", width=350)
    search_button = Button(label="Search", button_type="primary")
    clear_button = Button(label="Clear", button_type="default")

    results_div = Div(text="", width=380)

    toolbar = column(
        Div(
            text="""
            <div style=
                'padding: 8px 0 10px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                color: #57606a;
                letter-spacing: 0.5px;
            '>
                Search & Filters
            </div>"""
        ),
        row(
            column(_label("Resource type"), resource_type_selector, width=280),
            column(_label("Operational status"), open_only_toggle, width=190),
            column(distance_slider, width=280),
            column(address_input, row(search_button, clear_button), width=390),
            sizing_mode="stretch_width",
        ),
        row(
            column(_label("Eligibility"), eligibility_group, width=380),
            column(_label("Available days"), day_group, width=600),
            results_div,
            sizing_mode="stretch_width",
        ),
        width=1400,
        sizing_mode="stretch_width",
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
    location_list = Div(
        text="<div style='padding:12px; color:#6a737d;'>Apply filters or search an address to view nearby food banks.</div>",
        width=360,
    )

    panel = column(
        Div(text="<div style='font-size:12px; font-weight:700; letter-spacing:0.5px; color:#57606a; margin:8px 0 10px;'>NEARBY FOOD BANKS</div>"),
        location_list,
        results_div,
        sizing_mode="fixed",
    )

    return panel, {"location_list": location_list}


def format_nearby_foodbanks(foodbank_data):
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
            status_badge = "<span style='background:#dafbe1; color:#1a7f37; padding:2px 7px; border-radius:4px; font-size:10px; font-weight:700;'>OPEN</span>"
        else:
            status_badge = "<span style='background:#ffebe9; color:#cf222e; padding:2px 7px; border-radius:4px; font-size:10px; font-weight:700;'>CLOSED</span>"

        distance_html = ""
        if show_distance:
            distance_html = (
                f"<div style='margin-top:8px; font-size:12px; color:#6a737d; font-weight:600;'>"
                f"{row_data['distance']} miles away</div>"
            )

        cards.append(
            f"""
            <div style='padding:14px; border:1px solid #e1e4e8; border-radius:8px; margin-bottom:10px; background:white;'>
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
    """

def create_header():
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


def create_layout(fig, filter_bar, nearby_panel):
    header_div = create_header()
    main_content = row(
        nearby_panel,
        fig,
        sizing_mode="stretch_both"
    )

    centered_layout = column(
        header_div,
        filter_bar,
        main_content,
        sizing_mode="stretch_both"
    )
    return centered_layout


def create_sidebar(foodbank_df=None):
    del foodbank_df
    return create_filter_bar()
