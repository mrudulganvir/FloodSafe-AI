"""
test_comparison.py
==================
Cross-algorithm comparison tests for FloodSafe AI.

Tests:
  1. All algorithms run on identical graph states without mutating the graph.
  2. Cost optimality guarantee: Cost(A*) <= Cost(BFS) and Cost(A*) <= Cost(Greedy).
  3. Hop optimality guarantee: Hops(BFS) <= Hops(A*) and Hops(BFS) <= Hops(Greedy).
  4. Blocked road avoidance: No algorithm traverses a blocked road.
  5. Scenario comparison:
     - Scenario 1 (Clear): Compare metrics across all three.
     - Scenario 2 (Underpass flooded): All reroute around N5-N8.
     - Scenario 3 (Risky roads): A* penalizes risky paths, BFS focuses on hops.
  6. Output consistency: All algorithms return identical RouteResult structure.
"""

import pytest
import networkx as nx

from app.services.graph_service import (
    load_raw_graph_data,
    build_networkx_graph,
    get_scenario,
)
from app.services.hazard_service import build_hazard_graph, apply_hazards
from app.algorithms.bfs import bfs_search
from app.algorithms.greedy_best_first import greedy_best_first_search
from app.algorithms.astar import astar_search
from app.algorithms.base import RouteResult


@pytest.fixture
def clean_graph():
    """Returns a fresh Bengaluru sample graph with no hazards."""
    data = load_raw_graph_data()
    return build_networkx_graph(data)


class TestCrossAlgorithmComparison:
    """Test suite comparing BFS, Greedy Best-First, and A*."""

    def test_schema_consistency_across_all_algorithms(self, clean_graph):
        """All three algorithms must return a RouteResult with identical field types."""
        algorithms = [bfs_search, greedy_best_first_search, astar_search]

        for algo_fn in algorithms:
            res: RouteResult = algo_fn(clean_graph, "N1", "N12")
            assert isinstance(res, RouteResult)
            assert isinstance(res.algorithm, str)
            assert isinstance(res.found, bool)
            assert isinstance(res.path_node_ids, list)
            assert isinstance(res.path_coords, list)
            assert isinstance(res.total_distance_m, float)
            assert isinstance(res.total_risk_penalty, float)
            assert isinstance(res.total_cost, float)
            assert isinstance(res.nodes_explored, int)
            assert isinstance(res.time_ms, float)
            assert isinstance(res.explanation, str)
            assert len(res.path_coords) == len(res.path_node_ids)

            # Test dictionary conversion for API compatibility
            d = res.to_dict()
            assert isinstance(d, dict)
            assert d["algorithm"] == res.algorithm
            assert "total_cost" in d

    def test_astar_cost_optimality_vs_bfs_and_greedy(self, clean_graph):
        """
        On any graph with non-negative costs and admissible heuristic:
        Cost(A*) <= Cost(BFS) and Cost(A*) <= Cost(Greedy).
        """
        bfs_res = bfs_search(clean_graph, "N1", "N12")
        greedy_res = greedy_best_first_search(clean_graph, "N1", "N12")
        astar_res = astar_search(clean_graph, "N1", "N12")

        assert astar_res.found and bfs_res.found and greedy_res.found

        # A* total cost must be less than or equal to both
        assert astar_res.total_cost <= bfs_res.total_cost + 1e-4
        assert astar_res.total_cost <= greedy_res.total_cost + 1e-4

    def test_bfs_hop_optimality_vs_greedy_and_astar(self, clean_graph):
        """
        BFS is guaranteed to find the minimum number of edges (hops):
        Hops(BFS) <= Hops(Greedy) and Hops(BFS) <= Hops(A*).
        """
        bfs_res = bfs_search(clean_graph, "N1", "N12")
        greedy_res = greedy_best_first_search(clean_graph, "N1", "N12")
        astar_res = astar_search(clean_graph, "N1", "N12")

        bfs_hops = len(bfs_res.path_node_ids) - 1
        greedy_hops = len(greedy_res.path_node_ids) - 1
        astar_hops = len(astar_res.path_node_ids) - 1

        assert bfs_hops <= greedy_hops
        assert bfs_hops <= astar_hops

    def test_all_algorithms_avoid_blocked_roads_scenario_2(self):
        """In scenario 2 (Domlur underpass N5-N8 blocked), all three algorithms must reroute."""
        G = build_hazard_graph("sample_2")

        results = [
            bfs_search(G, "N1", "N12"),
            greedy_best_first_search(G, "N1", "N12"),
            astar_search(G, "N1", "N12"),
        ]

        for res in results:
            assert res.found is True
            for i in range(len(res.path_node_ids) - 1):
                pair = {res.path_node_ids[i], res.path_node_ids[i + 1]}
                assert pair != {"N5", "N8"}, (
                    f"Algorithm {res.algorithm} traversed blocked edge N5-N8!"
                )

    def test_scenario_3_risk_penalty_impact(self):
        """
        In scenario 3 (N6-N7 blocked, N3-N5 & N5-N6 risky):
        - All three algorithms avoid the blocked road.
        - A* finds a cost-optimal route under the risk penalties.
        """
        G = build_hazard_graph("sample_3")

        bfs_res = bfs_search(G, "N1", "N12")
        greedy_res = greedy_best_first_search(G, "N1", "N12")
        astar_res = astar_search(G, "N1", "N12")

        for res in [bfs_res, greedy_res, astar_res]:
            assert res.found is True
            # Check blocked road N6-N7
            for i in range(len(res.path_node_ids) - 1):
                pair = {res.path_node_ids[i], res.path_node_ids[i + 1]}
                assert pair != {"N6", "N7"}

        # A* must remain cost-optimal
        assert astar_res.total_cost <= bfs_res.total_cost + 1e-4
        assert astar_res.total_cost <= greedy_res.total_cost + 1e-4

    def test_algorithms_do_not_mutate_graph(self, clean_graph):
        """
        Running BFS, Greedy, and A* in sequence on the same graph instance
        must not change the graph's nodes or edges.
        """
        original_nodes = list(clean_graph.nodes(data=True))
        original_edges = list(clean_graph.edges(data=True))

        _ = bfs_search(clean_graph, "N1", "N12")
        _ = greedy_best_first_search(clean_graph, "N1", "N12")
        _ = astar_search(clean_graph, "N1", "N12")

        assert list(clean_graph.nodes(data=True)) == original_nodes
        assert list(clean_graph.edges(data=True)) == original_edges

    def test_all_algorithms_report_no_route_when_islanded(self, clean_graph):
        """When the destination shelter (N12) is completely cut off, all algorithms report found=False."""
        hazards = {"blocked": [["N11", "N12"]], "risky": []}
        G = apply_hazards(clean_graph, hazards)

        bfs_res = bfs_search(G, "N1", "N12")
        greedy_res = greedy_best_first_search(G, "N1", "N12")
        astar_res = astar_search(G, "N1", "N12")

        assert bfs_res.found is False
        assert greedy_res.found is False
        assert astar_res.found is False

        assert bfs_res.path_node_ids == []
        assert greedy_res.path_node_ids == []
        assert astar_res.path_node_ids == []
