"""
bfs.py
======
Breadth-First Search (BFS) implementation for FloodSafe AI.

ALGORITHM CHARACTERISTICS:
  - Strategy: Unweighted search exploring level-by-level (FIFO queue).
  - Optimality: Guarantees the minimum number of hops (edges traversed).
  - Limitation: Ignores physical edge lengths and risk penalties. A path of 2
    long roads will be preferred over 3 short roads, even if the latter is
    shorter or safer.
  - Flood Awareness: Refuses to traverse roads with status == 'blocked' (infinite cost).
"""

from collections import deque
import math
import time
import networkx as nx

from app.services.graph_service import validate_nodes
from app.services.hazard_service import get_edge_cost
from app.algorithms.base import (
    RouteResult,
    reconstruct_path,
    compute_path_metrics,
    extract_path_coords,
)


def bfs_search(G: nx.Graph, start: str, destination: str) -> RouteResult:
    """
    Execute Breadth-First Search from start to destination on graph G.

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
            algorithm="bfs",
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

    queue = deque([start])
    visited = {start}
    parent_map: dict[str, str | None] = {start: None}
    nodes_explored = 0
    found = False

    while queue:
        curr = queue.popleft()
        nodes_explored += 1

        if curr == destination:
            found = True
            break

        for neighbor in G.neighbors(curr):
            # Check hazard status: blocked roads have infinite cost
            if math.isinf(get_edge_cost(G, curr, neighbor)):
                continue

            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = curr
                queue.append(neighbor)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    if not found:
        return RouteResult(
            algorithm="bfs",
            found=False,
            path_node_ids=[],
            path_coords=[],
            total_distance_m=0.0,
            total_risk_penalty=0.0,
            total_cost=0.0,
            nodes_explored=nodes_explored,
            time_ms=elapsed_ms,
            explanation=(
                f"BFS could not find any accessible route from {start} to {destination}. "
                "All possible paths are severed by road blockages."
            ),
        )

    path = reconstruct_path(parent_map, destination)
    distance, risk_penalty, cost = compute_path_metrics(G, path)
    coords = extract_path_coords(G, path)

    hop_count = len(path) - 1
    explanation = (
        f"BFS found a route with the minimum number of road segments ({hop_count} hops). "
        "BFS treats all unblocked roads equally and does not consider physical distance or risk penalties."
    )

    return RouteResult(
        algorithm="bfs",
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
