"""
schemas.py
==========
Pydantic data models for API request and response serialization and validation.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Hazard Models
# --------------------------------------------------------------------------

class HazardInput(BaseModel):
    """
    Representation of simulated flood hazards.
    Contains pairs of node IDs indicating road segments that are blocked or risky.
    Example:
        blocked: [["N5", "N8"]]
        risky: [["N3", "N5"], ["N5", "N6"]]
    """
    blocked: list[list[str]] = Field(
        default_factory=list,
        description="List of [node_a, node_b] pairs that are impassable.",
    )
    risky: list[list[str]] = Field(
        default_factory=list,
        description="List of [node_a, node_b] pairs that carry a risk penalty.",
    )


# --------------------------------------------------------------------------
# Graph & Scenario Models
# --------------------------------------------------------------------------

class NodeSchema(BaseModel):
    """Intersections or points of interest on the road network."""
    id: str
    label: str
    lat: float
    lon: float
    is_shelter: bool = False
    note: Optional[str] = ""


class EdgeSchema(BaseModel):
    """Road segments connecting nodes."""
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    length_m: float
    bidirectional: bool = True
    label: Optional[str] = ""


class GraphSchema(BaseModel):
    """Full road network graph definition."""
    graph_id: str
    name: str
    description: str
    risk_penalty_m: float = 500.0
    notes: Optional[str] = ""
    nodes: list[NodeSchema]
    edges: list[EdgeSchema]


class ScenarioSummarySchema(BaseModel):
    """Summary of a scenario for listing."""
    id: str
    name: str
    description: str
    default_start: str
    default_destination: str
    teaching_note: Optional[str] = ""


class ScenarioDetailSchema(BaseModel):
    """Detailed scenario representation including its hazard overlay and graph data."""
    id: str
    name: str
    description: str
    default_start: str
    default_destination: str
    hazards: HazardInput
    teaching_note: Optional[str] = ""
    graph: GraphSchema


# --------------------------------------------------------------------------
# Route Comparison Models
# --------------------------------------------------------------------------

class RouteCompareRequest(BaseModel):
    """
    Request payload for comparing route-planning algorithms under simulated flood conditions.
    """
    scenario_id: str = Field(
        ...,
        description="Identifier of the scenario to load (e.g., 'sample_1', 'sample_2', 'sample_3').",
    )
    start_node: str = Field(
        ...,
        description="Source node ID from which evacuation begins.",
    )
    destination_node: str = Field(
        ...,
        description="Target node ID (typically an evacuation shelter).",
    )
    hazards: Optional[HazardInput] = Field(
        default=None,
        description="Optional additional simulated hazards to overlay on top of the scenario.",
    )
    algorithms: list[str] = Field(
        default_factory=lambda: ["bfs", "greedy", "astar"],
        description="List of algorithms to execute (supports 'bfs', 'greedy', 'astar').",
    )


class RouteResultSchema(BaseModel):
    """Outcome and execution metrics of an individual search algorithm."""
    algorithm: str
    found: bool
    path_node_ids: list[str] = Field(default_factory=list)
    path_coords: list[tuple[float, float]] = Field(default_factory=list)
    total_distance_m: float = 0.0
    total_risk_penalty: float = 0.0
    total_cost: float = 0.0
    nodes_explored: int = 0
    time_ms: float = 0.0
    explanation: str = ""


class RouteCompareResponse(BaseModel):
    """Response containing comparisons across all requested algorithms."""
    scenario_id: str
    start_node: str
    destination_node: str
    results: list[RouteResultSchema]
    hazard_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Count of normal, risky, and blocked edges in the active graph.",
    )
