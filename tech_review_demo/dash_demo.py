import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy, Input, Output, html
import pandas as pd
import hashlib

def color_from_id(route_id):
    # Generate a color from the route_id
    hex_hash = hashlib.md5(str(route_id).encode()).hexdigest()
    return f"#{hex_hash[:6]}"

# Format food bank markers
food_banks = pd.read_csv("../data/Emergency_Food_and_Meals_Seattle_and_King_County_20260222.csv")
food_banks = food_banks.rename(columns={
    "Latitude": "lat",
    "Longitude": "lon"
})
markers = food_banks[["lat", "lon", "Website"]].to_dict("records")
geojson_foodbank_data = dlx.dicts_to_geojson(markers)

# Format transit routes
transit_data = pd.read_csv("../data/shapes.txt")
polylines = []
for shape_id, group in transit_data.groupby("shape_id"):
    coords = group[["shape_pt_lat", "shape_pt_lon"]].values.tolist()
    polyline = dl.Polyline(positions=coords, color=color_from_id(group["shape_id"]))
    polylines.append(polyline)

# Dash app
app = DashProxy()
app.layout = html.Div(
    [
        dl.Map(
            children=[
                dl.TileLayer(),
                dl.GeoJSON(data=geojson_foodbank_data, id="food banks"),
                *polylines
            ],
            center=[47.5, -122.4],
            zoom=10,
            style={"height": "80vh"}
        ),
        html.Div(id="food bank"),
    ]
)

# Callbacks
@app.callback(Output("food bank", "children"), [Input("food banks", "clickData")])
def capital_click(feature):
    if feature is not None:
        return f"Website for food bank clicked: {feature['properties']['Website']}"

if __name__ == "__main__":
    app.run()
