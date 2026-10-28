"""
test_api.py
===========
Integration and endpoint unit tests for the FloodSafe AI FastAPI backend (Milestone 4).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ===========================================================================
# Health & Root Endpoints
# ===========================================================================

def test_health_endpoint():
    """GET /api/health should return status 200 and 'ok'."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_endpoint():
    """GET / should return status 200 with information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "FloodSafe AI" in data["message"]
    assert "docs" in data


# ===========================================================================
# Scenario Endpoints
# ===========================================================================

def test_list_scenarios():
    """GET /api/scenarios should return all 3 predefined scenarios."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    ids = [item["id"] for item in data]
    assert "sample_1" in ids
    assert "sample_2" in ids
    assert "sample_3" in ids

    for item in data:
        assert "id" in item
        assert "name" in item
        assert "description" in item
        assert "default_start" in item
        assert "default_destination" in item


def test_get_scenario_detail_success():
    """GET /api/scenarios/{id} should return full scenario details and graph data."""
    response = client.get("/api/scenarios/sample_2")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "sample_2"
    assert data["name"] == "Domlur Underpass Flooded"
    assert "hazards" in data
    assert ["N5", "N8"] in data["hazards"]["blocked"]

    # Graph structure verification
    assert "graph" in data
    graph = data["graph"]
    assert graph["graph_id"] == "bengaluru_sample"
    assert len(graph["nodes"]) == 12
    assert len(graph["edges"]) == 18


def test_get_scenario_detail_not_found():
    """GET /api/scenarios/{unknown_id} should return 404."""
    response = client.get("/api/scenarios/non_existent_scenario_123")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


# ===========================================================================
# Route Comparison Endpoints
# ===========================================================================

def test_compare_routes_default_algorithms():
    """POST /api/routes/compare should execute BFS, Greedy, and A* by default."""
    payload = {
        "scenario_id": "sample_1",
        "start_node": "N1",
        "destination_node": "N12",
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["scenario_id"] == "sample_1"
    assert data["start_node"] == "N1"
    assert data["destination_node"] == "N12"
    assert len(data["results"]) == 3

    algo_names = [res["algorithm"] for res in data["results"]]
    assert "bfs" in algo_names
    assert "greedy" in algo_names
    assert "astar" in algo_names

    # All should have found valid paths
    for res in data["results"]:
        assert res["found"] is True
        assert res["path_node_ids"][0] == "N1"
        assert res["path_node_ids"][-1] == "N12"
        assert res["total_distance_m"] > 0
        assert res["nodes_explored"] > 0
        assert len(res["path_coords"]) == len(res["path_node_ids"])
        assert res["time_ms"] >= 0


def test_compare_routes_with_custom_hazards():
    """POST /api/routes/compare should respect user-provided hazard overrides."""
    payload = {
        "scenario_id": "sample_1",
        "start_node": "N1",
        "destination_node": "N12",
        "hazards": {
            "blocked": [["N5", "N8"]],
            "risky": [["N3", "N5"]],
        },
        "algorithms": ["astar"],
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) == 1
    astar_res = data["results"][0]
    assert astar_res["found"] is True

    # Blocked road N5-N8 must not be in path
    for i in range(len(astar_res["path_node_ids"]) - 1):
        pair = {astar_res["path_node_ids"][i], astar_res["path_node_ids"][i + 1]}
        assert pair != {"N5", "N8"}

    # Check hazard summary count
    assert data["hazard_summary"]["blocked"] == 1
    assert data["hazard_summary"]["risky"] == 1


def test_compare_routes_start_equals_destination():
    """POST /api/routes/compare with identical start and dest should return zero distance."""
    payload = {
        "scenario_id": "sample_1",
        "start_node": "N12",
        "destination_node": "N12",
        "algorithms": ["bfs", "astar"],
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    for res in data["results"]:
        assert res["found"] is True
        assert res["path_node_ids"] == ["N12"]
        assert res["total_distance_m"] == 0.0
        assert res["total_cost"] == 0.0


def test_compare_routes_no_valid_path():
    """POST /api/routes/compare when shelter is cut off should return found=False."""
    payload = {
        "scenario_id": "sample_1",
        "start_node": "N1",
        "destination_node": "N12",
        "hazards": {
            "blocked": [["N11", "N12"]],
            "risky": [],
        },
        "algorithms": ["astar"],
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    res = data["results"][0]
    assert res["found"] is False
    assert res["path_node_ids"] == []
    assert res["path_coords"] == []
    assert "could not find" in res["explanation"].lower()


# ===========================================================================
# Error Handling & Validation Tests
# ===========================================================================

def test_compare_routes_invalid_scenario():
    """POST /api/routes/compare with nonexistent scenario_id should return 404."""
    payload = {
        "scenario_id": "unknown_scenario_xyz",
        "start_node": "N1",
        "destination_node": "N12",
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_compare_routes_invalid_node():
    """POST /api/routes/compare with nonexistent node should return 400."""
    payload = {
        "scenario_id": "sample_1",
        "start_node": "NONEXISTENT_NODE",
        "destination_node": "N12",
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 400
    assert "does not exist in the graph" in response.json()["detail"]


def test_compare_routes_invalid_algorithm():
    """POST /api/routes/compare with invalid algorithm name should return 400."""
    payload = {
        "scenario_id": "sample_1",
        "start_node": "N1",
        "destination_node": "N12",
        "algorithms": ["quantum_search"],
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 400
    assert "unsupported algorithm" in response.json()["detail"].lower()


def test_compare_routes_malformed_request():
    """POST /api/routes/compare with missing required fields should return 422."""
    payload = {
        # missing scenario_id, start_node, destination_node
        "algorithms": ["astar"]
    }
    response = client.post("/api/routes/compare", json=payload)
    assert response.status_code == 422
