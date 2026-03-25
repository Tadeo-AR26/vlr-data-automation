from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_db
from src.utils.database_manager import DatabaseManager

router = APIRouter()

@router.get("/")
async def list_teams(
    name: str = Query(None, description="Filter by exact team name (case-insensitive). Returns a single team."), 
    tag: str = Query(None, description="Filter by exact team tag (case-insensitive). Returns a single team."), 
    country: str = Query(None, description="Filter teams by country. Returns a paginated list."), 
    limit: int = Query(20, ge=1, le=100, description="Number of results to return per page."),
    skip: int = Query(0, ge=0, description="Number of results to skip for pagination."), 
    db: DatabaseManager = Depends(get_db)
):
    """
    Lists teams with optional filters and pagination
    - If `name` or `tag` is provided, it returns a single matching team
    - If `country` is provided, it returns a paginated list of teams from that country
    - If no filters are provided, it returns a paginated list of all teams sorted by rank
    """
    if name:
        team = db.get_team_by_name(name)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team with name '{name}' not found.")
        return team

    if tag:
        team = db.get_team_by_tag(tag)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team with tag '{tag}' not found.")
        return team

    if country:
        return db.get_teams_by_country(country, limit=limit, offset=skip)

    return db.get_teams(limit=limit, offset=skip)

@router.get("/{team_id}", summary="Get team by ID")
async def get_team_by_id(team_id: str, db: DatabaseManager = Depends(get_db)):
    team = db.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    return team

@router.get("/{team_id}/roster")
async def get_team_roster(
    team_id: str, db: DatabaseManager = Depends(get_db)):
    team = db.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "roster": team.get("roster", [])
    }

@router.get("/{team_id}/matches/upcoming")
async def get_upcoming_matches(team_id: str, db: DatabaseManager = Depends(get_db)):
    team = db.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "upcoming_matches": team.get("upcoming_matches", [])
    }

@router.get("/{team_id}/matches/recent")
async def get_recent_matches(team_id: str, db: DatabaseManager = Depends(get_db)):
    team = db.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "recent_matches": team.get("recent_matches", [])
    }