import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine
from app import models
from app.api import events, findings, investigations
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

# Validate configuration
try:
    settings.validate()
    logger.info("Configuration validated successfully")
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    raise

# Initialize tool registry
from app.tools.registry import tool_registry
from app.tools.ip_reputation import IPReputationTool
from app.tools.privileged_user import PrivilegedUserTool
from app.tools.related_alerts import RelatedAlertsTool
from app.tools.geo_anomaly import GeoAnomalyTool
from app.tools.playbook import PlaybookTool
from app.tools.action_simulator import ActionSimulatorTool

# Register all tools
tool_registry.register(IPReputationTool())
tool_registry.register(PrivilegedUserTool())
tool_registry.register(RelatedAlertsTool())
tool_registry.register(GeoAnomalyTool())
tool_registry.register(PlaybookTool())
tool_registry.register(ActionSimulatorTool())

logger.info(f"Registered {len(tool_registry.list_tools())} tools")

app = FastAPI(
    title="SentinelOps API",
    description="Autonomous security triage backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "database": "connected",
        "version": "0.1.0",
        "tools_registered": len(tool_registry.list_tools())
    }


app.include_router(events.router)
app.include_router(findings.router)
app.include_router(investigations.router)
