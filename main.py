from fastapi import FastAPI
from models.helper import  create_tables
from routers.auth import router as auth_router
from routers.incident import router as incident_router
from routers.comment import router as comment_router
from routers.logs import router as logs_router
from routers import analytics
import os
import sys
import asyncio

app = FastAPI()

app.include_router(auth_router)
app.include_router(comment_router)
app.include_router(incident_router)
app.include_router(logs_router)
app.include_router(analytics.router)
@app.on_event("startup")
async def startup():
    if "pytest" in sys.modules or os.getenv("SKIP_DB_STARTUP") == "1":
        return

    try:
        await asyncio.wait_for(create_tables(), timeout=1)
    except Exception:
        pass