import networkx as nx
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from networkx.algorithms.simple_paths import shortest_simple_paths


class calculateRoute:
    USER_ALLOWED_DIST = 1 # Allow 1 mile between user and nodes
    WALKING_SPEED = 2 # MPH

    def __init__(self, food_bank_df, transit_df, transfers_df):
        self.food_bank_df = food_bank_df
        self.transit_df = transit_df
        self.transfers_df = transfers_df
        self.graph = self._initialize_graph()

        self.transit_coords = np.radians(self.transit_df[['stop_lat','stop_lon']].dropna())
        self.transit_tree = BallTree(self.transit_coords, metric='haversine')

        self.food_bank_coords = np.radians(self.food_bank_df[['Latitude','Longitude']].dropna())
        self.food_bank_tree = BallTree(self.food_bank_coords, metric='haversine')

    def _initialize_graph(self):
        graph = nx.Graph()
        edge_list = list(zip(self.transit_df["unique_key"], self.transit_df["next_stop"], self.transit_df["estimated_travel_time_minutes_between_stops"]))
        graph.add_weighted_edges_from(edge_list)
        transfer_list = list(zip(self.transfers_df["source_node"], self.transfers_df["nearby_node"], self.transfers_df["estimated_time"]))
        graph.add_weighted_edges_from(transfer_list)
        return graph

    def set_user_location(self, user_location: tuple):
        self.user_location = user_location # lat, lon coordinates. Assumed to be valid and in Seattle
        self._add_user_location_to_graph()

    def _get_nearby_nodes(self, tree, source_coords, radius):
        lat, lon = source_coords
        coords = [[np.radians(lat), np.radians(lon)]]
        allowed_radius = radius / 3959

        indices, dist = tree.query_radius(coords, r=allowed_radius, return_distance=True)
        return indices[0], dist[0] * 3959

    def _remove_old_user_location_from_graph(self):
        # Remove old address on updates
        if "USER" in self.graph:
            self.graph.remove_node("USER")

    def _add_user_location_to_graph(self):
        self._remove_old_user_location_from_graph()
        transit_idx, transit_dist = self._get_nearby_nodes(self.transit_tree, self.user_location, self.USER_ALLOWED_DIST)
        food_bank_idx, food_bank_dist = self._get_nearby_nodes(self.food_bank_tree, self.user_location, self.USER_ALLOWED_DIST)

        for df_index, dist in zip(transit_idx, transit_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60
            self.graph.add_edge("USER", self.transit_df['unique_key'].iloc[df_index], weight=estimated_time)

        for df_index, dist in zip(food_bank_idx, food_bank_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60 # in minutes
            self.graph.add_edge("USER", self.food_bank_df['bank_id'].iloc[df_index], weight=estimated_time)

    def _get_nearby_nodes_to_food_bank(self, food_bank_id):
        food_bank = self.food_bank_df[self.food_bank_df['bank_id'] == food_bank_id]
        coords = tuple(food_bank[['Latitude', 'Longitude']].iloc[0])
        transit_idx, transit_dist = self._get_nearby_nodes(self.transit_tree, coords, self.USER_ALLOWED_DIST)

        temp_edges = []
        for df_index, dist in zip(transit_idx, transit_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60
            stop_id = self.transit_df['unique_key'].iloc[df_index]
            self.graph.add_edge(food_bank_id, stop_id, weight=estimated_time)
            temp_edges.append((food_bank_id, stop_id))
        return temp_edges


    def get_route_to_destination(self, food_bank_id):
        try:
            temp_edges = self._get_nearby_nodes_to_food_bank(food_bank_id)
            time, route = nx.single_source_dijkstra(self.graph, 'USER', food_bank_id, weight='weight')
            self.graph.remove_edges_from(temp_edges) # For next food bank id
            return time, route # Return shortest path
        except Exception as e:
            return None, None


# Test directions -- make sure not finding non existent backwards routes
# Test directions -- make sure transfers and walking is bidirectional
# Test still works on user address updates (test state)
# Test still works on new food bank (test state)