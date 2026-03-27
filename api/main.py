from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.routers import teams, players, matches, tournaments
from sync_activity import run_sync

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_sync, 'interval', hours=12, id="sync_job")
    scheduler.start()
    
    # IMPORTANT: Don't call run_sync() because it will block the startup. Instead, we rely on the scheduled job to run every 12 hours.
    # The first sync will happen 12 hours after the server starts
    
    yield # Here the app runs
    
    print("Stopping Scheduler...")
    scheduler.shutdown()

app = FastAPI(
    title="Valorant Esports API",
    description="API for accessing Valorant esports data including teams, players, and matches.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(players.router, prefix="/players", tags=["Players"]) 
app.include_router(matches.router, prefix="/matches", tags=["Matches"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["Tournaments"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Valorant Esports API! Use the endpoints to access teams, players, matches, and tournaments data. ",
        "docs": "/docs",
        "status": "online"
    }

from fastapi import BackgroundTasks
import historical_fetch # Importa tu función de scrapeo

@app.get("/admin/seed-db")
async def seed_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(historical_fetch.run_all)
    return {"status": "Scraping histórico iniciado en la nube"}