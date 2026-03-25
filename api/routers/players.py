from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_db
from src.utils.database_manager import DatabaseManager

router = APIRouter()

@router.get("/")
async def list_players(
    ign: str = None, 
    country: str = Query(None, description="Filter players by country name or code."), 
    limit: int = Query(20, le=100), 
    skip: int = 0, 
    db: DatabaseManager = Depends(get_db)
):
    if ign:
        player = db.get_player_by_ign(ign)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found.")
        return player
    
    if country:
        return db.get_players_by_country(country=country, limit=limit, offset=skip)

    return db.get_players(limit=limit, offset=skip)

@router.get("/{player_id}")
async def player_detail(player_id: str, db: DatabaseManager = Depends(get_db)):
    player = db.get_player_by_id(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found.")
    return player

@router.get("/past-teams/")
async def get_player_past_teams(
    player_id: str = Query(None, description="The player's unique ID"),
    ign: str = Query(None, description="The player's in-game name (IGN)"),
    db: DatabaseManager = Depends(get_db)
):
    if not player_id and not ign:
        raise HTTPException(status_code=400, detail="Either 'player_id' or 'ign' must be provided.")
    
    if player_id and ign:
        raise HTTPException(status_code=400, detail="Provide only 'player_id' or 'ign', not both.")

    past_teams = db.get_player_past_teams(player_id=player_id, ign=ign)
    if past_teams is None:
        raise HTTPException(status_code=404, detail="Player not found.")
        
    return past_teams