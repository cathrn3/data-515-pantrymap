import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy, Input, Output, html, dcc
import pandas as pd
import hashlib

def color_from_id(route_id):
    # Generate a color from the route_id
    hex_hash = hashlib.md5(str(route_id).encode()).hexdigest()
    return f"#{hex_hash[:6]}"

############################
#         Markers          #
############################
food_banks = pd.read_csv("../../data/Emergency_Food_and_Meals_Seattle_and_King_County_20260222.csv")
food_banks = food_banks.rename(columns={
    "Latitude": "lat",
    "Longitude": "lon"
})
markers = food_banks[["lat", "lon", "Website"]].to_dict("records")
geojson_foodbank_data = dlx.dicts_to_geojson(markers)

############################
#        Polylines         #
############################
transit_data = pd.read_csv("../../data/shapes.txt")
polylines = []
for shape_id, group in transit_data.groupby("shape_id"):
    coords = group[["shape_pt_lat", "shape_pt_lon"]].values.tolist()
    polyline = dl.Polyline(positions=coords, color=color_from_id(group["shape_id"]))
    polylines.append(polyline)

############################
#          Setup           #
############################
app = DashProxy()
app.layout = html.Div(
    [
        dl.Map(
            children=[
                dl.TileLayer(), # Default map tiles
                dl.GeoJSON(data=geojson_foodbank_data, id="food banks"), # Markers
                *polylines # Polylines
            ],
            center=[47.5, -122.4],
            zoom=10,
            style={"height": "80vh"}
        ),
        dcc.Input( # User input
            id="input address",
            type="text",
            placeholder="",
            debounce=True
        ),
        dcc.Dropdown( # Dropdown filter
            ["All"] + list(food_banks["Who They Serve"].unique()),
            multi=True,
            id="filter",
            clearable=True,
            value=["All"]
        ),
        html.Div(id="food bank"),
        html.Div(id="output address"),
    ]
)

############################
#        Callbacks         #
############################
# Event handling (User clicks)
@app.callback(Output("food bank", "children"), [Input("food banks", "clickData")])
def food_bank_click(feature):
    if feature is not None:
        return f"Website for food bank clicked: {feature['properties']['Website']}"

# User inputs
@app.callback(Output("output address", "children"), [Input("input address", "value")])
def enter_address(value):
    if value is not None:
        return f"Closest address to {value} is: TBD"

# Applying filters
@app.callback(Output("food banks", "data"), [Input("filter", "value")])
def filter_foodbanks(value):
    if value is None or "All" in value:
        return geojson_foodbank_data
    mask = food_banks["Who They Serve"].isin(value)
    filtered_food_banks = food_banks[mask]
    updated_markers = filtered_food_banks[["lat", "lon", "Website"]].to_dict("records")
    return dlx.dicts_to_geojson(updated_markers)

if __name__ == "__main__":
    app.run()
