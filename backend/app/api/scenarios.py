"""
scenarios.py
============
FastAPI API router for inspecting predefined flood scenarios and raw road graph data.
"""

from fastapi import APIRouter, HTTPException
from app.services.graph_service import (
    load_scenarios,
    get_scenario,
    load_raw_graph_data,
)
from app.models.schemas import (
    ScenarioSummarySchema,
    ScenarioDetailSchema,
    GraphSchema,
)

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get("", response_model=list[ScenarioSummarySchema])
def list_scenarios() -> list[ScenarioSummarySchema]:
    """
    Retrieve summaries of all predefined flood simulation scenarios.
    """
    scenarios = load_scenarios()
    return [
        ScenarioSummarySchema(
            id=s["id"],
            name=s["name"],
            description=s["description"],
            default_start=s["default_start"],
            default_destination=s["default_destination"],
            teaching_note=s.get("teaching_note", ""),
        )
        for s in scenarios
    ]


@router.get("/{scenario_id}", response_model=ScenarioDetailSchema)
def get_scenario_details(scenario_id: str) -> ScenarioDetailSchema:
    """
    Retrieve full configuration and graph structure for a specific scenario.
    Includes node coordinates, road lengths, and preset blocked/risky segments.
    """
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{scenario_id}' not found.",
        )

    raw_graph = load_raw_graph_data()

    return ScenarioDetailSchema(
        id=scenario["id"],
        name=scenario["name"],
        description=scenario["description"],
        default_start=scenario["default_start"],
        default_destination=scenario["default_destination"],
        hazards=scenario["hazards"],
        teaching_note=scenario.get("teaching_note", ""),
        graph=GraphSchema(**raw_graph),
    )
