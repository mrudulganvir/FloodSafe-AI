"""
test_greedy.py
==============
Unit tests for the Greedy Best-First Search algorithm module.
"""

import math
import pytest
import networkx as nx

from app.services.graph_service import (
    load_raw_graph_data,
    build_networkx_graph,
    haversine_distance,
    get_node_coords,
)
from app.services.hazard_service import apply_hazards
from app.algorithms.greedy_best_first import greedy_best_first_search


@pytest.fixture
def clean_graph():
    """Returns a fresh Bengaluru sample graph with no hazards."""
    data = load_raw_graph_data()
    return build_networkx_graph(data)


class TestGreedyBestFirst:
    """Test suite for Greedy Best-First Search."""

    def test_greedy_finds_path_on_clean_graph(self, clean_graph):
        """Greedy search should successfully find a route from N1 to N12."""
        res = greedy_best_first_search(clean_graph, "N1", "N12")

        assert res.found is True
        assert res.algorithm == "greedy"
        assert res.path_node_ids[0] == "N1"
        assert res.path_node_ids[-1] == "N12"
        assert res.total_distance_m > 0
        assert res.nodes_explored > 0
        assert len(res.path_coords) == len(res.path_node_ids)
        assert res.time_ms >= 0.0

    def test_greedy_path_is_continuous(self, clean_graph):
        """Every consecutive node pair in the returned path must be an actual edge in the graph."""
        res = greedy_best_first_search(clean_graph, "N1", "N12")
        assert res.found is True

        for i in range(len(res.path_node_ids) - 1):
            u, v = res.path_node_ids[i], res.path_node_ids[i + 1]
            assert clean_graph.has_edge(u, v), f"Edge {u}-{v} does not exist in graph"

    def test_greedy_avoids_blocked_roads(self, clean_graph):
        """Greedy must never include a road marked as blocked in its returned path."""
        # Block Domlur underpass route N5-N8
        hazards = {"blocked": [["N5", "N8"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        res = greedy_best_first_search(G, "N1", "N12")
        assert res.found is True

        for i in range(len(res.path_node_ids) - 1):
            pair = {res.path_node_ids[i], res.path_node_ids[i + 1]}
            assert pair != {"N5", "N8"}, "Blocked edge N5-N8 found in Greedy path!"

    def test_greedy_start_equals_destination(self, clean_graph):
        """If start is destination, return immediately with 0 cost."""
        res = greedy_best_first_search(clean_graph, "N12", "N12")
        assert res.found is True
        assert res.path_node_ids == ["N12"]
        assert res.total_distance_m == 0.0
        assert res.total_cost == 0.0
        assert res.nodes_explored == 1

    def test_greedy_no_route_when_completely_blocked(self, clean_graph):
        """If destination is unreachable due to blockages, return found=False."""
        hazards = {"blocked": [["N11", "N12"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        res = greedy_best_first_search(G, "N1", "N12")
        assert res.found is False
        assert res.path_node_ids == []
        assert res.path_coords == []

    def test_greedy_invalid_nodes_raise_error(self, clean_graph):
        """Invalid node IDs should raise a ValueError."""
        with pytest.raises(ValueError, match="does not exist in the graph"):
            greedy_best_first_search(clean_graph, "MISSING_NODE", "N12")

    def test_greedy_expands_frontier_by_heuristic(self, clean_graph):
        """Verify that from N1, Greedy prefers N3 over N2 because N3 is geographically closer to N12."""
        dest_lat, dest_lon = get_node_coords(clean_graph, "N12")
        n2_lat, n2_lon = get_node_coords(clean_graph, "N2")
        n3_lat, n3_lon = get_node_coords(clean_graph, "N3")

        d_n2 = haversine_distance(n2_lat, n2_lon, dest_lat, dest_lon)
        d_n3 = haversine_distance(n3_lat, n3_lon, dest_lat, dest_lon)

        # Confirm N3 is closer to N12 as the crow flies
        assert d_n3 < d_n2

        res = greedy_best_first_search(clean_graph, "N1", "N12")
        assert res.found is True
        # Since N3 is closer to destination than N2, Greedy should take N3 as its second node
        assert res.path_node_ids[1] == "N3"
