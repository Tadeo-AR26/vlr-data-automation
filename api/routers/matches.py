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

@router.get("/{match_id}/map-stats", summary="Get player stats for a specific map")
async def get_map_stats(
    match_id: str,
    map_name: str = Query(None, description="The name of the map (e.g., 'Haven', 'Split'). Case-insensitive."),
    map_number: int = Query(None, ge=1, description="The order of the map in the series (e.g., 1 for the first map)."),
    db: DatabaseManager = Depends(get_db)
):
    """
    Retrieves player performance statistics for a single map within a match.
    Provide either `map_name` or `map_number`.
    """
    if not map_name and not map_number:
        raise HTTPException(status_code=400, detail="Either 'map_name' or 'map_number' must be provided.")
    if map_name and map_number:
        raise HTTPException(status_code=400, detail="Provide only 'map_name' or 'map_number', not both.")

    match = db.get_match_by_id(match_id)
    if not match or "performance" not in match:
        raise HTTPException(status_code=404, detail="Match or performance data not found.")

    performance_data = match["performance"]
    
    # The first item is "All Maps", so we skip it for map-specific queries.
    map_specific_performance = performance_data[1:]

    found_map = None
    if map_number:
        if map_number > len(map_specific_performance):
            raise HTTPException(status_code=404, detail=f"Map number {map_number} is out of bounds for this match.")
        found_map = map_specific_performance[map_number - 1]
    elif map_name:
        for map_perf in map_specific_performance:
            if map_perf.get("map", "").lower() == map_name.lower():
                found_map = map_perf
                break
    
    if not found_map:
        raise HTTPException(status_code=404, detail=f"Map '{map_name or map_number}' not found in this match.")

    return found_map.get("players", [])

@router.get("/{match_id}/players", summary="Get players in a match")
async def get_match_players(match_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Gets a list of all players (ID and IGN) who participated in a specific match.
    """
    match = db.get_match_by_id(match_id)
    if not match or "performance" not in match or not match["performance"]:
        raise HTTPException(status_code=404, detail="Match or performance data not found.")

    # "All Maps" performance is at index 0 and contains all players
    all_maps_perf = match["performance"][0]
    player_ids = {player.get("player_id") for player in all_maps_perf.get("players", []) if player.get("player_id")}

    if not player_ids:
        return []

    return db._get_player_names(list(player_ids))

@router.get("/{match_id}/result", summary="Get match result")
async def get_match_result(match_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Gets the final score and participating teams for a specific match.
    """
    summary = db.get_match_summary(match_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Match not found.")
    return summary