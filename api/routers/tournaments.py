from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_db
from src.utils.database_manager import DatabaseManager

router = APIRouter()

@router.get("/")
async def list_tournaments(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: DatabaseManager = Depends(get_db)
):
    """
    Lists all available tournaments with pagination.
    """
    tournaments = db.get_tournaments(limit=limit, offset=skip)
    return tournaments

@router.get("/{tournament_id}")
async def get_tournament_details(
    tournament_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Retrieves all details for a specific tournament, including its list of
    participating team IDs and match IDs.
    """
    tournament = db.get_tournament_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found.")
    return tournament

@router.get("/{tournament_id}/teams")
async def get_tournament_teams(
    tournament_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Retrieves the list of teams (ID, name, and tag) that participated in a specific tournament.
    """
    teams = db.get_tournament_teams(tournament_id)
    if teams is None:
        raise HTTPException(status_code=404, detail="Tournament not found.")
    return teams

@router.get("/{tournament_id}/matches")
async def get_tournament_matches(
    tournament_id: str,
    db: DatabaseManager = Depends(get_db)
):
    matches = db.get_tournament_matches(tournament_id)
    if matches is None:
        raise HTTPException(status_code=404, detail="Tournament not found.")
    return matches