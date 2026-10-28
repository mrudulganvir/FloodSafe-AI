"""
test_astar.py
=============
Unit tests for the A* Search algorithm module.
"""

import math
import pytest
import networkx as nx

from app.services.graph_service import (
    load_raw_graph_data,
    build_networkx_graph,
)
from app.services.hazard_service import apply_hazards, get_edge_cost
from app.algorithms.astar import astar_search


@pytest.fixture
def clean_graph():
    """Returns a fresh Bengaluru sample graph with no hazards."""
    data = load_raw_graph_data()
    return build_networkx_graph(data)


def compute_nx_shortest_cost(G: nx.Graph, start: str, dest: str) -> float:
    """Helper using NetworkX dijkstra_path to compute optimal cost as ground truth."""
    # Build a weighted graph with actual traversal costs
    G_weighted = nx.Graph()
    for u, v in G.edges():
        c = get_edge_cost(G, u, v)
        if not math.isinf(c):
            G_weighted.add_edge(u, v, weight=c)

    return nx.shortest_path_length(G_weighted, start, dest, weight="weight")


class TestAStar:
    """Test suite for A* search."""

    def test_astar_finds_path_on_clean_graph(self, clean_graph):
        """A* should successfully find a route from N1 to N12."""
        res = astar_search(clean_graph, "N1", "N12")

        assert res.found is True
        assert res.algorithm == "astar"
        assert res.path_node_ids[0] == "N1"
        assert res.path_node_ids[-1] == "N12"
        assert res.total_distance_m > 0
        assert res.nodes_explored > 0
        assert len(res.path_coords) == len(res.path_node_ids)
        assert res.time_ms >= 0.0

    def test_astar_is_cost_optimal_on_clean_graph(self, clean_graph):
        """A* must find a route whose total cost equals Dijkstra optimal cost."""
        res = astar_search(clean_graph, "N1", "N12")
        expected_optimal_cost = compute_nx_shortest_cost(clean_graph, "N1", "N12")

        assert pytest.approx(res.total_cost, rel=1e-4) == expected_optimal_cost

    def test_astar_avoids_blocked_roads(self, clean_graph):
        """A* must never traverse a road that is blocked."""
        hazards = {"blocked": [["N5", "N8"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        res = astar_search(G, "N1", "N12")
        assert res.found is True

        for i in range(len(res.path_node_ids) - 1):
            pair = {res.path_node_ids[i], res.path_node_ids[i + 1]}
            assert pair != {"N5", "N8"}, "Blocked edge N5-N8 found in A* path!"

    def test_astar_reroutes_around_risky_road(self, clean_graph):
        """
        Adding risk penalties to edges on the default optimal route
        should cause A* to choose an alternative safer route.
        """
        # Baseline optimal route
        base_res = astar_search(clean_graph, "N1", "N12")
        original_path = list(base_res.path_node_ids)

        # Mark all edges on original path as risky (except final N11-N12)
        risky_pairs = []
        for i in range(len(original_path) - 2):
            risky_pairs.append([original_path[i], original_path[i + 1]])

        hazards = {"blocked": [], "risky": risky_pairs}
        G = apply_hazards(clean_graph, hazards)

        rerouted_res = astar_search(G, "N1", "N12")
        assert rerouted_res.found is True
        # Path should have changed to avoid excessive penalties where possible
        assert rerouted_res.path_node_ids != original_path

    def test_astar_start_equals_destination(self, clean_graph):
        """If start is destination, return immediately with 0 cost."""
        res = astar_search(clean_graph, "N5", "N5")
        assert res.found is True
        assert res.path_node_ids == ["N5"]
        assert res.total_distance_m == 0.0
        assert res.total_cost == 0.0
        assert res.nodes_explored == 1

    def test_astar_no_route_when_completely_blocked(self, clean_graph):
        """If destination is unreachable due to blockages, return found=False."""
        hazards = {"blocked": [["N11", "N12"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        res = astar_search(G, "N1", "N12")
        assert res.found is False
        assert res.path_node_ids == []
        assert res.path_coords == []

    def test_astar_invalid_nodes_raise_error(self, clean_graph):
        """Invalid node IDs should raise a ValueError."""
        with pytest.raises(ValueError, match="does not exist in the graph"):
            astar_search(clean_graph, "UNKNOWN_NODE", "N12")
