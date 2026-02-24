"""
PantryMap Dashboard - Bokeh Server Application
Interactive food bank finder with transit accessibility
"""

from bokeh.io import curdoc
from bokeh.layouts import column, row, layout
from bokeh.models import (
    ColumnDataSource, HoverTool, Select, CheckboxGroup, Slider, Div,
    Button, DataTable, TableColumn, NumberFormatter, RangeSlider,
    Panel, Tabs, CustomJS 
)
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10_10
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2, pi

# Constants for Web Mercator projection
def lat_lon_to_mercator(lat, lon):
    """Convert lat/lon to Web Mercator coordinates"""
    k = 6378137  # Earth radius in meters
    x = lon * (k * pi/180.0)
    y = np.log(np.tan((90 + lat) * pi/360.0)) * k
    return x, y

def mercator_to_lat_lon(x, y):
    """Convert Web Mercator to lat/lon"""
    k = 6378137
    lon = (x / k) * (180.0 / pi)
    lat = (2 * np.arctan(np.exp(y / k)) - pi/2) * (180.0 / pi)
    return lat, lon

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in miles"""
    R = 3959  # Earth's radius in miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 2)

# Load sample data
def load_data():
    """Load food bank data"""
    data = {
        'name': [
            'University District Food Bank',
            'Ballard Food Bank',
            'West Seattle Food Bank',
            'Rainier Valley Food Bank',
            'Capitol Hill Food Bank',
            'Northgate Community Food Bank',
            'White Center Food Bank',
            'Green Lake Food Pantry',
            'Fremont Food Bank',
            'Georgetown Food Pantry'
        ],
        'address': [
            '5017 Roosevelt Way NE, Seattle, WA 98105',
            '5130 Leary Ave NW, Seattle, WA 98107',
            '3419 SW Morgan St, Seattle, WA 98126',
            '3800 S Othello St, Seattle, WA 98118',
            '1265 S Main St, Seattle, WA 98144',
            '10564 5th Ave NE, Seattle, WA 98125',
            '1035 SW 116th St, Seattle, WA 98146',
            '7900 East Green Lake Dr N, Seattle, WA 98103',
            '1441 N 34th St, Seattle, WA 98103',
            '6512 13th Ave S, Seattle, WA 98108'
        ],
        'lat': [47.6634, 47.6661, 47.5383, 47.5376, 47.5992, 47.7089, 47.4983, 47.6805, 47.6494, 47.5456],
        'lon': [-122.3151, -122.3814, -122.3816, -122.2811, -122.3094, -122.3334, -122.3544, -122.3210, -122.3542, -122.3089],
        'hours': [
            'Mon-Fri 9AM-5PM',
            'Tue-Sat 10AM-4PM',
            'Mon-Fri 10AM-3PM',
            'Wed-Fri 11AM-4PM',
            'Mon-Thu 12PM-6PM',
            'Mon-Fri 9AM-4PM',
            'Tue-Thu 10AM-3PM',
            'Mon-Fri 10AM-2PM',
            'Mon-Wed 1PM-5PM',
            'Thu-Sat 11AM-3PM'
        ],
        'services': [
            'Fresh produce, Halal, Delivery',
            'Hot meals, Groceries, Seniors',
            'Fresh produce, Baby food, Pets',
            'Multicultural, Classes',
            'LGBTQ+ friendly, Mental health',
            'Bilingual, Immigration',
            'Fresh produce, ESL',
            'Organic, Nutrition',
            'Community kitchen, Fresh',
            'Emergency services, Referrals'
        ],
        'transit_accessible': ['Yes', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'Limited'],
        'nearest_stop': [
            'U-District Station (5 min)',
            'Ballard Ave (3 min)',
            'Limited access',
            'Othello Station (8 min)',
            'Capitol Hill Station (10 min)',
            'Northgate Station (6 min)',
            'Limited access',
            'Route 16 (4 min)',
            'Fremont Ave (7 min)',
            'Route 60 (12 min)'
        ],
        'wait_time': [15, 20, 10, 25, 18, 12, 8, 15, 22, 14],
        'capacity': [150, 200, 100, 180, 120, 140, 90, 110, 160, 95]
    }
    df = pd.DataFrame(data)
    
    # Convert to Web Mercator
    df['x'], df['y'] = zip(*[lat_lon_to_mercator(lat, lon) for lat, lon in zip(df['lat'], df['lon'])])
    
    return df

# Initialize data
df_original = load_data()
user_lat, user_lon = 47.6062, -122.3321  # Default: Seattle center
user_x, user_y = lat_lon_to_mercator(user_lat, user_lon)

# Calculate distances
df_original['distance'] = df_original.apply(
    lambda row: calculate_distance(user_lat, user_lon, row['lat'], row['lon']),
    axis=1
)

# Color mapping for transit accessibility
color_map = {'Yes': '#2ecc71', 'No': '#e74c3c', 'Limited': '#f39c12'}
df_original['color'] = df_original['transit_accessible'].map(color_map)

# Create ColumnDataSource
source = ColumnDataSource(df_original)

# Create map figure
tile_provider = get_provider(Vendors.CARTODBPOSITRON)

p_map = figure(
    x_range=(-13650000, -13610000),
    y_range=(6000000, 6040000),
    x_axis_type="mercator",
    y_axis_type="mercator",
    width=900,
    height=600,
    title="Food Bank Locations - Seattle Area",
    tools="pan,wheel_zoom,box_zoom,reset,save",
    toolbar_location="above"
)

p_map.add_tile(tile_provider)

# Add food bank markers
food_bank_markers = p_map.circle(
    x='x',
    y='y',
    size=15,
    color='color',
    alpha=0.8,
    source=source,
    legend_field='transit_accessible'
)

# Add user location marker
user_source = ColumnDataSource(data={'x': [user_x], 'y': [user_y]})
p_map.asterisk(
    x='x',
    y='y',
    size=25,
    color='red',
    alpha=1.0,
    source=user_source,
    legend_label='Your Location'
)

# Configure hover tool
hover = HoverTool(
    renderers=[food_bank_markers],
    tooltips=[
        ("Name", "@name"),
        ("Address", "@address"),
        ("Hours", "@hours"),
        ("Transit", "@nearest_stop"),
        ("Wait Time", "@wait_time min"),
        ("Distance", "@distance mi"),
        ("Services", "@services")
    ]
)
p_map.add_tools(hover)

# Configure legend
p_map.legend.location = "top_right"
p_map.legend.click_policy = "hide"
p_map.legend.background_fill_alpha = 0.8

# Create wait time bar chart
p_wait = figure(
    x_range=df_original['name'].tolist(),
    height=300,
    width=900,
    title="Average Wait Time by Location",
    toolbar_location=None,
    tools=""
)

p_wait.vbar(
    x='name',
    top='wait_time',
    width=0.8,
    source=source,
    color='color',
    alpha=0.8
)

p_wait.xaxis.major_label_orientation = pi/4
p_wait.yaxis.axis_label = "Wait Time (minutes)"

# Create distance chart
p_distance = figure(
    x_range=df_original['name'].tolist(),
    height=300,
    width=900,
    title="Distance from Your Location",
    toolbar_location=None,
    tools=""
)

p_distance.vbar(
    x='name',
    top='distance',
    width=0.8,
    source=source,
    color='#3498db',
    alpha=0.8
)

p_distance.xaxis.major_label_orientation = pi/4
p_distance.yaxis.axis_label = "Distance (miles)"

# Create capacity chart
p_capacity = figure(
    x_range=df_original['name'].tolist(),
    height=300,
    width=900,
    title="Daily Capacity",
    toolbar_location=None,
    tools=""
)

p_capacity.vbar(
    x='name',
    top='capacity',
    width=0.8,
    source=source,
    color='#9b59b6',
    alpha=0.8
)

p_capacity.xaxis.major_label_orientation = pi/4
p_capacity.yaxis.axis_label = "People per day"

# Create data table
columns = [
    TableColumn(field="name", title="Food Bank"),
    TableColumn(field="distance", title="Distance (mi)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="transit_accessible", title="Transit"),
    TableColumn(field="wait_time", title="Wait (min)"),
    TableColumn(field="hours", title="Hours"),
]

data_table = DataTable(
    source=source,
    columns=columns,
    width=900,
    height=400,
    index_position=None,
    selectable=True
)

# Create filter widgets
transit_checkbox = CheckboxGroup(
    labels=["Transit Accessible Only"],
    active=[]
)

wait_slider = Slider(
    start=0,
    end=30,
    value=30,
    step=5,
    title="Maximum Wait Time (minutes)"
)

distance_slider = Slider(
    start=0,
    end=10,
    value=10,
    step=0.5,
    title="Maximum Distance (miles)"
)

service_select = Select(
    title="Required Service:",
    value="All",
    options=["All", "Fresh produce", "Hot meals", "Halal", "Delivery", "Bilingual"]
)

# Statistics divs
stats_html = """
<div style="padding: 15px; background: #ecf0f1; border-radius: 5px; margin: 10px 0;">
    <h3 style="margin: 0 0 10px 0; color: #2c3e50;">Dashboard Statistics</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
        <div style="text-align: center; padding: 15px; background: white; border-radius: 5px;">
            <div style="font-size: 32px; font-weight: bold; color: #3498db;">{total}</div>
            <div style="color: #7f8c8d; margin-top: 5px;">Total Food Banks</div>
        </div>
        <div style="text-align: center; padding: 15px; background: white; border-radius: 5px;">
            <div style="font-size: 32px; font-weight: bold; color: #2ecc71;">{transit}</div>
            <div style="color: #7f8c8d; margin-top: 5px;">Transit Accessible</div>
        </div>
        <div style="text-align: center; padding: 15px; background: white; border-radius: 5px;">
            <div style="font-size: 32px; font-weight: bold; color: #e74c3c;">{avg_wait:.0f}</div>
            <div style="color: #7f8c8d; margin-top: 5px;">Avg Wait (min)</div>
        </div>
        <div style="text-align: center; padding: 15px; background: white; border-radius: 5px;">
            <div style="font-size: 32px; font-weight: bold; color: #9b59b6;">{filtered}</div>
            <div style="color: #7f8c8d; margin-top: 5px;">Filtered Results</div>
        </div>
    </div>
</div>
"""

stats_div = Div(text=stats_html.format(
    total=len(df_original),
    transit=len(df_original[df_original['transit_accessible'] == 'Yes']),
    avg_wait=df_original['wait_time'].mean(),
    filtered=len(df_original)
))

# Header
header_html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; color: white; border-radius: 10px; margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 36px;">🍽️ PantryMap Professional Dashboard</h1>
    <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
        Enterprise Food Bank Accessibility Analysis System
    </p>
</div>
"""
header = Div(text=header_html)

# Info panel
info_html = """
<div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; 
            border-radius: 5px; margin: 10px 0;">
    <h4 style="margin: 0 0 10px 0; color: #856404;">
        ℹ️ How to Use This Dashboard
    </h4>
    <ul style="margin: 0; padding-left: 20px; color: #856404;">
        <li>Use filters on the right to refine food bank search</li>
        <li>Hover over map markers for detailed information</li>
        <li>Click legend items to show/hide categories</li>
        <li>Pan and zoom the map to explore different areas</li>
        <li>View detailed data in the table tab</li>
    </ul>
</div>
"""
info_div = Div(text=info_html)

# Update function
def update_data():
    """Update data based on filters"""
    df_filtered = df_original.copy()
    
    # Transit filter
    if 0 in transit_checkbox.active:
        df_filtered = df_filtered[df_filtered['transit_accessible'] == 'Yes']
    
    # Wait time filter
    df_filtered = df_filtered[df_filtered['wait_time'] <= wait_slider.value]
    
    # Distance filter
    df_filtered = df_filtered[df_filtered['distance'] <= distance_slider.value]
    
    # Service filter
    if service_select.value != "All":
        df_filtered = df_filtered[df_filtered['services'].str.contains(service_select.value, case=False)]
    
    # Update source
    source.data = dict(df_filtered)
    
    # Update charts x_range
    names = df_filtered['name'].tolist()
    p_wait.x_range.factors = names
    p_distance.x_range.factors = names
    p_capacity.x_range.factors = names
    
    # Update statistics
    stats_div.text = stats_html.format(
        total=len(df_original),
        transit=len(df_original[df_original['transit_accessible'] == 'Yes']),
        avg_wait=df_original['wait_time'].mean(),
        filtered=len(df_filtered)
    )

# Attach callbacks
transit_checkbox.on_change('active', lambda attr, old, new: update_data())
wait_slider.on_change('value', lambda attr, old, new: update_data())
distance_slider.on_change('value', lambda attr, old, new: update_data())
service_select.on_change('value', lambda attr, old, new: update_data())

# Create tabs
tab1 = Panel(child=column(p_map, info_div), title="📍 Interactive Map")
tab2 = Panel(child=data_table, title="📊 Data Table")
tab3 = Panel(child=column(p_wait, p_distance, p_capacity), title="📈 Analytics")

tabs = Tabs(tabs=[tab1, tab2, tab3])

# Create filter panel
filters = column(
    Div(text="<h3 style='margin: 0 0 15px 0;'>🔍 Filters</h3>"),
    transit_checkbox,
    wait_slider,
    distance_slider,
    service_select,
    Div(text="<hr style='margin: 20px 0;'>"),
    Div(text="""
        <div style='padding: 10px; background: #e8f5e9; border-radius: 5px;'>
            <strong>💡 Tip:</strong> Adjust filters to find food banks 
            that best match your needs and location.
        </div>
    """)
)

# Create layout
main_content = column(header, stats_div, tabs, sizing_mode="stretch_width")
sidebar = column(filters, width=300)

final_layout = row(main_content, sidebar, sizing_mode="stretch_width")

# Add to document
curdoc().add_root(final_layout)
curdoc().title = "PantryMap Professional Dashboard"
