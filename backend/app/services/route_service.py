"""
route_service.py
================
Orchestration service for pathfinding and algorithm comparison in FloodSafe AI.
Coordinates graph construction, hazard overlay, algorithm execution, and metric formatting.
"""

from typing import Optional, Callable
import networkx as nx

from app.services.graph_service import (
    validate_nodes,
    get_scenario,
)
from app.services.hazard_service import (
    build_hazard_graph,
    get_hazard_summary,
)
from app.algorithms.bfs import bfs_search
from app.algorithms.greedy_best_first import greedy_best_first_search
from app.algorithms.astar import astar_search
from app.algorithms.base import RouteResult
from app.models.schemas import (
    HazardInput,
    RouteCompareResponse,
    RouteResultSchema,
)

# Canonical mapping of supported algorithm identifiers
ALGORITHM_MAP: dict[str, Callable[[nx.Graph, str, str], RouteResult]] = {
    "bfs": bfs_search,
    "greedy": greedy_best_first_search,
    "greedy_best_first": greedy_best_first_search,
    "astar": astar_search,
    "a_star": astar_search,
    "a*": astar_search,
}


def normalize_algorithm_name(name: str) -> str:
    """Normalize algorithm query names to lowercase stripped strings."""
    return name.strip().lower()


def compare_routes(
    scenario_id: str,
    start_node: str,
    destination_node: str,
    hazards: Optional[HazardInput | dict] = None,
    algorithms: Optional[list[str]] = None,
) -> RouteCompareResponse:
    """
    Run selected search algorithms on the specified scenario graph and return comparisons.

    Args:
        scenario_id: Identifier of the base scenario.
        start_node: Source node ID.
        destination_node: Destination node ID.
        hazards: Optional custom hazard overlays.
        algorithms: List of algorithm names to run (default: ['bfs', 'greedy', 'astar']).

    Returns:
        RouteCompareResponse with results for each algorithm and hazard counts.

    Raises:
        ValueError: If scenario, node, or algorithm identifier is invalid.
    """
    # 1. Verify scenario existence
    if get_scenario(scenario_id) is None:
        raise ValueError(f"Scenario '{scenario_id}' not found.")

    # 2. Convert Pydantic model to dict if needed
    hazards_dict: Optional[dict] = None
    if hazards is not None:
        if isinstance(hazards, HazardInput):
            hazards_dict = hazards.model_dump()
        elif isinstance(hazards, dict):
            hazards_dict = hazards

    # 3. Build graph with scenario & extra hazards
    G = build_hazard_graph(scenario_id, extra_hazards=hazards_dict)

    # 4. Validate start and destination nodes exist in G
    validate_nodes(G, start_node, destination_node)

    # 5. Determine which algorithms to execute
    if not algorithms:
        algos_to_run = ["bfs", "greedy", "astar"]
    else:
        algos_to_run = algorithms

    results: list[RouteResultSchema] = []

    for algo_name in algos_to_run:
        key = normalize_algorithm_name(algo_name)
        if key not in ALGORITHM_MAP:
            valid_keys = sorted(set(["bfs", "greedy", "astar"]))
            raise ValueError(
                f"Unsupported algorithm '{algo_name}'. Supported algorithms are: {valid_keys}"
            )

        algo_func = ALGORITHM_MAP[key]
        route_res: RouteResult = algo_func(G, start_node, destination_node)

        # Standardize result schema
        results.append(
            RouteResultSchema(
                algorithm=route_res.algorithm,
                found=route_res.found,
                path_node_ids=route_res.path_node_ids,
                path_coords=route_res.path_coords,
                total_distance_m=round(route_res.total_distance_m, 2),
                total_risk_penalty=round(route_res.total_risk_penalty, 2),
                total_cost=round(route_res.total_cost, 2),
                nodes_explored=route_res.nodes_explored,
                time_ms=round(route_res.time_ms, 3),
                explanation=route_res.explanation,
            )
        )

    hazard_summary = get_hazard_summary(G)

    return RouteCompareResponse(
        scenario_id=scenario_id,
        start_node=start_node,
        destination_node=destination_node,
        results=results,
        hazard_summary=hazard_summary,
    )
