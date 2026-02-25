# PantryMap - Professional Food Bank Accessibility Platform

Enterprise-grade interactive dashboard for analyzing food bank accessibility via public transit. Built with Bokeh Server, featuring real-time filtering, accessibility scoring, and geographic visualization.

## Overview

PantryMap is a production-ready dashboard application designed for food security organizations and urban planners. It visualizes food bank locations, calculates accessibility scores based on distance and transit access, and provides advanced filtering capabilities.

**Live at:** http://localhost:5006/pantrymap_enhanced

## Features

### 🗺️ Interactive Map
- **Professional CartoDB Positron basemap** with seamless panning and zooming
- **Color-coded markers** by accessibility score:
  - 🟢 Green (80+) = Highly accessible
  - 🟠 Orange (60-80) = Moderately accessible
  - 🔴 Red (<60) = Limited accessibility
- **Smart bounds calculation** - Map automatically centers on all food banks
- **Hover tooltips** showing:
  - Location name and address
  - Distance from user (miles)
  - Accessibility score (0-100)
  - Weekly visitor count
  - Transit type (Light Rail/Bus)
- **Professional toolbar** with pan, zoom, reset, and save tools

### 📊 Analytics Dashboard
Four key metrics displayed in real-time:
- **Total Locations** - Network size across Seattle
- **Transit Accessible** - Count and percentage with transit access
- **Average Accessibility** - Quality score out of 100
- **Weekly Reach** - Total unique visitors served

All metrics update instantly based on applied filters.

### 🎯 Advanced Filtering System
- **Search by location** - Name or address autocomplete
- **Transit Type Filter** - Choose Light Rail, Bus, or both
- **Accessibility Score Filter** - Range slider (0-100)
- **Distance Filter** - Range slider (0-15 miles)
- **Capacity Filter** - Minimum daily serving capacity

Real-time results counter shows matching locations out of total.

### 📋 Location Cards
Professional card layout displaying:
- Location name with accessibility score badge
- Street address
- Operating hours
- Transit type
- Distance from user
- Weekly visitor metrics

Hover effects provide subtle visual feedback.

### 🧮 Accessibility Score Algorithm
Each location gets a 0-100 score based on:
- **Distance** (70% weight): Closer = higher score
- **Transit Access** (30% weight): Light Rail or Bus access adds points
- **Formula**: `distance_score = max(0, 100 - (distance × 10))` + `transit_bonus`

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# CD into correct directory
cd docs/technology_review

# Install dependencies
pip install -r requirements_bokeh.txt
```

## Running the Dashboard

### Development Mode
```bash
bokeh serve Bokeh_demo.py --port 5006
```

### Automatic Browser Opening
The app automatically opens your browser at:
```
http://localhost:5006/pantrymap_enhanced
```

### Custom Port
```bash
bokeh serve pantrymap_enhanced.py --port 5007
```

## Usage Guide

### Getting Started
1. Launch the app: `bokeh serve pantrymap_enhanced.py`
2. Browser opens automatically to http://localhost:5006/pantrymap_enhanced
3. Dashboard loads with all 10 food banks visible
4. Metrics show full network statistics

### Using the Map
- **Pan**: Click and drag to move around the map
- **Zoom**: Scroll wheel or use +/- buttons
- **Reset**: Click reset button to return to original view
- **Hover**: Move mouse over markers to see full details
- **Export**: Click save button to download map as PNG

### Filtering Results
1. **Search**: Type location name or address to filter instantly
2. **Transit Type**: Check "Light Rail accessible" and/or "Bus accessible"
3. **Accessibility**: Drag slider to show only locations with min score
4. **Distance**: Adjust maximum distance from your location
5. **Capacity**: Set minimum food bank capacity needed
6. **Results**: Counter shows matching locations out of total

Results update in real-time as you adjust any filter. Location cards below map display matching locations sorted by accessibility score.

### Understanding Accessibility Scores
- **80-100 (Green)**: Excellent - Close by and great transit access
- **60-80 (Orange)**: Good - Moderate distance or transit options
- **Below 60 (Red)**: Limited - Far away or poor transit access

## Architecture

### Frontend (Bokeh Client)
- **Responsive layout**: Column/row-based layout system
- **Interactive widgets**: TextInput, CheckboxGroup, RangeSlider
- **Real-time visualization**: Map and cards update instantly
- **Professional styling**: GitHub-style color scheme

### Backend (Bokeh Server)
- **Python callbacks**: All filtering logic in Python
- **ColumnDataSource**: Reactive data binding
- **Haversine formula**: Accurate distance calculations
- **Web Mercator**: Geographic projection for maps
- **WebSocket**: Real-time communication with client

### Data Flow
1. User adjusts filter widget
2. Callback function triggered
3. Data filtered in Python
4. ColumnDataSource updated
5. Map and cards re-render in browser
6. Results counter updates

## Customization

### Update Data Source
Modify the `load_food_bank_data()` function to use your own data:

```python
def load_food_bank_data():
    """Load food bank data from your source"""
    df = pd.read_csv('your_data.csv')
    
    # Ensure columns: name, address, lat, lon, hours, transit, capacity, weekly_visitors
    df['x'], df['y'] = zip(*[
        lat_lon_to_mercator(lat, lon) 
        for lat, lon in zip(df['lat'], df['lon'])
    ])
    
    return df
```

### Change Color Scheme
Update the COLORS dictionary at the top of the file:

```python
COLORS = {
    'bg': '#fafbfc',
    'text_primary': '#0d1117',
    'accent_blue': '#0969da',
    'accent_green': '#1a7f37',
    # ... etc
}
```

### Add More Filters
Create a new widget and add to sidebar:

```python
new_filter = RangeSlider(
    start=0, end=100, value=(0, 100),
    title="New Filter",
    width=360
)

# In update() function:
df_filtered = df_filtered[
    (df_filtered['column'] >= new_filter.value[0]) &
    (df_filtered['column'] <= new_filter.value[1])
]

# Attach callback:
new_filter.on_change('value', lambda attr, old, new: update())
```

### Modify Metrics
Edit the `create_analytics_panel()` function to calculate different metrics:

```python
def create_analytics_panel():
    custom_metric = df['column'].sum()  # Your calculation
    return f"..."  # Update HTML
```

## Deployment

### Development
```bash
bokeh serve pantrymap_enhanced.py
```

### Production with SSL
```bash
bokeh serve pantrymap_enhanced.py \
  --port 5006 \
  --allow-websocket-origin yourdomain.com \
  --use-xheaders
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_bokeh.txt .
RUN pip install -r requirements_bokeh.txt
COPY pantrymap_enhanced.py .
CMD ["bokeh", "serve", "pantrymap_enhanced.py", "--port", "5006", "--allow-websocket-origin=*"]
EXPOSE 5006
```

Build and run:
```bash
docker build -t pantrymap .
docker run -p 5006:5006 pantrymap
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5006
lsof -ti:5006 | xargs kill -9

# Or use different port
bokeh serve pantrymap_enhanced.py --port 5007
```

### Module Import Errors
```bash
# Verify bokeh is installed
pip list | grep bokeh

# Reinstall if needed
pip install --force-reinstall bokeh==3.3.4 pandas numpy
```

### Blank Page
- Check browser console (F12) for errors
- Verify terminal output for Python errors
- Try hard refresh (Cmd+Shift+R or Ctrl+Shift+R)

## Future Enhancements

1. **Real GTFS data** - Integrate actual transit schedules
2. **APIs integration** - Pull live food bank data from databases
3. **User accounts** - Save favorite locations and preferences
4. **Email alerts** - Notify users of new food bank locations
5. **Mobile app** - Native iOS/Android version
6. **Export reports** - Generate PDF/Excel summaries
7. **Feedback system** - Collect user ratings and comments

## Resources

- [Bokeh Documentation](https://docs.bokeh.org/)
- [Bokeh Server Guide](https://docs.bokeh.org/en/latest/docs/user_guide/server.html)
- [Seattle Open Data Portal](https://data.seattle.gov/)
- [Web Mercator Projection](https://en.wikipedia.org/wiki/Web_Mercator_projection)

## License

Educational project for demonstrating professional Bokeh dashboard development.
