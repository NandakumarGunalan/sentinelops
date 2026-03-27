from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Finding
from app.schemas import FindingOut

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("", response_model=list[FindingOut])
def list_findings(
    status: str | None = Query(default=None, description="Filter by status"),
    priority: str | None = Query(default=None, description="Filter by priority"),
    db: Session = Depends(get_db),
):
    q = db.query(Finding)
    if status:
        q = q.filter(Finding.status == status)
    if priority:
        q = q.filter(Finding.priority == priority)
    return q.order_by(Finding.created_at.desc()).all()


@router.get("/{finding_id}", response_model=FindingOut)
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding
