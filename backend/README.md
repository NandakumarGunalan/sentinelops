# SentinelOps Backend

Autonomous security triage infrastructure backend built with FastAPI, LangGraph, and SQLite.

## Features

- **Autonomous Investigation**: LangGraph-powered multi-step security alert triage
- **6 Investigation Tools**: IP reputation, privileged user lookup, related alerts, geo anomaly detection, playbook lookup, action simulator
- **Complete Audit Trail**: Every investigation step, tool call, and decision persisted to database
- **REST API**: Endpoints for alert ingestion and investigation trace retrieval
- **Bounded Autonomy**: Configurable step limits and stopping conditions

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create data directory:
```bash
mkdir -p data
```

3. Copy environment configuration:
```bash
cp .env.example .env
```

4. (Optional) Customize configuration in `.env`

### Running the Backend

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Health Check
```bash
GET /health
```

### Ingest Alert and Trigger Investigation
```bash
POST /api/alerts
Content-Type: application/json

{
  "source": "cloudtrail",
  "event_type": "login_failure",
  "severity": "high",
  "raw_payload": "{\"user_id\": \"user123\", \"source_ip\": \"192.168.1.100\"}"
}
```

### Get Investigation Trace
```bash
GET /api/investigations/{investigation_id}/trace
```

## Configuration

Key environment variables:

- `DATABASE_URL`: SQLite database path (default: `sqlite:///./data/sentinelops.db`)
- `MAX_INVESTIGATION_STEPS`: Maximum steps per investigation (default: 15)
- `TOOL_TIMEOUT_SECONDS`: Tool execution timeout (default: 10)
- `ENABLE_REAL_ACTIONS`: Enable real action execution vs simulation (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

## Architecture

```
backend/
├── app/
│   ├── agents/          # LangGraph workflow and nodes
│   ├── api/             # REST API endpoints
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── services/        # Business logic (investigation, trace recording)
│   ├── tools/           # Investigation tools (6 MVP tools)
│   ├── config.py        # Configuration management
│   ├── db.py            # Database connection
│   └── main.py          # FastAPI application
├── data/                # SQLite database storage
└── requirements.txt     # Python dependencies
```

## Database

The backend uses SQLite for local development with the following schema:

- `security_events`: Ingested security alerts
- `investigations`: Investigation metadata and status
- `investigation_steps`: Individual workflow steps
- `tool_invocations`: Tool execution records
- `findings`: Final investigation results
- `feedback`: Human feedback on findings

Tables are created automatically on startup.

## Tools

The system includes 6 deterministic investigation tools:

1. **IP Reputation Lookup**: Check IP address reputation (hash-based scoring)
2. **Privileged User Lookup**: Check if user has elevated privileges
3. **Recent Related Alerts**: Find similar alerts in recent history
4. **Geo Anomaly Check**: Detect unusual geographic access patterns
5. **Playbook Lookup**: Find recommended response playbooks
6. **Action Simulator**: Simulate response actions (safe by default)

All tools use deterministic logic for reliable hackathon demos.

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black app/
flake8 app/
```

## Troubleshooting

### Database Issues

If you encounter database errors, delete the database and restart:

```bash
rm data/sentinelops.db
uvicorn app.main:app --reload
```

### Import Errors

Make sure you're in the `backend/` directory when running the server:

```bash
cd backend
uvicorn app.main:app --reload
```

### Tool Timeouts

If tools are timing out, increase `TOOL_TIMEOUT_SECONDS` in `.env`

## License

MIT
