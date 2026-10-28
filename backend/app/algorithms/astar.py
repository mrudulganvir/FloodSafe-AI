"""
astar.py
========
A* Search implementation for FloodSafe AI.

ALGORITHM CHARACTERISTICS:
  - Evaluation Function: f(n) = g(n) + h(n)
      * g(n): Exact accumulated risk-adjusted travel cost from start to node n.
      * h(n): Admissible heuristic estimate of remaining cost from node n to destination
              (straight-line Haversine distance in metres).
  - Optimality: Guaranteed to find the minimum-cost route because h(n) is admissible
    (straight-line distance never exceeds curved road length, and risk penalties are non-negative).
  - Flood Awareness:
      * Blocked roads have infinite cost and are skipped completely.
      * Risky roads add an extra penalty (500 m equivalent), encouraging A* to find
        safer routes even if slightly longer geographically.
"""

import heapq
import math
import time
import itertools
import networkx as nx

from app.services.graph_service import (
    validate_nodes,
    get_node_coords,
    haversine_distance,
)
from app.services.hazard_service import get_edge_cost
from app.algorithms.base import (
    RouteResult,
    reconstruct_path,
    compute_path_metrics,
    extract_path_coords,
)


def astar_search(G: nx.Graph, start: str, destination: str) -> RouteResult:
    """
    Execute A* search from start to destination on graph G.

    Cost model:
      edge_cost = physical_length + risk_penalty (or infinity if blocked)
    Heuristic:
      h(n) = haversine_distance(node_coords, dest_coords)

    Args:
        G: NetworkX Graph with hazards applied.
        start: Node ID of starting location.
        destination: Node ID of destination shelter.

    Returns:
        RouteResult containing path, distance, cost, nodes explored, time, and explanation.
    """
    validate_nodes(G, start, destination)
    start_time = time.perf_counter()

    # Special case: start is already destination
    if start == destination:
        coords = extract_path_coords(G, [start])
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return RouteResult(
            algorithm="astar",
            found=True,
            path_node_ids=[start],
            path_coords=coords,
            total_distance_m=0.0,
            total_risk_penalty=0.0,
            total_cost=0.0,
            nodes_explored=1,
            time_ms=elapsed_ms,
            explanation="Start and destination are identical. Zero movement required.",
        )

    dest_lat, dest_lon = get_node_coords(G, destination)

    def heuristic(node: str) -> float:
        lat, lon = get_node_coords(G, node)
        return haversine_distance(lat, lon, dest_lat, dest_lon)

    # g_score tracks the lowest known cost from start to each node
    g_score: dict[str, float] = {node: math.inf for node in G.nodes()}
    g_score[start] = 0.0

    tie_breaker = itertools.count()
    start_h = heuristic(start)
    # Priority queue stores tuples: (f_score, tie_breaker, node_id)
    frontier = [(start_h, next(tie_breaker), start)]

    parent_map: dict[str, str | None] = {start: None}
    visited: set[str] = set()
    nodes_explored = 0
    found = False

    while frontier:
        current_f, _, curr = heapq.heappop(frontier)

        if curr in visited:
            continue

        visited.add(curr)
        nodes_explored += 1

        if curr == destination:
            found = True
            break

        for neighbor in G.neighbors(curr):
            edge_cost = get_edge_cost(G, curr, neighbor)
            # Skip blocked edges with infinite cost
            if math.isinf(edge_cost):
                continue

            tentative_g = g_score[curr] + edge_cost

            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent_map[neighbor] = curr
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(frontier, (f_score, next(tie_breaker), neighbor))

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    if not found:
        return RouteResult(
            algorithm="astar",
            found=False,
            path_node_ids=[],
            path_coords=[],
            total_distance_m=0.0,
            total_risk_penalty=0.0,
            total_cost=0.0,
            nodes_explored=nodes_explored,
            time_ms=elapsed_ms,
            explanation=(
                f"A* could not find an accessible route from {start} to {destination}. "
                "All routes to the shelter are impassable due to blocked roads."
            ),
        )

    path = reconstruct_path(parent_map, destination)
    distance, risk_penalty, cost = compute_path_metrics(G, path)
    coords = extract_path_coords(G, path)

    explanation = (
        f"A* found the mathematically optimal route with total risk-adjusted cost of {round(cost, 1)}m "
        f"({round(distance, 1)}m physical distance + {round(risk_penalty, 1)}m hazard penalties). "
        "It balanced accumulated road costs g(n) with the straight-line heuristic h(n) to guarantee minimum cost."
    )

    return RouteResult(
        algorithm="astar",
        found=True,
        path_node_ids=path,
        path_coords=coords,
        total_distance_m=distance,
        total_risk_penalty=risk_penalty,
        total_cost=cost,
        nodes_explored=nodes_explored,
        time_ms=elapsed_ms,
        explanation=explanation,
    )
