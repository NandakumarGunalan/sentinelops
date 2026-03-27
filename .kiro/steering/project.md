---
inclusion: always
---

# SentinelOps — Project Steering

## What this is
Autonomous security triage infrastructure. Hackathon project.

## Stack decisions
- Backend: FastAPI (Python 3.11+)
- Agent orchestration: LangGraph
- Frontend: React 18 + Vite + TypeScript
- Persistence: SQLite (dev), swappable to Postgres
- Containerization: Docker Compose

## Conventions
- Backend lives in `backend/`, frontend in `frontend/`
- All agents defined under `backend/app/agents/`
- API routes under `backend/app/api/`
- SQLite DB file written to `data/sentinelops.db`
- Keep Docker Compose working at all times for local dev

## Goals for hackathon
1. Ingest raw security events
2. Run autonomous LangGraph triage pipeline
3. Surface prioritized findings in the React UI
