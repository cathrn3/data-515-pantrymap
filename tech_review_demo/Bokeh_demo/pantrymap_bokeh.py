"""
PantryMap - Enterprise Food Bank Accessibility Platform
MLOps-driven analytics for food security and public transit integration
"""

from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from bokeh.models import (
    ColumnDataSource, HoverTool, Div, RangeSlider, TextInput, 
    CheckboxGroup, MultiSelect, Select, CustomJS, DatePicker, Circle
)
from bokeh.plotting import figure
from bokeh.palettes import RdYlGn
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2, pi
from datetime import datetime
import json

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def lat_lon_to_mercator(lat, lon):
    """Convert lat/lon to Web Mercator projection"""
    k = 6378137
    x = lon * (k * pi/180.0)
    y = np.log(np.tan((90 + lat) * pi/360.0)) * k
    return x, y

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in miles using Haversine formula"""
    R = 3959
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 2)

def calculate_accessibility_score(distance, transit_accessible):
    """Calculate accessibility score (0-100) based on distance and transit"""
    distance_score = max(0, 100 - (distance * 10))
    transit_bonus = 20 if transit_accessible else 0
    return min(100, distance_score + transit_bonus)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_food_bank_data():
    """Load food bank data with enhanced attributes"""
    data = {
        'name': [
            'University District Food Bank',
            'Ballard Food Bank', 
            'West Seattle Food Bank',
            'Rainier Valley Food Bank',
            'Capitol Hill Food Bank',
            'Northgate Community Food Bank',
            'White Center Food Bank',
            'Fremont Food Bank',
            'Georgetown Food Pantry',
            'Beacon Hill Food Bank'
        ],
        'address': [
            '5017 Roosevelt Way NE',
            '5130 Leary Ave NW',
            '3419 SW Morgan St',
            '3800 S Othello St',
            '1265 S Main St',
            '10564 5th Ave NE',
            '1035 SW 116th St',
            '1441 N 34th St',
            '6512 13th Ave S',
            '2800 Beacon Ave S'
        ],
        'lat': [47.6634, 47.6661, 47.5383, 47.5376, 47.5992, 47.7089, 47.4983, 47.6494, 47.5456, 47.5794],
        'lon': [-122.3151, -122.3814, -122.3816, -122.2811, -122.3094, -122.3334, -122.3544, -122.3542, -122.3089, -122.3115],
        'hours': [
            'Mon-Fri 9-5',
            'Tue-Sat 10-4',
            'Mon-Fri 10-3',
            'Wed-Fri 11-4',
            'Mon-Thu 12-6',
            'Mon-Fri 9-4',
            'Tue-Thu 10-3',
            'Mon-Wed 1-5',
            'Thu-Sat 11-3',
            'Mon-Fri 10-4'
        ],
        'transit': ['Link', 'Bus', 'Bus', 'Link', 'Link', 'Link', 'Bus', 'Bus', 'Bus', 'Link'],
        'capacity': [150, 200, 120, 180, 160, 140, 130, 110, 95, 175],
        'weekly_visitors': [280, 350, 200, 290, 310, 240, 210, 180, 150, 320],
    }
    
    df = pd.DataFrame(data)
    df['x'], df['y'] = zip(*[lat_lon_to_mercator(lat, lon) for lat, lon in zip(df['lat'], df['lon'])])
    
    # Add user location (Seattle downtown)
    user_lat, user_lon = 47.6062, -122.3321
    
    df['distance'] = df.apply(
        lambda row: calculate_distance(user_lat, user_lon, row['lat'], row['lon']), 
        axis=1
    )
    
    df['transit_accessible'] = df['transit'].isin(['Link', 'Bus']).astype(int)
    df['accessibility_score'] = df.apply(
        lambda row: calculate_accessibility_score(row['distance'], row['transit_accessible']),
        axis=1
    )
    
    return df, user_lat, user_lon

# ============================================================================
# INITIALIZE DATA
# ============================================================================

df = load_food_bank_data()[0]
user_lat, user_lon = load_food_bank_data()[1], load_food_bank_data()[2]
user_x, user_y = lat_lon_to_mercator(user_lat, user_lon)

source = ColumnDataSource(df)
user_source = ColumnDataSource({'x': [user_x], 'y': [user_y]})

# ============================================================================
# UI CONFIGURATION
# ============================================================================

COLORS = {
    'bg': '#fafbfc',
    'border': '#e5e7eb',
    'text_primary': '#0d1117',
    'text_secondary': '#57606a',
    'text_tertiary': '#8c959f',
    'accent_blue': '#0969da',
    'accent_green': '#1a7f37',
    'accent_orange': '#fb8500',
    'accent_red': '#da3633',
    'bg_light': '#f6f8fa',
    'bg_hover': '#eaeef2',
}

# ============================================================================
# HEADER
# ============================================================================

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

# ============================================================================
# ANALYTICS DASHBOARD
# ============================================================================

def create_analytics_panel():
    """Create enterprise analytics dashboard"""
    total_capacity = df['capacity'].sum()
    avg_accessibility = df['accessibility_score'].mean()
    transit_accessible_count = df['transit_accessible'].sum()
    total_weekly_visitors = df['weekly_visitors'].sum()
    
    return f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_blue']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Locations</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">{len(df)}</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">across Seattle</div>
        </div>
        
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_green']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Transit Accessible</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">{transit_accessible_count}/{len(df)}</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">100% coverage</div>
        </div>
        
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_orange']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Avg Accessibility</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">{avg_accessibility:.0f}</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">out of 100</div>
        </div>
        
        <div style="padding: 16px; background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; border-left: 3px solid {COLORS['accent_green']};">
            <div style="color: {COLORS['text_tertiary']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Weekly Reach</div>
            <div style="font-size: 28px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 4px;">{total_weekly_visitors:,}</div>
            <div style="font-size: 12px; color: {COLORS['text_secondary']};">unique visitors</div>
        </div>
    </div>
    """

analytics_div = Div(text=create_analytics_panel())

# ============================================================================
# SEARCH & FILTERS
# ============================================================================

search_input = TextInput(
    placeholder="Search by location...",
    width=360,
    height=36
)

transit_filter = CheckboxGroup(
    labels=["Light Rail accessible", "Bus accessible"],
    active=[0, 1]
)

accessibility_slider = RangeSlider(
    start=0, end=100, value=(60, 100), step=5,
    title="Accessibility Score",
    width=360
)

distance_filter = RangeSlider(
    start=0, end=15, value=(0, 15), step=0.5,
    title="Maximum Distance (mi)",
    width=360
)

capacity_filter = RangeSlider(
    start=0, end=200, value=(0, 200), step=10,
    title="Minimum Capacity",
    width=360
)

results_div = Div(text="")

# ============================================================================
# MAP VISUALIZATION
# ============================================================================

x_min, x_max = df['x'].min(), df['x'].max()
y_min, y_max = df['y'].min(), df['y'].max()
x_padding = (x_max - x_min) * 0.15
y_padding = (y_max - y_min) * 0.15

map_fig = figure(
    x_range=(x_min - x_padding, x_max + x_padding),
    y_range=(y_min - y_padding, y_max + y_padding),
    x_axis_type="mercator",
    y_axis_type="mercator",
    width=1000,
    height=800,
    tools="pan,wheel_zoom,reset,save",
    toolbar_location="above",
    background_fill_color='#fafbfc',
    border_fill_color='#fafbfc',
    outline_line_color='#e5e7eb',
    sizing_mode="scale_width"
)

map_fig.add_tile("CartoDB Positron")
map_fig.toolbar.logo = None
map_fig.xgrid.visible = False
map_fig.ygrid.visible = False
map_fig.toolbar.active_drag = 'auto'

# Add color column to source based on accessibility score
colors = []
for score in df['accessibility_score']:
    if score >= 80:
        colors.append('#1a7f37')  # Green
    elif score >= 60:
        colors.append('#fb8500')  # Orange
    else:
        colors.append('#da3633')  # Red

source.data['color'] = colors

# Food bank markers - sized by accessibility score
markers = map_fig.circle(
    x='x', y='y', size=10,
    color='color',
    alpha=0.85,
    source=source,
    line_color="white",
    line_width=2
)

# Configure selection/hover glyphs to preserve color-coded markers
markers.selection_glyph = Circle(
    fill_color={'field': 'color'},
    fill_alpha=1.0,
    line_color='black',
    line_width=2.5,
    size=12
)
markers.nonselection_glyph = Circle(
    fill_color={'field': 'color'},
    fill_alpha=0.85,
    line_color='white',
    line_width=2,
    size=10
)
markers.hover_glyph = Circle(
    fill_color={'field': 'color'},
    fill_alpha=1.0,
    line_color='black',
    line_width=2.5,
    size=12
)

# User location
map_fig.circle(
    x='x', y='y', size=14,
    color='#2563eb',
    alpha=1.0,
    source=user_source,
    line_color="white",
    line_width=2.5
)

# Hover information
hover = HoverTool(
    renderers=[markers],
    tooltips=[
        ("Name", "@name"),
        ("Address", "@address"),
        ("Distance", "@distance{0.00} mi"),
        ("Accessibility Score", "@accessibility_score{0}"),
        ("Weekly Visitors", "@weekly_visitors"),
        ("Transit", "@transit"),
    ]
)
map_fig.add_tools(hover)

# ============================================================================
# LOCATION LIST
# ============================================================================

def create_location_list():
    items = []
    for _, row in df.sort_values('accessibility_score', ascending=False).iterrows():
        score = int(row['accessibility_score'])
        score_color = '#1a7f37' if score >= 80 else '#fb8500' if score >= 60 else '#da3633'
        
        items.append(f"""
        <div style="padding: 14px 0; border-bottom: 1px solid {COLORS['border']}; transition: background-color 0.2s;"
             onmouseover="this.style.backgroundColor='{COLORS['bg_hover']}'" 
             onmouseout="this.style.backgroundColor='transparent'">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                        <h4 style="margin: 0; font-size: 14px; font-weight: 600; color: {COLORS['text_primary']};">
                            {row['name']}
                        </h4>
                        <div style="padding: 2px 8px; background: {score_color}; color: white; border-radius: 4px; font-size: 11px; font-weight: 600;">
                            {score}
                        </div>
                    </div>
                    <p style="margin: 0 0 6px 0; font-size: 13px; color: {COLORS['text_secondary']};"> 
                        {row['address']}
                    </p>
                    <div style="display: flex; gap: 16px; font-size: 11px; color: {COLORS['text_tertiary']};">
                        <span>{row['hours']}</span>
                        <span>{row['transit']}</span>
                        <span>{row['distance']} mi</span>
                    </div>
                </div>
                <div style="text-align: right; flex-shrink: 0; min-width: 50px;">
                    <div style="font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};"> {int(row['weekly_visitors'])}</div>
                    <div style="font-size: 10px; color: {COLORS['text_tertiary']}; margin-top: 2px;">weekly</div>
                </div>
            </div>
        </div>
        """)
    
    return f"""
    <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; overflow: hidden; padding: 14px;">
        {''.join(items)}
    </div>
    """

location_list = Div(text=create_location_list())

# ============================================================================
# UPDATE FUNCTION
# ============================================================================

def update():
    """Update all visualizations based on filters"""
    df_filtered = df.copy()
    
    # Distance filter
    min_dist, max_dist = distance_filter.value
    df_filtered = df_filtered[
        (df_filtered['distance'] >= min_dist) & 
        (df_filtered['distance'] <= max_dist)
    ]
    
    # Accessibility filter
    min_acc, max_acc = accessibility_slider.value
    df_filtered = df_filtered[
        (df_filtered['accessibility_score'] >= min_acc) & 
        (df_filtered['accessibility_score'] <= max_acc)
    ]
    
    # Transit filter
    transit_types = []
    if 0 in transit_filter.active:
        transit_types.append('Link')
    if 1 in transit_filter.active:
        transit_types.append('Bus')
    
    if transit_types:
        df_filtered = df_filtered[df_filtered['transit'].isin(transit_types)]
    
    # Capacity filter
    min_cap, max_cap = capacity_filter.value
    df_filtered = df_filtered[
        (df_filtered['capacity'] >= min_cap) & 
        (df_filtered['capacity'] <= max_cap)
    ]
    
    # Search filter
    if search_input.value:
        search_term = search_input.value.lower()
        df_filtered = df_filtered[
            df_filtered['name'].str.lower().str.contains(search_term) |
            df_filtered['address'].str.lower().str.contains(search_term)
        ]
    
    # Recalculate colors based on filtered data
    colors = []
    for score in df_filtered['accessibility_score']:
        if score >= 80:
            colors.append('#1a7f37')  # Green
        elif score >= 60:
            colors.append('#fb8500')  # Orange
        else:
            colors.append('#da3633')  # Red
    
    # Update source
    source.data = dict(df_filtered)
    source.data['color'] = colors
    
    # Recalculate map bounds based on filtered data
    if len(df_filtered) > 0:
        x_min_filtered = df_filtered['x'].min()
        x_max_filtered = df_filtered['x'].max()
        y_min_filtered = df_filtered['y'].min()
        y_max_filtered = df_filtered['y'].max()
        
        # Add 15% padding to all sides
        x_padding = (x_max_filtered - x_min_filtered) * 0.15 if (x_max_filtered - x_min_filtered) > 0 else 50000
        y_padding = (y_max_filtered - y_min_filtered) * 0.15 if (y_max_filtered - y_min_filtered) > 0 else 50000
        
        # Update map bounds to show all filtered results
        map_fig.x_range.start = x_min_filtered - x_padding
        map_fig.x_range.end = x_max_filtered + x_padding
        map_fig.y_range.start = y_min_filtered - y_padding
        map_fig.y_range.end = y_max_filtered + y_padding
    
    # Update results count
    results_div.text = f"""
    <div style="padding: 12px 0; color: {COLORS['text_secondary']}; font-size: 13px; border-bottom: 1px solid {COLORS['border']}; margin-bottom: 12px;">
        Showing <strong style="color: {COLORS['text_primary']}; font-weight: 600;">{len(df_filtered)}</strong> of <strong style="color: {COLORS['text_primary']}; font-weight: 600;">{len(df)}</strong> locations
    </div>
    """
    
    # Update location list
    if len(df_filtered) > 0:
        items = []
        for _, row in df_filtered.sort_values('accessibility_score', ascending=False).iterrows():
            score = int(row['accessibility_score'])
            score_color = '#1a7f37' if score >= 80 else '#fb8500' if score >= 60 else '#da3633'
            
            items.append(f"""
            <div style="padding: 14px 0; border-bottom: 1px solid {COLORS['border']}; transition: background-color 0.2s;"
                 onmouseover="this.style.backgroundColor='{COLORS['bg_hover']}'" 
                 onmouseout="this.style.backgroundColor='transparent'">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <h4 style="margin: 0; font-size: 14px; font-weight: 600; color: {COLORS['text_primary']};">
                                {row['name']}
                            </h4>
                            <div style="padding: 2px 8px; background: {score_color}; color: white; border-radius: 4px; font-size: 11px; font-weight: 600;">
                                {score}
                            </div>
                        </div>
                        <p style="margin: 0 0 6px 0; font-size: 13px; color: {COLORS['text_secondary']};"> 
                            {row['address']}
                        </p>
                        <div style="display: flex; gap: 16px; font-size: 11px; color: {COLORS['text_tertiary']};">
                            <span>{row['hours']}</span>
                            <span>{row['transit']}</span>
                            <span>{row['distance']} mi</span>
                        </div>
                    </div>
                    <div style="text-align: right; flex-shrink: 0; min-width: 50px;">
                        <div style="font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};"> {int(row['weekly_visitors'])}</div>
                        <div style="font-size: 10px; color: {COLORS['text_tertiary']}; margin-top: 2px;">weekly</div>
                    </div>
                </div>
            </div>
            """)
        
        location_list.text = f"""
        <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; overflow: hidden; padding: 14px;">
            {''.join(items)}
        </div>
        """
    else:
        location_list.text = f"""
        <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 40px 20px; text-align: center; color: {COLORS['text_tertiary']}; font-size: 13px;">
            No locations match your filters. Try adjusting your search criteria.
        </div>
        """

# ============================================================================
# CALLBACKS
# ============================================================================

search_input.on_change('value', lambda attr, old, new: update())
transit_filter.on_change('active', lambda attr, old, new: update())
accessibility_slider.on_change('value', lambda attr, old, new: update())
distance_filter.on_change('value', lambda attr, old, new: update())
capacity_filter.on_change('value', lambda attr, old, new: update())

# ============================================================================
# LAYOUT
# ============================================================================

sidebar = column(
    Div(text="<div style='padding: 12px 0; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #57606a; letter-spacing: 0.5px;'>Search & Filters</div>"),
    search_input,
    Div(text="<div style='margin-top: 16px; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #57606a; letter-spacing: 0.5px;'>Transit Type</div>"),
    transit_filter,
    Div(text="<div style='margin-top: 16px;'></div>"),
    accessibility_slider,
    Div(text="<div style='margin-top: 12px;'></div>"),
    distance_filter,
    Div(text="<div style='margin-top: 12px;'></div>"),
    capacity_filter,
    Div(text="<div style='margin-top: 16px;'></div>"),
    results_div,
    location_list,
    width=380,
    height=900,
    sizing_mode="fixed"
)

main_content = row(
    sidebar,
    map_fig,
    sizing_mode="stretch_both"
)

centered_layout = column(
    header_div,
    analytics_div,
    main_content,
    sizing_mode="stretch_both"
)

# ============================================================================
# DOCUMENT SETUP
# ============================================================================

def make_doc(doc):
    doc.add_root(centered_layout)
    doc.title = "PantryMap"
    doc.theme = "light"

curdoc().add_root(centered_layout)
curdoc().title = "PantryMap"

# ============================================================================
# BOKEH SERVER
# ============================================================================
# To run this app, use: bokeh serve --show pantrymap_bokeh.py
