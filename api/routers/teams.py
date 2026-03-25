from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_db
from src.utils.database_manager import DatabaseManager

router = APIRouter()

@router.get("/")
async def get_teams(
    name: str = None, 
    tag: str = None, 
    country: str = None, 
    limit: int = Query(10, le=500),
    skip: int = 0, 
    db: DatabaseManager = Depends(get_db)
):
    if name:
        team = db.get_team_by_name(name)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team with name '{name}' not found")
        return team

    elif tag:
        team = db.get_team_by_tag(tag)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team with tag '{tag}' not found")
        return team

    elif country:
        teams = db.get_teams_by_country(country, limit=limit)
        if not teams:
            return []
        return teams

    else:
        return db.get_teams(limit=limit, offset=skip)

@router.get("/{team_id}/roster")
async def get_team_roster(
    team_id: str = None, 
    name: str = None, 
    tag: str = None, 
    db: DatabaseManager = Depends(get_db)
):
    team = db.get_team_by_any(team_id, name, tag)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return {
        "team_name": team["name"],
        "roster": team.get("roster", [])
    }

@router.get("/{team_id}/matches/upcoming")
async def get_upcoming(
    team_id: str = None, 
    name: str = None, 
    tag: str = None, 
    db: DatabaseManager = Depends(get_db)
):
    team = db.get_team_by_any(team_id, name, tag)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return {
        "team_name": team["name"],
        "upcoming_matches": team.get("upcoming_matches", [])
    }

@router.get("/{team_id}/matches/recent")
async def get_recent(
    team_id: str = None, 
    name: str = None, 
    tag: str = None, 
    db: DatabaseManager = Depends(get_db)
):
    team = db.get_team_by_any(team_id, name, tag)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return {
        "team_name": team["name"],
        "recent_matches": team.get("recent_matches", [])
    }