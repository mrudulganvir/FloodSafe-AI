"""
test_graph.py
=============
Smoke tests for the graph data layer (Milestone 2).

These tests verify:
  - The JSON data loads correctly
  - The NetworkX graph has the expected nodes and edges
  - Hazards are applied correctly
  - The cost model (get_edge_cost) works as expected
  - Edge cases (invalid nodes) raise proper errors

Run with:
    cd backend
    pytest tests/test_graph.py -v
"""

import math
import pytest
import networkx as nx

from app.services.graph_service import (
    load_raw_graph_data,
    build_networkx_graph,
    get_graph_for_scenario,
    get_node_coords,
    haversine_distance,
    validate_nodes,
    get_scenario,
    load_scenarios,
)
from app.services.hazard_service import (
    apply_hazards,
    get_edge_cost,
    get_edge_risk_penalty,
    build_hazard_graph,
    RISK_PENALTY_M,
)


# ===========================================================================
# FIXTURES
# A pytest fixture is a reusable setup step. The @pytest.fixture decorator
# tells pytest to run this function before each test that requests it.
# ===========================================================================

@pytest.fixture
def raw_data():
    """Load sample_graph.json once and share it across tests."""
    return load_raw_graph_data()


@pytest.fixture
def base_graph(raw_data):
    """A clean NetworkX graph with no hazards applied."""
    return build_networkx_graph(raw_data)


# ===========================================================================
# Graph structure tests
# ===========================================================================

class TestGraphStructure:
    """Verify the sample graph has the expected nodes and edges."""

    def test_graph_loads_without_error(self, raw_data):
        """The JSON file must parse correctly."""
        assert raw_data is not None
        assert "nodes" in raw_data
        assert "edges" in raw_data

    def test_correct_node_count(self, base_graph):
        """Our Bengaluru sample has exactly 12 nodes."""
        assert base_graph.number_of_nodes() == 12

    def test_correct_edge_count(self, base_graph):
        """Our Bengaluru sample has exactly 18 edges."""
        assert base_graph.number_of_edges() == 18

    def test_all_expected_nodes_present(self, base_graph):
        """Every node from N1 to N12 must be in the graph."""
        for i in range(1, 13):
            assert f"N{i}" in base_graph, f"Node N{i} is missing from the graph"

    def test_node_has_coordinates(self, base_graph):
        """Every node must have lat and lon attributes."""
        for node_id, data in base_graph.nodes(data=True):
            assert "lat" in data, f"{node_id} missing 'lat'"
            assert "lon" in data, f"{node_id} missing 'lon'"
            # Coordinates must be in a valid range for Bengaluru
            assert 12.8 < data["lat"] < 13.2, f"{node_id} lat out of Bengaluru range"
            assert 77.4 < data["lon"] < 77.8, f"{node_id} lon out of Bengaluru range"

    def test_shelter_node_is_n12(self, base_graph):
        """N12 (Vidhana Soudha) must be marked as a shelter."""
        assert base_graph.nodes["N12"]["is_shelter"] is True

    def test_start_node_is_not_shelter(self, base_graph):
        """N1 (Silk Board) should not be a shelter."""
        assert base_graph.nodes["N1"]["is_shelter"] is False

    def test_edges_have_length(self, base_graph):
        """Every edge must have a positive length_m attribute."""
        for u, v, data in base_graph.edges(data=True):
            assert "length_m" in data, f"Edge {u}-{v} missing length_m"
            assert data["length_m"] > 0, f"Edge {u}-{v} has non-positive length"

    def test_all_edges_default_to_normal_status(self, base_graph):
        """Before hazards are applied, every edge must be 'normal'."""
        for u, v, data in base_graph.edges(data=True):
            assert data.get("status") == "normal", (
                f"Edge {u}-{v} has unexpected status '{data.get('status')}' "
                f"before hazards are applied"
            )

    def test_graph_is_connected(self, base_graph):
        """All nodes must be reachable from any other node (no isolated nodes)."""
        assert nx.is_connected(base_graph), (
            "The graph is not fully connected — some nodes are unreachable"
        )

    def test_specific_edge_n1_n3_exists(self, base_graph):
        """Spot-check: the Silk Board to Koramangala road must exist."""
        assert base_graph.has_edge("N1", "N3")
        assert base_graph["N1"]["N3"]["length_m"] == 1951  # updated to ceil(haversine)

    def test_specific_edge_n11_n12_exists(self, base_graph):
        """Spot-check: the final road to the shelter must exist."""
        assert base_graph.has_edge("N11", "N12")
        assert base_graph["N11"]["N12"]["length_m"] == 460


# ===========================================================================
# Hazard model tests
# ===========================================================================

class TestHazardModel:
    """Verify that apply_hazards and get_edge_cost work correctly."""

    def test_blocked_edge_has_inf_cost(self, base_graph):
        """A blocked edge must return infinity as its cost."""
        hazards = {"blocked": [["N5", "N8"]], "risky": []}
        G = apply_hazards(base_graph, hazards)
        cost = get_edge_cost(G, "N5", "N8")
        assert math.isinf(cost), "Blocked edge should have infinite cost"

    def test_risky_edge_has_penalty_added(self, base_graph):
        """A risky edge cost = length_m + RISK_PENALTY_M."""
        hazards = {"blocked": [], "risky": [["N3", "N5"]]}
        G = apply_hazards(base_graph, hazards)
        expected = base_graph["N3"]["N5"]["length_m"] + RISK_PENALTY_M
        assert get_edge_cost(G, "N3", "N5") == expected

    def test_normal_edge_cost_equals_length(self, base_graph):
        """A normal edge cost must equal its physical length only."""
        cost = get_edge_cost(base_graph, "N1", "N3")
        assert cost == base_graph["N1"]["N3"]["length_m"]

    def test_original_graph_unmodified_after_hazard(self, base_graph):
        """
        CRITICAL: Applying hazards must NOT modify the original graph.
        If this fails, algorithms would see each other's side-effects.
        """
        hazards = {"blocked": [["N1", "N3"]], "risky": []}
        _ = apply_hazards(base_graph, hazards)  # apply to a copy
        # Original must still be normal
        assert base_graph["N1"]["N3"]["status"] == "normal"

    def test_blocked_overrides_risky(self, base_graph):
        """
        If an edge is blocked, marking it as risky should not downgrade it.
        blocked takes precedence over risky.
        """
        hazards = {
            "blocked": [["N5", "N8"]],
            "risky":   [["N5", "N8"]],  # same edge — must stay blocked
        }
        G = apply_hazards(base_graph, hazards)
        assert G["N5"]["N8"]["status"] == "blocked"

    def test_risk_penalty_value(self, base_graph):
        """The RISK_PENALTY_M constant must be 500 (as documented)."""
        assert RISK_PENALTY_M == 500.0

    def test_risky_edge_penalty_isolated(self, base_graph):
        """get_edge_risk_penalty returns RISK_PENALTY_M for risky, 0 for normal."""
        hazards = {"blocked": [], "risky": [["N3", "N5"]]}
        G = apply_hazards(base_graph, hazards)
        assert get_edge_risk_penalty(G, "N3", "N5") == RISK_PENALTY_M
        assert get_edge_risk_penalty(G, "N1", "N3") == 0.0

    def test_empty_hazards_leaves_graph_unchanged(self, base_graph):
        """Applying empty hazards must produce a graph identical to the input."""
        G = apply_hazards(base_graph, {"blocked": [], "risky": []})
        for u, v, data in G.edges(data=True):
            assert data["status"] == "normal"


# ===========================================================================
# Coordinate and heuristic tests
# ===========================================================================

class TestCoordinatesAndHeuristic:
    """Verify the Haversine heuristic is admissible and correct."""

    def test_get_node_coords_returns_lat_lon(self, base_graph):
        """get_node_coords must return a (lat, lon) tuple."""
        lat, lon = get_node_coords(base_graph, "N1")
        assert lat == pytest.approx(12.9177, abs=0.001)
        assert lon == pytest.approx(77.6233, abs=0.001)

    def test_haversine_same_point_is_zero(self):
        """Distance from a point to itself must be 0."""
        d = haversine_distance(12.9177, 77.6233, 12.9177, 77.6233)
        assert d == pytest.approx(0.0, abs=0.01)

    def test_haversine_symmetry(self):
        """Distance A→B must equal distance B→A."""
        d1 = haversine_distance(12.9177, 77.6233, 12.9797, 77.5905)
        d2 = haversine_distance(12.9797, 77.5905, 12.9177, 77.6233)
        assert d1 == pytest.approx(d2, rel=1e-6)

    def test_haversine_admissibility_on_every_edge(self, base_graph):
        """
        ADMISSIBILITY TEST: For every edge in the graph, the straight-line
        distance (heuristic) must be <= the actual road length.

        This is the formal proof that h(n) never overestimates — a
        requirement for A* to be optimal.
        """
        for u, v, data in base_graph.edges(data=True):
            lat_u, lon_u = get_node_coords(base_graph, u)
            lat_v, lon_v = get_node_coords(base_graph, v)
            straight_line = haversine_distance(lat_u, lon_u, lat_v, lon_v)
            road_length = data["length_m"]
            assert straight_line <= road_length, (
                f"Admissibility violated on edge {u}-{v}: "
                f"straight-line {straight_line:.0f}m > road {road_length}m"
            )


# ===========================================================================
# Scenario loading tests
# ===========================================================================

class TestScenarios:
    """Verify named scenarios load and apply correctly."""

    def test_three_scenarios_exist(self):
        """There must be exactly 3 scenarios in scenarios.json."""
        scenarios = load_scenarios()
        assert len(scenarios) == 3

    def test_scenario_ids_are_correct(self):
        """All three expected scenario IDs must exist."""
        scenarios = load_scenarios()
        ids = [s["id"] for s in scenarios]
        assert "sample_1" in ids
        assert "sample_2" in ids
        assert "sample_3" in ids

    def test_get_scenario_returns_correct_one(self):
        """get_scenario('sample_2') must return the bridge-blocked scenario."""
        s = get_scenario("sample_2")
        assert s is not None
        assert s["name"] == "Domlur Underpass Flooded"

    def test_get_scenario_returns_none_for_unknown_id(self):
        """Requesting a non-existent scenario ID must return None."""
        s = get_scenario("this_does_not_exist")
        assert s is None

    def test_sample_1_has_no_hazards(self):
        """Scenario 1 (Clear Roads) must have empty hazard lists."""
        s = get_scenario("sample_1")
        assert s["hazards"]["blocked"] == []
        assert s["hazards"]["risky"] == []

    def test_sample_2_blocks_n5_n8(self):
        """Scenario 2 must block the N5-N8 edge."""
        s = get_scenario("sample_2")
        blocked = s["hazards"]["blocked"]
        assert ["N5", "N8"] in blocked

    def test_build_hazard_graph_applies_scenario_2(self, base_graph):
        """
        build_hazard_graph for scenario 2 must return a graph where
        N5-N8 is blocked.
        """
        G = build_hazard_graph("sample_2")
        assert G["N5"]["N8"]["status"] == "blocked"

    def test_build_hazard_graph_invalid_scenario_raises(self):
        """Requesting a non-existent scenario must raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            build_hazard_graph("nonexistent_scenario_xyz")


# ===========================================================================
# validate_nodes tests
# ===========================================================================

class TestValidateNodes:
    """Edge-case handling for invalid node IDs."""

    def test_valid_nodes_do_not_raise(self, base_graph):
        """Valid node IDs must not raise any error."""
        validate_nodes(base_graph, "N1", "N12")  # should not raise

    def test_invalid_node_raises_value_error(self, base_graph):
        """An invalid node ID must raise ValueError with a helpful message."""
        with pytest.raises(ValueError, match="N99"):
            validate_nodes(base_graph, "N1", "N99")

    def test_error_message_includes_available_nodes(self, base_graph):
        """The error message must list the available node IDs."""
        with pytest.raises(ValueError, match="N1"):  # N1 should be in the list
            validate_nodes(base_graph, "INVALID")
