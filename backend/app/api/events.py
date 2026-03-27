from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import SecurityEvent
from app.schemas import IngestRequest, SecurityEventOut, AlertIngestResponse
from app.services.investigation_service import run_investigation
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


async def trigger_investigation_background(alert_id: int):
    """Background task to run investigation"""
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        await run_investigation(db, alert_id)
    except Exception as e:
        logger.error(f"Background investigation failed for alert {alert_id}: {e}")
    finally:
        db.close()


@router.post("", response_model=AlertIngestResponse, status_code=201)
async def ingest_alert(
    payload: IngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ingest a security alert and trigger autonomous investigation"""
    # Create security event
    event = SecurityEvent(
        source=payload.source,
        event_type=payload.event_type,
        severity=payload.severity,
        raw_payload=payload.raw_payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    logger.info(f"Alert {event.id} ingested. Triggering investigation.")
    
    # Trigger investigation in background
    background_tasks.add_task(trigger_investigation_background, event.id)
    
    return {
        "alert_id": event.id,
        "investigation_id": None,  # Will be created in background
        "status": "investigation_started",
        "message": "Alert ingested and investigation triggered"
    }
