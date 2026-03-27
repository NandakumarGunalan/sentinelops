# SentinelOps

Autonomous security triage infrastructure — hackathon project.

## Stack

- **Backend**: FastAPI + LangGraph agent orchestration
- **Frontend**: React + Vite
- **Persistence**: SQLite
- **Infrastructure**: Docker Compose

## Structure

```
backend/    # FastAPI app + LangGraph agents
frontend/   # React + Vite UI
docs/       # Architecture and API docs
data/       # SQLite DB and seed data
scripts/    # Dev/ops utility scripts
tests/      # Integration and unit tests
```

## Getting Started

```bash
docker-compose up --build
```

Frontend: http://localhost:5173  
Backend API: http://localhost:8000  
API Docs: http://localhost:8000/docs
