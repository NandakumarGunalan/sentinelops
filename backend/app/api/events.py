from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import SecurityEvent
from app.schemas import IngestRequest, SecurityEventOut

router = APIRouter(prefix="/ingest", tags=["events"])


@router.post("", response_model=SecurityEventOut, status_code=201)
def ingest_event(payload: IngestRequest, db: Session = Depends(get_db)):
    event = SecurityEvent(
        source=payload.source,
        event_type=payload.event_type,
        severity=payload.severity,
        raw_payload=payload.raw_payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
