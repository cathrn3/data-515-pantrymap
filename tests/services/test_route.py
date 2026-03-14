import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
import networkx as nx

from src.pantry_map.services.route import calculateRoute


class TestCalculateRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Mock data is setup like so:

        foodbank1                    foodbank2                   foodbank3            foodbank4
        route1 <------------------>
                                               route2 --------------->
                                               <------------------- route3
                                               <------------------- route4  # Slow route
        """
        # Food banks and their locations
        cls.food_bank_df = pd.DataFrame({
            "bank_id": ["foodbank1", "foodbank2", "foodbank3", "foodbank4"],
            "Latitude": [47.60, 47.71, 47.81, 48.10],
            "Longitude": [-122.33, -122.33, -122.33, -122.33]
        })
        # Transit routes with stops information
        cls.transit_df = pd.DataFrame({
            "unique_key": [
                "route1stop1", "route1stop2", "route1stop3",
                "route2stop1", "route2stop2",
                "route3stop1", "route3stop2",
                "route4stop1", "route4stop2"
            ],
            "route_id": [
                "route1", "route1", "route1",
                "route2", "route2",
                "route3", "route3",
                "route4", "route4"
            ],
            "next_stop": [
                "route1stop2", "route1stop3", np.nan,
                "route2stop2", np.nan,
                "route3stop2", np.nan,
                "route4stop2", np.nan
            ],
            "estimated_travel_time_minutes_between_stops": [1, 2, 3, 1, 2, 1, 2, 5, 5],
            "stop_lat": [47.60, 47.70, 47.60, 47.71, 47.80, 47.80, 47.71, 47.80, 47.71],
            "stop_lon": [-122.33, -122.33, -122.33, -122.33, -122.33, -122.33, -122.33, -122.33, -122.33]
        })
        # Available bus transfers
        cls.transfers_df = pd.DataFrame({
            "source_node": ["route1stop2", "route1stop2", "route1stop2"],
            "nearby_node": ["route2stop1", "route3stop2", "route4stop2"],
            "estimated_time": [30, 30, 30]
        })

    def setUp(self):
        self.routeCalculater = calculateRoute(self.food_bank_df, self.transit_df, self.transfers_df)

    def test_graph(self):
        """Ensure graph is correctly initialized"""
        graph = self.routeCalculater.graph

        expected_edges = {
            ("route1stop1", "route1stop2"),
            ("route1stop2", "route1stop3"),
            ("route2stop1", "route2stop2"),
            ("route3stop1", "route3stop2"),
            ("route4stop1", "route4stop2"),
            ("route1stop2", "route2stop1"),
            ("route1stop2", "route3stop2"),
            ("route1stop2", "route4stop2"),
        }
        self.assertTrue(set(graph.edges()), expected_edges)
        self.assertEqual(graph["route4stop1"]["route4stop2"]["weight"], 5)
        self.assertEqual(graph["route1stop2"]["route2stop1"]["weight"], 30)

    def test_set_user_location(self):
        """Test user location gets connected to the graph"""
        self.routeCalculater.set_user_location((47.59, -122.33))

        graph = self.routeCalculater.graph
        self.assertTrue(graph.has_edge("USER", "route1stop1"))
        self.assertTrue(graph.has_edge("USER", "foodbank1"))
        self.assertEqual(self.routeCalculater.get_user_location(), (47.59, -122.33))

    def test_reset_user_location(self):
        """Test previous user location gets reset upon new location"""
        self.routeCalculater.set_user_location((47.59, -122.33))
        self.routeCalculater.set_user_location((47.81, -122.33))

        graph = self.routeCalculater.graph
        self.assertFalse(graph.has_edge("USER", "route1stop1"))

        expected_user_edges = {
            ("USER", "foodbank3"),
            ("USER", "route2stop2"),
            ("USER", "route3stop1"),
            ("USER", "route4stop1")
        }
        self.assertTrue(expected_user_edges <= set(graph.edges()))

    def test_empty_user_location(self):
        """Should return no route if user location is not set"""
        self.routeCalculater.set_user_location(None)
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank1")
        self.assertIsNone(est_time)
        self.assertIsNone(route)

    def test_direct_walking(self):
        self.routeCalculater.set_user_location((47.59, -122.33))
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank1")
        self.assertAlmostEqual(est_time, 20, delta=1)
        self.assertEqual(route, ["USER", "foodbank1"])

    def test_transit_route(self):
        self.routeCalculater.set_user_location((47.59, -122.33))
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank2")
        self.assertAlmostEqual(est_time, 42, delta=1)
        self.assertEqual(route, ["USER", "route1stop1", "route1stop2", "foodbank2"])

    def test_transit_route_with_transfer(self):
        self.routeCalculater.set_user_location((47.59, -122.33))
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank3")
        self.assertAlmostEqual(est_time, 73, delta=1)
        self.assertEqual(route, ["USER", "route1stop1", "route1stop2", "route2stop1", "route2stop2", "foodbank3"])

    def test_directional_route(self):
        """Ensure route takes directionality into account and takes the optimal route"""
        self.routeCalculater.set_user_location((47.71, -122.33))
        _, route = self.routeCalculater.get_route_to_destination("foodbank3")
        self.assertEqual(route, ["USER", "route2stop1", "route2stop2", "foodbank3"])

        self.routeCalculater.set_user_location((47.81, -122.33))
        _, route = self.routeCalculater.get_route_to_destination("foodbank2")
        self.assertEqual(route, ["USER", "route3stop1", "route3stop2", "foodbank2"])

    def test_no_route_user_too_far(self):
        """Returns None if no route is found"""
        self.routeCalculater.set_user_location((40.00, -122.33))
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank1")
        self.assertIsNone(est_time)
        self.assertIsNone(route)

    def test_no_transit_route(self):
        self.routeCalculater.set_user_location((47.59, -122.33))
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank4")
        self.assertIsNone(est_time)
        self.assertIsNone(route)

    @patch("networkx.single_source_dijkstra")
    def test_no_route_on_exception(self, mock_dijkstra):
        """Gracefully returns None on unexpected exceptions"""
        mock_dijkstra.side_effect = Exception()
        self.routeCalculater.set_user_location((47.59, -122.33))
        est_time, route = self.routeCalculater.get_route_to_destination("foodbank1")
        self.assertIsNone(est_time)
        self.assertIsNone(route)
