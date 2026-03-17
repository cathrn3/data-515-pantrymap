"""Tests for main.py callbacks.

main.py executes at import time (loads data, builds map, wires callbacks),
so we patch the data loaders and curdoc before importing it.
"""
import sys
import unittest
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Fake data that the loaders will return
# ---------------------------------------------------------------------------
_FOODBANK_DF = pd.DataFrame({
    "Agency": ["Bank A", "Bank B"],
    "Food Resource Type": ["Food Bank", "Meal"],
    "Operational Status": ["Open", "Open"],
    "Who They Serve": ["General Public", "General Public"],
    "Days/Hours": ["Monday", "Tuesday"],
    "Latitude": [47.60, 47.61],
    "Longitude": [-122.33, -122.34],
    "x": [-13619000, -13618000],
    "y": [6049000, 6050000],
    "bank_id": ["b1", "b2"],
    "Location": ["Loc A", "Loc B"],
    "Address": ["1 St", "2 St"],
    "Phone Number": ["555-0001", "555-0002"],
    "Website": [None, None],
})

_SHAPES_DF = pd.DataFrame({
    "x": [-13619000, -13618000],
    "y": [6049000, 6050000],
    "color": ["#aabbcc", "#aabbcc"],
    "route_id": ["R1", "R1"],
    "direction_id": [0, 0],
    "unique_key": ["s1", "s2"],
})

_GROUPED_SHAPES_DF = (
    _SHAPES_DF.groupby(["route_id", "direction_id"])
    .agg({"x": list, "y": list, "color": "first"})
    .reset_index()
)

_TRANSIT_DF = pd.DataFrame({
    "unique_key": ["s1", "s2"],
    "stop_lat": [47.60, 47.61],
    "stop_lon": [-122.33, -122.34],
    "route_short_name": ["44", "44"],
    "next_stop": ["s2", None],
    "estimated_travel_time_minutes_between_stops": [5.0, None],
    "color": ["#aabbcc", "#aabbcc"],
})

_TRANSFERS_DF = pd.DataFrame({
    "source_node": pd.Series(dtype=str),
    "nearby_node": pd.Series(dtype=str),
    "estimated_time": pd.Series(dtype=float),
})


# ---------------------------------------------------------------------------
# Patch everything that runs at import time, then import main.
# The import must happen after patches are active, hence the pylint disable.
# ---------------------------------------------------------------------------
_shapes_return = (_SHAPES_DF.copy(), _GROUPED_SHAPES_DF.copy())
_patches = [
    patch("pantry_map.data.loader.get_foodbank_df",
          return_value=_FOODBANK_DF.copy()),
    patch("pantry_map.data.loader.get_shapes_df",
          return_value=_shapes_return),
    patch("pantry_map.data.loader.get_transit_df",
          return_value=_TRANSIT_DF.copy()),
    patch("pantry_map.data.loader.get_transfers_df",
          return_value=_TRANSFERS_DF.copy()),
    patch("bokeh.io.curdoc", return_value=MagicMock()),
]

for p in _patches:
    p.start()

# Remove any cached import so our patches take effect
sys.modules.pop("pantry_map.main", None)

# pylint: disable=wrong-import-position,wrong-import-order
import pantry_map.main as main_mod

for p in _patches:
    p.stop()


# pylint: disable=protected-access
class TestSafeCalculateDistance(unittest.TestCase):
    """Tests for the _safe_calculate_distance helper."""

    def test_valid_coords(self):
        """Valid coordinates return a finite distance."""
        dist = main_mod._safe_calculate_distance(47.6, -122.3, 47.7, -122.3)
        self.assertTrue(0 < dist < 100)

    def test_bad_inputs_return_inf(self):
        """None, non-numeric, and NaN inputs all return np.inf."""
        safe = main_mod._safe_calculate_distance
        self.assertEqual(safe(None, -122, 47, -122), np.inf)
        self.assertEqual(safe(47, -122, "x", -122), np.inf)
        self.assertEqual(safe(47, -122, float("nan"), -122), np.inf)


class TestUpdate(unittest.TestCase):
    """Tests for the update() callback."""

    def setUp(self):
        """Reset state before each test."""
        main_mod.user_location["lat"] = None
        main_mod.user_location["lon"] = None
        main_mod.foodbank_source.selected.indices = []
        main_mod.resource_type_selector.active = 0  # "Both"
        main_mod.distance_slider.value = 10
        main_mod.eligibility_group.value = []
        main_mod.day_group.value = []

    def test_basic_update_populates_sidebar(self):
        """Sidebar should contain food bank names after update."""
        main_mod.update()
        html = main_mod.nearby_widgets["location_list"].text
        self.assertIn("Bank A", html)

    def test_with_user_location_filters_by_distance(self):
        """With a user location set, distance filtering should apply."""
        main_mod.user_location["lat"] = 47.60
        main_mod.user_location["lon"] = -122.33
        main_mod.distance_slider.value = 1
        main_mod.update()
        html = main_mod.nearby_widgets["location_list"].text
        self.assertIn("Bank A", html)

    def test_selected_marker_skips_sidebar(self):
        """When a marker is selected, update() should not overwrite the sidebar."""
        main_mod.nearby_widgets["location_list"].text = "BEFORE"
        # Patch as a property so Bokeh's on_change callback isn't triggered
        # (direct assignment to .indices fires the wired marker_callback)
        with patch.object(type(main_mod.foodbank_source.selected), "indices",
                          new_callable=lambda: property(lambda s: [0])):
            main_mod.update()
        self.assertEqual(main_mod.nearby_widgets["location_list"].text, "BEFORE")


class TestOnSearchClick(unittest.TestCase):
    """Tests for the on_search_click() callback."""

    def setUp(self):
        """Reset search-related state."""
        main_mod.user_location["lat"] = None
        main_mod.user_location["lon"] = None
        main_mod.address_input.value = ""
        main_mod.search_widgets["results_div"].text = ""
        main_mod.foodbank_source.selected.indices = []

    def test_empty_address_shows_error(self):
        """Empty address input should show a red error message."""
        main_mod.address_input.value = ""
        main_mod.on_search_click()
        self.assertIn("color:red", main_mod.search_widgets["results_div"].text)

    @patch("pantry_map.main.geocode_address", return_value=(None, None))
    def test_geocode_failure(self, _mock):
        """Failed geocoding should show 'Could not find' message."""
        main_mod.address_input.value = "123 Fake St"
        main_mod.on_search_click()
        self.assertIn("Could not find", main_mod.search_widgets["results_div"].text)

    @patch("pantry_map.main.geocode_address", return_value=(47.6, -122.33))
    def test_success(self, _mock):
        """Successful geocoding should place pin and show green message."""
        main_mod.address_input.value = "123 Real St, Seattle"
        main_mod.on_search_click()
        self.assertEqual(main_mod.user_location["lat"], 47.6)
        self.assertTrue(len(main_mod.user_source.data["x"]) > 0)
        self.assertIn("color:green", main_mod.search_widgets["results_div"].text)


class TestOnClearClick(unittest.TestCase):
    """Tests for the on_clear_click() callback."""

    def test_resets_state(self):
        """Clearing should reset user location, address, and pin."""
        main_mod.user_location["lat"] = 47.6
        main_mod.user_location["lon"] = -122.33
        main_mod.address_input.value = "some address"
        main_mod.on_clear_click()
        self.assertIsNone(main_mod.user_location["lat"])
        self.assertEqual(main_mod.address_input.value, "")
        self.assertEqual(main_mod.user_source.data["x"], [])


class TestOnAddressChange(unittest.TestCase):
    """Tests for the on_address_change() callback."""

    def test_clears_location(self):
        """Changing the address text should clear the stored user location."""
        main_mod.user_location["lat"] = 47.6
        main_mod.on_address_change("value", "old", "new")
        self.assertIsNone(main_mod.user_location["lat"])


class TestMarkerCallback(unittest.TestCase):
    """Tests for the marker_callback() tap handler."""

    def setUp(self):
        """Reset marker-related state."""
        main_mod.user_location["lat"] = None
        main_mod.user_location["lon"] = None
        main_mod.foodbank_source.selected.indices = []
        main_mod.search_widgets["results_div"].text = ""

    def test_empty_selection_clears(self):
        """Deselecting a marker should clear the results div."""
        main_mod.marker_callback("indices", [0], [])
        self.assertEqual(main_mod.search_widgets["results_div"].text, "")

    def test_tap_no_user_location(self):
        """No user location: route returns None, no error shown."""
        main_mod.marker_callback("indices", [], [0])
        self.assertEqual(main_mod.search_widgets["results_div"].text, "")

    @patch.object(main_mod.route_planner, "get_route_to_destination",
                  return_value=(None, None, None))
    def test_tap_no_route_with_user_location(self, _mock):
        """With user location but no route, show 'No transit route'."""
        main_mod.user_location["lat"] = 47.6
        main_mod.user_location["lon"] = -122.33
        main_mod.marker_callback("indices", [], [0])
        self.assertIn("No transit route",
                       main_mod.search_widgets["results_div"].text)

    @patch.object(main_mod.route_planner, "get_route_to_destination",
                  return_value=(15.0, ["USER", "s1", "b1"],
                                [{"type": "walk"}]))
    def test_tap_with_route(self, _mock):
        """Valid route should show estimated time in results."""
        main_mod.user_location["lat"] = 47.6
        main_mod.user_location["lon"] = -122.33
        main_mod.marker_callback("indices", [], [0])
        self.assertIn("15 min",
                       main_mod.search_widgets["results_div"].text)


if __name__ == "__main__":
    unittest.main()
