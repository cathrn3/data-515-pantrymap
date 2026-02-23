## Background/Requirements
- Problem we are solving: want to surface geographic relationships between food banks and ease of transportation to reach. Need a map visualization to highlight relationships.
- Need interactive map
    - Zoom
    - Pan
    - Data updates on filters
    - Side bar pop ups on click
- Draw items on map
    - Food bank locations (latitude and longitude data)
    - Transit routes (have both GIS data for boundaries and coordinate data for routes)

## Python libraries
- Plotly dash
    - Dash is an open-source, low-code framework developed by Plotly for rapidly building analytical web applications and interactive dashboards using only Python
    - Open source
    - Strong support for map data
    - Entirely Python based
    - Some limitations on graph interactions
- Bokeh
    - 