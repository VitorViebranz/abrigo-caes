import os

from uvicorn import run
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    auth_router,
    users_router,
    roles_router,
    permissions_router,
    animals_router,
    vaccines_router,
    financial_router,
    inventory_router,
    donations_router,
)
from middlewares.trace_middleware import TraceIDMiddleware

load_dotenv()

app = FastAPI(
    title="Abrigo de Animais — API",
    description="Internal management system for the animal shelter. Auth required for all routes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TraceIDMiddleware)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(animals_router)
app.include_router(vaccines_router)
app.include_router(financial_router)
app.include_router(inventory_router)
app.include_router(donations_router)


@app.get("/status", tags=["Status"])
def get_status():
    return {"status": "online", "system": "Abrigo de Animais API"}

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, log_level="info")