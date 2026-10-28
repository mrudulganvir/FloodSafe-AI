"""
greedy_best_first.py
====================
Greedy Best-First Search implementation for FloodSafe AI.

ALGORITHM CHARACTERISTICS:
  - Strategy: Informed search prioritizing nodes closest to the destination
    according to heuristic h(n) = straight-line Haversine distance.
  - Priority: f(n) = h(n).
  - Optimality: NOT guaranteed to find the shortest or lowest-cost path. It is
    greedy and susceptible to misleading dead-ends or long detours.
  - Flood Awareness: Refuses to traverse roads with status == 'blocked' (infinite cost).
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


def greedy_best_first_search(G: nx.Graph, start: str, destination: str) -> RouteResult:
    """
    Execute Greedy Best-First Search from start to destination on graph G.

    Priority key is purely h(n), the straight-line distance to the destination.
    Accumulated path cost g(n) is ignored during frontier expansion.

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
            algorithm="greedy",
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

    # Priority queue stores tuples: (h_score, tie_breaker, node_id)
    tie_breaker = itertools.count()
    start_h = heuristic(start)
    frontier = [(start_h, next(tie_breaker), start)]

    parent_map: dict[str, str | None] = {start: None}
    visited: set[str] = set()
    nodes_explored = 0
    found = False

    while frontier:
        h_val, _, curr = heapq.heappop(frontier)

        if curr in visited:
            continue

        visited.add(curr)
        nodes_explored += 1

        if curr == destination:
            found = True
            break

        for neighbor in G.neighbors(curr):
            # Check hazard status: blocked roads have infinite cost
            if math.isinf(get_edge_cost(G, curr, neighbor)):
                continue

            if neighbor not in visited:
                if neighbor not in parent_map:
                    parent_map[neighbor] = curr
                h_neighbor = heuristic(neighbor)
                heapq.heappush(frontier, (h_neighbor, next(tie_breaker), neighbor))

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    if not found:
        return RouteResult(
            algorithm="greedy",
            found=False,
            path_node_ids=[],
            path_coords=[],
            total_distance_m=0.0,
            total_risk_penalty=0.0,
            total_cost=0.0,
            nodes_explored=nodes_explored,
            time_ms=elapsed_ms,
            explanation=(
                f"Greedy Best-First Search could not find an open route from {start} to {destination}. "
                "Traversable paths towards the destination are blocked by hazards."
            ),
        )

    path = reconstruct_path(parent_map, destination)
    distance, risk_penalty, cost = compute_path_metrics(G, path)
    coords = extract_path_coords(G, path)

    explanation = (
        "Greedy Best-First Search selected nodes that geographically appeared closest to the shelter (lowest Haversine distance). "
        "It reached the goal rapidly by following the heuristic, but because it ignored accumulated road lengths and risk penalties, "
        "its route may not be the globally lowest-cost path."
    )

    return RouteResult(
        algorithm="greedy",
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
