from bokeh.layouts import column, row
from bokeh.models import Div, TextInput, Button, Slider, CheckboxGroup, RadioButtonGroup
from pantry_map.utilities.constants import COLORS

def create_sidebar(foodbank_df):
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

    sidebar_layout = column(
        Div(
            text="""
            <div style=
                'padding: 12px 0;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                color: #57606a;
                letter-spacing: 0.5px;
            '>
                Search & Filters
            </div>"""
        ),
        Div(text="<div style='font-size:12px; font-weight:600; margin: 4px 0;'>Food resource type</div>"),
        resource_type_selector,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>Distance from address</div>"),
        distance_slider,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>Operational status</div>"),
        open_only_toggle,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>Eligibility</div>"),
        eligibility_group,
        Div(text="<div style='font-size:12px; font-weight:600; margin: 8px 0 2px;'>Available days</div>"),
        day_group,
        address_input,
        row(search_button, clear_button, width=360),
        results_div,
        width=380,
        sizing_mode="fixed"
    )

    # Return both the layout and the widgets for callbacks
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
