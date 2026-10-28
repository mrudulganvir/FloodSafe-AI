"""
hazard_service.py
=================
Responsible for applying flood hazards to a road graph.

Two types of hazards:
  1. BLOCKED  — edge cannot be traversed at all (infinite cost)
  2. RISKY    — edge can be traversed but incurs an extra penalty cost

IMPORTANT DESIGN DECISION:
  We always work on a COPY of the graph. This means:
    - The original graph loaded from JSON is never modified.
    - Each algorithm call gets a clean, consistent hazard configuration.
    - We can run all three algorithms on the exact same hazard state.

COST MODEL (transparent and documented):
  traversal_cost(edge) =
      math.inf                     if status == "blocked"
      length_m + RISK_PENALTY_M    if status == "risky"
      length_m                     otherwise (normal)

  RISK_PENALTY_M = 500 metres
  This is a simulation constant. It means: "This algorithm would rather
  travel an extra 500 m than use a risky road of equal length."
  It has NO real-world safety meaning and is NOT a flood probability.
"""

import math
import networkx as nx
from app.services.graph_service import (
    get_graph_for_scenario,
    load_raw_graph_data,
    build_networkx_graph,
)

# --------------------------------------------------------------------------
# Simulation constant
# --------------------------------------------------------------------------
RISK_PENALTY_M: float = 500.0   # metres equivalent penalty for a risky edge


# --------------------------------------------------------------------------
# Core hazard application
# --------------------------------------------------------------------------

def apply_hazards(G: nx.Graph, hazards: dict) -> nx.Graph:
    """
    Apply blocked and risky hazards to a COPY of the graph.

    Args:
        G       : a NetworkX Graph (the clean base graph)
        hazards : dict with two keys:
                    "blocked" → list of [node_a, node_b] pairs
                    "risky"   → list of [node_a, node_b] pairs

    Returns:
        A new Graph (copy) with updated "status" attributes on edges.
        The original G is untouched.

    Example input:
        hazards = {
            "blocked": [["N5", "N8"]],
            "risky":   [["N3", "N5"], ["N5", "N6"]]
        }
    """
    G_with_hazards = G.copy()   # ← COPY, never mutate the original

    # Apply blocked edges first
    for pair in hazards.get("blocked", []):
        u, v = pair[0], pair[1]
        if G_with_hazards.has_edge(u, v):
            G_with_hazards[u][v]["status"] = "blocked"
        # If the edge doesn't exist we silently skip — not an error.
        # (User might have removed an edge that wasn't in the graph.)

    # Apply risky edges — but never downgrade a blocked edge to risky
    for pair in hazards.get("risky", []):
        u, v = pair[0], pair[1]
        if G_with_hazards.has_edge(u, v):
            if G_with_hazards[u][v]["status"] != "blocked":
                G_with_hazards[u][v]["status"] = "risky"

    return G_with_hazards


def get_edge_cost(G: nx.Graph, u: str, v: str) -> float:
    """
    Compute the traversal cost for a single edge (u → v).

    This is the function algorithms call each time they expand a neighbour.
    The cost model is:
        blocked → math.inf   (impossible to traverse)
        risky   → length_m + RISK_PENALTY_M
        normal  → length_m

    Args:
        G : the graph WITH hazards already applied
        u : source node ID
        v : target node ID

    Returns:
        float — the cost to traverse this edge
    """
    edge_data = G[u][v]
    status = edge_data.get("status", "normal")
    length = edge_data["length_m"]

    if status == "blocked":
        return math.inf
    elif status == "risky":
        return length + RISK_PENALTY_M
    else:
        return length


def get_edge_risk_penalty(G: nx.Graph, u: str, v: str) -> float:
    """
    Return only the risk portion of an edge's cost (0 if not risky).
    Used to compute 'total_risk_penalty' in the algorithm result.
    """
    status = G[u][v].get("status", "normal")
    return RISK_PENALTY_M if status == "risky" else 0.0


# --------------------------------------------------------------------------
# Convenience builder used by the route service
# --------------------------------------------------------------------------

def build_hazard_graph(scenario_id: str, extra_hazards: dict | None = None) -> nx.Graph:
    """
    Full pipeline: load graph → apply scenario hazards → apply extra hazards.

    The route service calls this once per /routes/compare request.
    All three algorithms then receive the same graph object.

    Args:
        scenario_id   : which scenario to load (e.g. "sample_2")
        extra_hazards : additional user-supplied hazards from the API request
                        (can be None or {"blocked": [], "risky": []})

    Returns:
        A NetworkX Graph ready for pathfinding.

    Raises:
        ValueError: if scenario_id is not found
    """
    from app.services.graph_service import get_scenario  # avoid circular import at top

    # Load the base graph from JSON
    raw_data = load_raw_graph_data()
    G = build_networkx_graph(raw_data)

    # Get the scenario's built-in hazards
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(
            f"Scenario '{scenario_id}' not found. "
            f"Check scenarios.json for valid IDs."
        )

    # Layer 1: apply the scenario's default hazards
    G = apply_hazards(G, scenario["hazards"])

    # Layer 2: apply any extra hazards the user sent in the request
    if extra_hazards:
        G = apply_hazards(G, extra_hazards)

    return G


def get_hazard_summary(G: nx.Graph) -> dict:
    """
    Return a count summary of edge statuses in the graph.
    Useful for debugging and for the API response.

    Returns:
        {"normal": int, "risky": int, "blocked": int}
    """
    counts = {"normal": 0, "risky": 0, "blocked": 0}
    for u, v, data in G.edges(data=True):
        status = data.get("status", "normal")
        counts[status] = counts.get(status, 0) + 1
    return counts
