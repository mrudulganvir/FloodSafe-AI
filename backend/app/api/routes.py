"""
routes.py
=========
FastAPI API router for algorithm execution and route comparison under simulated flood conditions.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import RouteCompareRequest, RouteCompareResponse
from app.services.route_service import compare_routes

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/compare", response_model=RouteCompareResponse)
def compare_routing_algorithms(request: RouteCompareRequest) -> RouteCompareResponse:
    """
    Execute selected pathfinding algorithms (BFS, Greedy Best-First, A*) on the
    specified scenario and hazard state, returning comparative performance metrics.
    """
    try:
        response = compare_routes(
            scenario_id=request.scenario_id,
            start_node=request.start_node,
            destination_node=request.destination_node,
            hazards=request.hazards,
            algorithms=request.algorithms,
        )
        return response
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=404, detail=err_msg)
        else:
            raise HTTPException(status_code=400, detail=err_msg)
