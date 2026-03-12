import unittest
import pandas as pd
from pantry_map.utilities.utility import find_nearest_foodbanks

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