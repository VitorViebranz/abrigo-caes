import os

from uvicorn import run
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, users_router, dogs_router, vaccines_router, financial_router
from middlewares.trace_middleware import TraceIDMiddleware

load_dotenv()

app = FastAPI(
    title="Abrigo de Cães — API",
    description="Internal management system for the dog shelter. Auth required for all routes.",
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

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dogs_router)
app.include_router(vaccines_router)
app.include_router(financial_router)


@app.get("/status", tags=["Status"])
def get_status():
    return {"status": "online", "system": "Abrigo de Cães API"}

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, log_level="info")