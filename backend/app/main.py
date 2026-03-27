from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine
from app import models
from app.api import events, findings

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SentinelOps API",
    description="Autonomous security triage backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


app.include_router(events.router)
app.include_router(findings.router)
