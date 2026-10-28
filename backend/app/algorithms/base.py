"""
base.py
=======
Common data structures and helper utilities for all search algorithms.
"""

from dataclasses import dataclass, field
import time
import networkx as nx

from app.services.graph_service import get_node_coords
from app.services.hazard_service import get_edge_cost, get_edge_risk_penalty


@dataclass
class RouteResult:
    """
    Standardized return object for all routing algorithms in FloodSafe AI.
    """
    algorithm: str
    found: bool
    path_node_ids: list[str] = field(default_factory=list)
    path_coords: list[tuple[float, float]] = field(default_factory=list)
    total_distance_m: float = 0.0
    total_risk_penalty: float = 0.0
    total_cost: float = 0.0
    nodes_explored: int = 0
    time_ms: float = 0.0
    explanation: str = ""

    def to_dict(self) -> dict:
        """Convert result to a dictionary suitable for API JSON responses."""
        return {
            "algorithm": self.algorithm,
            "found": self.found,
            "path_node_ids": self.path_node_ids,
            "path_coords": self.path_coords,
            "total_distance_m": round(self.total_distance_m, 2),
            "total_risk_penalty": round(self.total_risk_penalty, 2),
            "total_cost": round(self.total_cost, 2),
            "nodes_explored": self.nodes_explored,
            "time_ms": round(self.time_ms, 3),
            "explanation": self.explanation,
        }


def reconstruct_path(parent_map: dict[str, str | None], destination: str) -> list[str]:
    """
    Reconstruct node path from destination back to start using parent pointers.
    """
    path = []
    curr: str | None = destination
    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)
    path.reverse()
    return path


def compute_path_metrics(G: nx.Graph, path: list[str]) -> tuple[float, float, float]:
    """
    Given a valid path in G, compute:
      - total_distance_m: physical road distance
      - total_risk_penalty: accumulated risk penalties
      - total_cost: distance + risk penalties
    """
    if len(path) <= 1:
        return 0.0, 0.0, 0.0

    total_distance = 0.0
    total_risk_penalty = 0.0
    total_cost = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_data = G[u][v]
        length = float(edge_data.get("length_m", 0.0))
        penalty = float(get_edge_risk_penalty(G, u, v))
        cost = float(get_edge_cost(G, u, v))

        total_distance += length
        total_risk_penalty += penalty
        total_cost += cost

    return total_distance, total_risk_penalty, total_cost


def extract_path_coords(G: nx.Graph, path: list[str]) -> list[tuple[float, float]]:
    """Extract (lat, lon) coordinates for every node in the path."""
    return [get_node_coords(G, node_id) for node_id in path]
