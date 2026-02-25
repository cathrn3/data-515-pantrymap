# Tech Review Demo - PantryMap Visualizations

This folder contains multiple visualization demos for the PantryMap project.

## Available Demos

### 1. Bokeh Demo - Interactive Food Bank Accessibility Map
**Location:** `Bokeh_demo/`

An enterprise-grade interactive dashboard for analyzing food bank accessibility via public transit.

**To run:**
```bash
cd Bokeh_demo
pip install -r requirements_bokeh.txt
bokeh serve --show pantrymap_bokeh.py
```

**Features:**
- Interactive map with accessibility scoring
- Real-time filtering by transit type, distance, and capacity
- Professional CartoDB basemap
- Accessibility analytics dashboard

---

### 2. Dash Demo
**Location:** See other README in this folder for Dash demo instructions

---

**Tech Stack:** Bokeh, Pandas, NumPy, Web Mercator Projection

**Data Source:** Emergency Food and Meals (Seattle & King County)
