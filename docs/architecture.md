# Architecture

## Overview

SentinelOps is an autonomous security triage system. Incoming alerts are
processed by a LangGraph agent pipeline that classifies, enriches, and
prioritizes them before surfacing actionable findings in the UI.

## Components

- **Ingest layer**: receives raw security events via REST or webhook
- **Agent pipeline**: LangGraph graph that triages and enriches events
- **Persistence**: SQLite for local/dev; swappable for Postgres in prod
- **API**: FastAPI exposes triage results and agent status
- **UI**: React dashboard for reviewing and acting on findings

## Data flow

```
Event source → POST /ingest → LangGraph pipeline → SQLite → GET /findings → UI
```
