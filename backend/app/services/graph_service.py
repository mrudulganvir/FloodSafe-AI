"""
graph_service.py
================
Responsible for:
  1. Loading the raw road network from sample_graph.json
  2. Converting it into a NetworkX Graph object
  3. Providing the Haversine distance function used as the heuristic h(n)
     in Greedy Best-First Search and A* Search
  4. Loading and retrieving named scenarios from scenarios.json

WHY NetworkX?
  NetworkX is Python's standard graph library. A NetworkX Graph stores:
    - Nodes as a dictionary:  G.nodes["N1"] → {"lat": ..., "lon": ..., ...}
    - Edges as a dictionary:  G["N1"]["N2"] → {"length_m": 1950, "status": "normal"}
  We do NOT use NetworkX's built-in shortest-path functions (like nx.shortest_path).
  We implement BFS, Greedy, and A* ourselves so we can learn and explain them.

WHY undirected Graph (not DiGraph)?
  All sample roads are bidirectional. An undirected Graph automatically lets
  you travel both ways on every edge. If we needed one-way streets, we would
  switch to nx.DiGraph.
"""

import json
import math
from pathlib import Path
import networkx as nx

# --------------------------------------------------------------------------
# File paths
# --------------------------------------------------------------------------
# Path(__file__) is the path to *this* file (graph_service.py).
# .parent goes up one folder (services/), .parent.parent goes to app/.
# Then we navigate into the data/ folder.
DATA_DIR = Path(__file__).parent.parent / "data"
GRAPH_FILE = DATA_DIR / "sample_graph.json"
SCENARIOS_FILE = DATA_DIR / "scenarios.json"


# --------------------------------------------------------------------------
# Raw data loading
# --------------------------------------------------------------------------

def load_raw_graph_data() -> dict:
    """
    Read sample_graph.json from disk and return the parsed dictionary.
    Called once when the scenario is first requested.
    """
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scenarios() -> list[dict]:
    """Read scenarios.json and return the list of scenario dictionaries."""
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_scenario(scenario_id: str) -> dict | None:
    """
    Find and return a single scenario by its ID string.
    Returns None if the ID does not exist (caller handles the error).
    """
    for scenario in load_scenarios():
        if scenario["id"] == scenario_id:
            return scenario
    return None


# --------------------------------------------------------------------------
# Graph construction
# --------------------------------------------------------------------------

def build_networkx_graph(graph_data: dict) -> nx.Graph:
    """
    Convert the raw JSON dictionary into a NetworkX Graph.

    After calling this function, you can use the graph like this:
        G.nodes["N1"]           → {"label": "Silk Board", "lat": 12.9177, ...}
        G["N1"]["N3"]           → {"length_m": 1950, "status": "normal"}
        list(G.neighbors("N1")) → ["N2", "N3"]   (all nodes directly connected)

    Each edge gets a default "status" of "normal".
    hazard_service.py will change this to "blocked" or "risky" later.
    """
    G = nx.Graph()

    # Add every node with all its attributes
    for node in graph_data["nodes"]:
        G.add_node(
            node["id"],
            label=node["label"],
            lat=node["lat"],
            lon=node["lon"],
            is_shelter=node["is_shelter"],
        )

    # Add every edge with length and a default normal status
    # All our sample roads are bidirectional, so nx.Graph handles both directions.
    for edge in graph_data["edges"]:
        G.add_edge(
            edge["from"],
            edge["to"],
            length_m=edge["length_m"],
            label=edge.get("label", ""),
            status="normal",     # hazard_service will update this field
        )

    return G


def get_graph_for_scenario(scenario_id: str) -> nx.Graph:
    """
    Convenience function: load the raw data and build the NetworkX graph.
    Returns the graph in its clean "no hazards applied" state.
    The caller (hazard_service) is responsible for applying hazards.
    """
    raw_data = load_raw_graph_data()
    return build_networkx_graph(raw_data)


# --------------------------------------------------------------------------
# Coordinate helpers
# --------------------------------------------------------------------------

def get_node_coords(G: nx.Graph, node_id: str) -> tuple[float, float]:
    """
    Return (lat, lon) tuple for a node.
    Used by algorithms when they need a node's geographic position.
    Raises KeyError if node_id is not in the graph.
    """
    node_data = G.nodes[node_id]
    return node_data["lat"], node_data["lon"]


def haversine_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle (straight-line) distance between two
    geographic coordinates using the Haversine formula.

    WHY we need this:
      Greedy Best-First Search and A* need to *estimate* the distance
      from any node to the destination without actually knowing the road.
      The straight-line distance is the best possible estimate — a road
      can never be shorter than a straight line — so this is an
      *admissible heuristic* for A*.

    ADMISSIBILITY (key viva concept):
      A heuristic h(n) is admissible if:
          h(n) ≤ true_remaining_cost(n)   for every node n
      The Haversine distance satisfies this because roads always zig-zag,
      making them longer than the straight line between two points.
      A* is guaranteed to find the optimal path only if h(n) is admissible.

    Args:
        lat1, lon1: coordinates of the start node
        lat2, lon2: coordinates of the destination node

    Returns:
        Straight-line distance in metres
    """
    R = 6_371_000  # Earth radius in metres

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(delta_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def validate_nodes(G: nx.Graph, *node_ids: str) -> None:
    """
    Check that all given node IDs exist in the graph.
    Raises ValueError with a clear message if any node is missing.
    This prevents cryptic KeyErrors deep inside algorithm code.
    """
    for node_id in node_ids:
        if node_id not in G:
            available = sorted(G.nodes())
            raise ValueError(
                f"Node '{node_id}' does not exist in the graph. "
                f"Available nodes: {available}"
            )
