from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_db
from src.utils.database_manager import DatabaseManager

router = APIRouter()

@router.get("/")
async def list_matches(
    tournament_id: str = Query(None, description="Filter matches by tournament ID."),
    team_id: str = Query(None, description="Filter matches by a participating team's ID."),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return per page."),
    skip: int = Query(0, ge=0, description="Number of results to skip for pagination."),
    db: DatabaseManager = Depends(get_db)
):
    """
    Lists matches with optional filters and pagination.
    This endpoint returns a summary and does not include detailed performance stats.
    """
    matches = db.get_matches(
        limit=limit, 
        offset=skip, 
        tournament_id=tournament_id, 
        team_id=team_id
    )
    return matches

@router.get("/{match_id}", summary="Get match by ID")
async def get_match_detail(match_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Retrieves detailed information for a specific match by its unique ID,
    including full performance stats for each player and map.
    """
    match = db.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")
    return match