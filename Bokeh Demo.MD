PantryMap Bokeh Professional Dashboard
Enterprise-grade interactive food bank accessibility analysis system built with Bokeh Server.

Overview
This is a production-ready, professional dashboard application designed for analyzing food bank accessibility via public transit. Bokeh is used extensively in enterprise environments, scientific computing, and data science teams at companies like Netflix, Bloomberg, and NASA.

Features

1. Interactive Map Tab

Professional tile-based map using CartoDB Positron tiles
Color-coded markers for transit accessibility:

🟢 Green = Fully accessible
🔴 Red = Not accessible
🟠 Orange = Limited access

Advanced hover tooltips showing all food bank details
Pan, zoom, and box select tools
User location marker (red asterisk)
Interactive legend (click to show/hide categories)
Export functionality (save as PNG)

2. Data Table Tab

Sortable data table with all food bank information
Selectable rows for detailed inspection
Formatted numbers (distance to 2 decimal places)
Professional styling with proper column headers

3. Analytics Tab

Wait time analysis - Color-coded bar chart by accessibility
Distance analysis - Blue bar chart showing proximity to user
Capacity analysis - Purple bar chart showing daily capacity
Dynamic updates - All charts update based on filters

4. Real-time Filters

Transit accessibility checkbox
Maximum wait time slider (0-30 minutes)
Maximum distance slider (0-10 miles)
Service selector dropdown (Fresh produce, Hot meals, Halal, etc.)
Instant updates - Dashboard reacts immediately to changes

5. Statistics Dashboard

Total food banks counter
Transit accessible count
Average wait time calculation
Filtered results counter
Professional card layout with color-coded metrics

Installation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_bokeh.txt

Running the Dashboard

# Start Bokeh server
bokeh serve pantrymap_bokeh_demo.py

# Or specify custom port
bokeh serve pantrymap_bokeh_demo.py --port 5006

Access the dashboard:

Default: http://localhost:5006/pantrymap_bokeh_demo
The server runs continuously and handles multiple concurrent users

Usage Guide
Initial View

Dashboard loads showing all 10 food banks
Map centered on Seattle with appropriate zoom
Statistics show full dataset metrics
All filters set to maximum values (show everything)

Filtering Data

Transit Filter: Check box to show only transit-accessible locations
Wait Time: Drag slider left to reduce maximum acceptable wait
Distance: Adjust slider to limit search radius
Services: Select specific service from dropdown

Map Interaction

Pan: Click and drag to move around map
Zoom: Scroll wheel or use zoom tools
Hover: Move mouse over markers to see details
Legend: Click legend items to hide/show categories
Reset: Click reset button to return to original view
Save: Click save button to export map as PNG

Data Table

Sort: Click column headers to sort data
Select: Click rows to highlight them
Inspect: View all details in formatted table

Analytics

View all three charts showing different metrics
Charts automatically filter based on sidebar selections
X-axis labels rotate for readability

Technology Stack
Bokeh Server Architecture

Server-side Python: All computation happens on server
WebSocket communication: Real-time updates
Tornado web server: Handles HTTP and WebSocket
Automatic scaling: Can handle multiple concurrent users

Key Components

ColumnDataSource: Reactive data binding
Tile providers: Professional map tiles
HoverTool: Rich interactive tooltips
Callbacks: Python-based interactivity
Layouts: Responsive grid system

