from fastapi import FastAPI
from api.routers import teams, players, matches #, tournaments

app = FastAPI(
    title="Valorant Esports API",
    description="API for accessing Valorant esports data including teams, players, and matches.",
    version="1.0.0"
)

app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(players.router, prefix="/players", tags=["Players"]) 
app.include_router(matches.router, prefix="/matches", tags=["Matches"])
#app.include_router(tournaments.router, prefix="/tournaments", tags=["Tournaments"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Valorant Esports API! Use the endpoints to access teams, players, matches, and tournaments data. ",
        "docs": "/docs",
        "status": "online"
    }