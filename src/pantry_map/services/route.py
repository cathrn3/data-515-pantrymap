"""
This module handles finding the estimated optimal route between a user's location
and a food bank via public transportation
"""

import networkx as nx
import numpy as np
from sklearn.neighbors import BallTree
import logging


class calculateRoute:
    """
    Find the shortest path via public transportation between a user and a selected food bank
    using Dijkstra's algorithm.
    Food banks and public transit stops are reachable by the user if they are within 1 mile.
    The estimated in-vehicle time along a route is calculated from the schedule information
    in the transit dataset.
    The estimated walking time to a node is calculated using the distance and an assumed
    walking speed.
    The estimated time taken to make a bus transfer is taken from the transfer data
    (e.g., ``transfers_df['estimated_time']``) rather than being a fixed constant.
    """
    USER_ALLOWED_DIST = 1 # Allow 1 mile between user and nodes
    WALKING_SPEED = 2 # Assumed walking speed at 2 MPH

    def __init__(self, food_bank_df, transit_df, transfers_df):
        self.user_location = None
        self.food_bank_df = food_bank_df
        self.transit_df = transit_df
        self.transfers_df = transfers_df
        self.graph = self._initialize_graph()

        self.transit_coords = np.radians(self.transit_df[['stop_lat','stop_lon']].dropna())
        self.transit_tree = BallTree(self.transit_coords, metric='haversine')

        self.food_bank_coords = np.radians(self.food_bank_df[['Latitude','Longitude']].dropna())
        self.food_bank_tree = BallTree(self.food_bank_coords, metric='haversine')

    def _initialize_graph(self):
        """
        Connect bus stops within each route and connect all available transfers between routes
        """
        graph = nx.DiGraph() # Bus routes are directional
        df_edges = self.transit_df[self.transit_df["next_stop"].notna()]
        edge_list = list(zip(df_edges["unique_key"], df_edges["next_stop"], df_edges["estimated_travel_time_minutes_between_stops"]))
        graph.add_weighted_edges_from(edge_list)
        transfer_list = list(zip(self.transfers_df["source_node"], self.transfers_df["nearby_node"], self.transfers_df["estimated_time"]))
        graph.add_weighted_edges_from(transfer_list)
        return graph

    def set_user_location(self, user_location: tuple | None):
        self.user_location = user_location # lat, lon coordinates
        if user_location is not None:
            self._add_user_location_to_graph()
    
    def get_user_location(self):
        return self.user_location

    def _get_nearby_nodes(self, tree, source_coords: tuple, radius: int):
        """Get nodes in the tree within the given radius to the source coordinates"""
        lat, lon = source_coords
        coords = [[np.radians(lat), np.radians(lon)]]
        allowed_radius = radius / 3959

        indices, dist = tree.query_radius(coords, r=allowed_radius, return_distance=True)
        return indices[0], dist[0] * 3959

    def _remove_old_user_location_from_graph(self):
        """Remove old address on updates"""
        if "USER" in self.graph:
            self.graph.remove_node("USER")

    def _add_user_location_to_graph(self):
        """
        Modifies the graph to include the user as a node.
        Users are connected to any nodes within a mile.
        """
        self._remove_old_user_location_from_graph()
        transit_idx, transit_dist = self._get_nearby_nodes(self.transit_tree, self.user_location, self.USER_ALLOWED_DIST)
        food_bank_idx, food_bank_dist = self._get_nearby_nodes(self.food_bank_tree, self.user_location, self.USER_ALLOWED_DIST)

        for df_index, dist in zip(transit_idx, transit_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60
            self.graph.add_edge("USER", self.transit_df['unique_key'].iloc[df_index], weight=estimated_time)
            self.graph.add_edge(self.transit_df['unique_key'].iloc[df_index], "USER", weight=estimated_time)

        for df_index, dist in zip(food_bank_idx, food_bank_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60 # in minutes
            self.graph.add_edge("USER", self.food_bank_df['bank_id'].iloc[df_index], weight=estimated_time)
            self.graph.add_edge(self.food_bank_df['bank_id'].iloc[df_index], "USER", weight=estimated_time)

    def _get_nearby_nodes_to_food_bank(self, food_bank_id: str):
        """Temporarily connect the given food bank to the graph, returning a new copy of the graph"""
        food_bank = self.food_bank_df[self.food_bank_df['bank_id'] == food_bank_id]
        coords = tuple(food_bank[['Latitude', 'Longitude']].iloc[0])
        transit_idx, transit_dist = self._get_nearby_nodes(self.transit_tree, coords, self.USER_ALLOWED_DIST)

        new_graph = self.graph.copy() # Safely copies graph for adding temp edges
        for df_index, dist in zip(transit_idx, transit_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60
            stop_id = self.transit_df['unique_key'].iloc[df_index]
            new_graph.add_edge(food_bank_id, stop_id, weight=estimated_time)
            new_graph.add_edge(stop_id, food_bank_id, weight=estimated_time)
        return new_graph

    def get_route_to_destination(self, food_bank_id: str):
        """Return the shortest path between the user and the given food bank. Return estimated time as well."""
        try:
            if self.user_location is None:
                return None, None
            new_graph = self._get_nearby_nodes_to_food_bank(food_bank_id)
            time, route = nx.single_source_dijkstra(new_graph, 'USER', food_bank_id, weight='weight')
            return time, route
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None, None
        except Exception:
            logging.exception(
                "Unexpected error occurred while finding route to food bank %s",
                food_bank_id,
            )
            return None, None
