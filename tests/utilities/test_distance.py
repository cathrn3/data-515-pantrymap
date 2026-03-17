"""Unit tests for distance calculations."""
import unittest
import pandas as pd
from pantry_map.utilities.utility import (
    find_nearest_foodbanks, color_from_id, lat_lon_to_mercator, calculate_distance,
)

class TestNearestFoodbanks(unittest.TestCase):
    """Unit tests for calculating distances and finding nearest food banks."""

    def setUp(self):
        """Create a tiny mock foodbank DataFrame for testing."""
        self.foodbanks = pd.DataFrame({
            'Name': ['A', 'B', 'C'],
            'Latitude': [0, 0, 1],
            'Longitude': [0, 1, 0]
        })

    def test_returns_k_results(self):
        """Should return exactly k results if enough food banks exist."""
        nearest = find_nearest_foodbanks(self.foodbanks, 0, 0, k=2)
        self.assertEqual(len(nearest), 2)

    def test_sorted_by_distance(self):
        """Returned food banks should be sorted closest first."""
        nearest = find_nearest_foodbanks(self.foodbanks, 0, 0, k=3)
        distances = nearest['distance'].values
        self.assertTrue(all(distances[i] <= distances[i+1] for i in range(len(distances)-1)))

    def test_k_larger_than_foodbanks(self):
        """If k > number of food banks, return all food banks."""
        nearest = find_nearest_foodbanks(self.foodbanks, 0, 0, k=10)
        self.assertEqual(len(nearest), len(self.foodbanks))

    def test_missing_coordinates(self):
        """Should skip food banks with missing latitude or longitude."""
        df_with_nans = pd.DataFrame({
            'Name': ['Valid', 'NoLat', 'NoLon', 'NoBoth'],
            'Latitude': [0, None, 0, None],
            'Longitude': [0, 0, None, None]
        })
        nearest = find_nearest_foodbanks(df_with_nans, 0, 0, k=5)
        self.assertEqual(len(nearest), 1)
        self.assertEqual(nearest.iloc[0]['Name'], 'Valid')


class TestUtilityFunctions(unittest.TestCase):
    """Tests for color_from_id, lat_lon_to_mercator, and calculate_distance."""

    def test_color_from_id(self):
        """Deterministic hex color; different IDs differ; int/str same."""
        c1 = color_from_id("route_42")
        self.assertTrue(c1.startswith("#") and len(c1) == 7)
        self.assertEqual(c1, color_from_id("route_42"))  # deterministic
        self.assertNotEqual(c1, color_from_id("route_99"))
        self.assertEqual(color_from_id(123), color_from_id("123"))

    def test_lat_lon_to_mercator(self):
        """Origin maps to (0, 0); Seattle coords give reasonable Mercator values."""
        x, y = lat_lon_to_mercator(0, 0)
        self.assertAlmostEqual(x, 0, places=1)
        self.assertAlmostEqual(y, 0, places=1)
        sx, sy = lat_lon_to_mercator(47.6, -122.33)
        self.assertTrue(-14_000_000 < sx < -13_000_000)
        self.assertTrue(5_000_000 < sy < 7_000_000)

    def test_calculate_distance(self):
        """Same point is 0; known pair gives expected miles."""
        self.assertEqual(calculate_distance(47.6, -122.3, 47.6, -122.3), 0)
        dist = calculate_distance(47.6, -122.3, 47.7, -122.3)
        self.assertTrue(6 < dist < 8)  # ~6.9 miles
