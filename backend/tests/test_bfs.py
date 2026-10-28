"""
test_bfs.py
===========
Unit tests for the Breadth-First Search (BFS) algorithm module.
"""

import math
import pytest
import networkx as nx

from app.services.graph_service import (
    load_raw_graph_data,
    build_networkx_graph,
)
from app.services.hazard_service import apply_hazards
from app.algorithms.bfs import bfs_search


@pytest.fixture
def clean_graph():
    """Returns a fresh Bengaluru sample graph with no hazards."""
    data = load_raw_graph_data()
    return build_networkx_graph(data)


class TestBFS:
    """Test suite for BFS pathfinding."""

    def test_bfs_finds_path_on_clean_graph(self, clean_graph):
        """BFS should successfully find a route from Silk Board (N1) to Vidhana Soudha (N12)."""
        res = bfs_search(clean_graph, "N1", "N12")

        assert res.found is True
        assert res.algorithm == "bfs"
        assert res.path_node_ids[0] == "N1"
        assert res.path_node_ids[-1] == "N12"
        assert res.total_distance_m > 0
        assert res.nodes_explored > 0
        assert len(res.path_coords) == len(res.path_node_ids)
        assert res.time_ms >= 0.0

    def test_bfs_minimizes_hop_count(self, clean_graph):
        """BFS must produce the minimal hop count path."""
        res = bfs_search(clean_graph, "N1", "N12")
        bfs_hops = len(res.path_node_ids) - 1

        # Use unweighted NetworkX shortest path as ground truth for minimum hop count
        nx_shortest_hop_length = nx.shortest_path_length(clean_graph, "N1", "N12")
        assert bfs_hops == nx_shortest_hop_length

    def test_bfs_avoids_blocked_roads(self, clean_graph):
        """BFS must never include a road marked as blocked in its returned path."""
        # Block direct path edges N5-N8 and N6-N8
        hazards = {"blocked": [["N5", "N8"], ["N6", "N8"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        res = bfs_search(G, "N1", "N12")
        assert res.found is True

        # Ensure blocked edges are not consecutive nodes in path
        for i in range(len(res.path_node_ids) - 1):
            pair = {res.path_node_ids[i], res.path_node_ids[i + 1]}
            assert pair != {"N5", "N8"}, "Blocked edge N5-N8 found in BFS path!"
            assert pair != {"N6", "N8"}, "Blocked edge N6-N8 found in BFS path!"

    def test_bfs_start_equals_destination(self, clean_graph):
        """If start is destination, return immediately with 0 cost and single node."""
        res = bfs_search(clean_graph, "N1", "N1")
        assert res.found is True
        assert res.path_node_ids == ["N1"]
        assert res.total_distance_m == 0.0
        assert res.total_cost == 0.0
        assert res.total_risk_penalty == 0.0
        assert res.nodes_explored == 1

    def test_bfs_no_route_when_completely_blocked(self, clean_graph):
        """If destination is completely surrounded by blocked roads, report not found."""
        # Block the only incoming road to N12: N11-N12
        hazards = {"blocked": [["N11", "N12"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        res = bfs_search(G, "N1", "N12")
        assert res.found is False
        assert res.path_node_ids == []
        assert res.path_coords == []
        assert "could not find any accessible route" in res.explanation

    def test_bfs_invalid_nodes_raise_error(self, clean_graph):
        """Invalid node IDs should raise a ValueError with helpful message."""
        with pytest.raises(ValueError, match="does not exist in the graph"):
            bfs_search(clean_graph, "INVALID_START", "N12")

        with pytest.raises(ValueError, match="does not exist in the graph"):
            bfs_search(clean_graph, "N1", "INVALID_DEST")

    def test_bfs_ignores_risk_penalty_when_finding_hops(self, clean_graph):
        """
        BFS should traverse a risky road if that road provides the minimum hop count,
        accumulating the risk penalty into total_cost without changing its hop choice.
        """
        # Mark N1-N3 as risky
        hazards = {"blocked": [], "risky": [["N1", "N3"]]}
        G = apply_hazards(clean_graph, hazards)

        res = bfs_search(G, "N1", "N3")
        assert res.found is True
        assert res.path_node_ids == ["N1", "N3"]
        assert res.total_risk_penalty == 500.0
        assert res.total_cost == res.total_distance_m + 500.0
