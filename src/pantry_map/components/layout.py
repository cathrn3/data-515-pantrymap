from bokeh.layouts import column, row
from bokeh.models import MultiSelect, Div, TextInput, Button
from pantry_map.utilities.constants import COLORS
import math





# ── Helper: badge colour by type ────────────────────────────────────────────
def _badge_style(resource_type):
    t = resource_type.lower()
    if "food bank" in t and "meal" in t:
        return "background:#fef3c7;color:#92400e;border:1px solid #fde68a;", "Food Bank + Meal"
    elif "food bank" in t:
        return "background:#dbeafe;color:#1e40af;border:1px solid #bfdbfe;", "Food Bank"
    else:
        return "background:#dcfce7;color:#166534;border:1px solid #bbf7d0;", "Meal Program"


# ── Public helper: build HTML cards for a list of food bank rows ─────────────
def render_foodbank_cards(df, title=None):
    """
    Given a DataFrame of food banks (optionally with a 'distance' column),
    return an HTML string of styled cards suitable for a Bokeh Div.

    Parameters
    ----------
    df : pd.DataFrame
        Rows from the food bank dataset.  Must contain at minimum:
        Location, Food Resource Type, Phone Number, Days/Hours, Address.
        If a 'distance' column is present, it is shown on the card.
    title : str, optional
        Section heading rendered above the cards.
    """
    if df is None or len(df) == 0:
        return """
            <div style='padding:24px 0; text-align:center; color:#57606a;'>
                <div style='font-size:32px; margin-bottom:8px;'>&#128269;</div>
                <div style='font-weight:600; margin-bottom:4px;'>No food banks found</div>
                <div style='font-size:13px;'>Try a different address.</div>
            </div>"""

    has_distance = "distance" in df.columns

    # Section heading
    heading = ""
    if title:
        heading = f"""
        <div style='
            padding: 10px 0 6px 0;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #57606a;
            letter-spacing: 0.5px;
            border-top: 1px solid {COLORS['border']};
            margin-top: 8px;
        '>{title}</div>"""

    cards_html = ""
    for _, row_data in df.iterrows():
        name    = row_data.get("Location") or row_data.get("Agency", "Unknown")
        rtype   = str(row_data.get("Food Resource Type", ""))
        phone   = str(row_data.get("Phone Number", "")).strip()
        hours   = str(row_data.get("Days/Hours", "")).strip()
        address = str(row_data.get("Address", "")).strip()
        status  = str(row_data.get("Operational Status", "open")).lower()



        badge_style, badge_label = _badge_style(rtype)


        # Distance chip
        dist_html = ""
        if has_distance and not math.isnan(float(row_data["distance"])):
            dist_html = f"""
            <span style='
                display:inline-block;
                background:#e0f2fe;
                color:#075985;
                border:1px solid #bae6fd;
                border-radius:20px;
                font-size:11px;
                font-weight:600;
                padding:2px 8px;
                margin-left:6px;
            '>&#128205; {float(row_data['distance']):.1f} mi</span>"""

        # Status dot
        dot_color = "#22c55e" if status == "open" else "#ef4444"
        status_label = status.capitalize()

        # Phone row
        phone_html = ""
        if phone and phone != "nan":
            phone_html = f"""
            <div style='display:flex;align-items:center;gap:6px;margin-top:5px;font-size:12px;color:#57606a;'>
                <span>&#128222;</span><span>{phone}</span>
            </div>"""

        # Hours row
        hours_html = ""
        if hours and hours != "nan":
            hours_html = f"""
            <div style='display:flex;align-items:flex-start;gap:6px;margin-top:5px;font-size:12px;color:#57606a;'>
                <span>&#128336;</span><span>{hours}</span>
            </div>"""

        # Address row
        address_html = ""
        if address and address != "nan":
            address_html = f"""
            <div style='display:flex;align-items:flex-start;gap:6px;margin-top:5px;font-size:12px;color:#57606a;'>
                <span>&#128205;</span><span>{address}</span>
            </div>"""

        cards_html += f"""
        <div style='
            background: white;
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            border-left: 3px solid {COLORS['accent_blue']};
        '>
            <!-- Name + badge -->
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px;'>
                <div style='font-size:13px;font-weight:600;color:{COLORS["text_primary"]};line-height:1.35;'>{name}</div>
                <span style='
                    flex-shrink:0;
                    font-size:10px;
                    font-weight:600;
                    padding:2px 7px;
                    border-radius:20px;
                    {badge_style}
                '>{badge_label}</span>
            </div>
            <!-- Rating + distance + status -->
            <div style='display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-bottom:2px;'>

                {dist_html}
                <span style='margin-left:auto;font-size:11px;font-weight:500;display:flex;align-items:center;gap:4px;'>
                    <span style='width:7px;height:7px;border-radius:50%;background:{dot_color};display:inline-block;'></span>
                    <span style='color:{dot_color};'>{status_label}</span>
                </span>
            </div>
            {phone_html}
            {hours_html}
            {address_html}
        </div>"""

    return heading + cards_html


# ── create_sidebar ───────────────────────────────────────────────────────────
def create_sidebar(foodbank_df):
    # Dropdown filter
    options = list(foodbank_df["Food Resource Type"].unique())
    resource_type_dropdown = MultiSelect(
        value=options,
        options=options
    )

    # Text input and search button for address input
    address_input = TextInput(value="", title="Enter your address:")
    search_button = Button(label="Search", button_type="primary")

    # Status / error message area
    results_div = Div(text="", width=360)

    # Food bank cards list — show all by default
    default_html = render_foodbank_cards(
        foodbank_df,
        title=f"All food banks ({len(foodbank_df)})"
    )
    location_list = Div(
        text=default_html,
        width=360,
        styles={"overflow-y": "auto", "max-height": "480px"}
    )

    sidebar_layout = column(
        Div(
            text=f"""
            <div style='
                padding: 12px 0;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                color: {COLORS['text_secondary']};
                letter-spacing: 0.5px;
            '>Search &amp; Filters</div>"""
        ),
        resource_type_dropdown,
        address_input,
        search_button,
        results_div,
        location_list,
        width=380,
        sizing_mode="fixed"
    )

    # Return both the layout and the widgets for callbacks
    return sidebar_layout, {
        "resource_type_dropdown": resource_type_dropdown,
        "address_input": address_input,
        "search_button": search_button,
        "results_div": results_div,
        "location_list": location_list,
    }

def create_analytics_panel():
    return f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_blue']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Locations</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">across Seattle</div>
        </div>
        
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_green']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Transit Accessible</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">100% coverage</div>
        </div>
        
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_orange']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Avg Accessibility</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">out of 100</div>
        </div>
        
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_green']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Weekly Reach</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">placeholder</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">unique visitors</div>
        </div>
    </div>
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


def create_layout(fig, sidebar):
    analytics_div = Div(text=create_analytics_panel())
    header_div = create_header()
    main_content = row(
        sidebar,
        fig,
        sizing_mode="stretch_both"
    )

    centered_layout = column(
        header_div,
        analytics_div,
        main_content,
        sizing_mode="stretch_both"
    )
    return centered_layout
