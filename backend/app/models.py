from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)          # e.g. "cloudtrail", "siem"
    event_type = Column(String, nullable=False)      # e.g. "login_failure"
    severity = Column(String, default="unknown")     # low / medium / high / critical
    raw_payload = Column(Text, nullable=False)       # original JSON as string
    received_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    investigation = relationship("Investigation", back_populates="alert", uselist=False)


class Investigation(Base):
    __tablename__ = "investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("security_events.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="running")  # running, completed, failed, max_steps_reached
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    final_risk_score = Column(Float, nullable=True)
    step_count = Column(Integer, default=0)
    
    # Relationships
    alert = relationship("SecurityEvent", back_populates="investigation")
    steps = relationship("InvestigationStep", back_populates="investigation", cascade="all, delete-orphan")
    finding = relationship("Finding", back_populates="investigation", uselist=False)


class InvestigationStep(Base):
    __tablename__ = "investigation_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)  # initialize, analyze_evidence, select_tool, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    inputs = Column(Text)  # JSON string
    outputs = Column(Text)  # JSON string
    reasoning = Column(Text)
    
    # Relationships
    investigation = relationship("Investigation", back_populates="steps")
    tool_invocations = relationship("ToolInvocation", back_populates="step", cascade="all, delete-orphan")


class ToolInvocation(Base):
    __tablename__ = "tool_invocations"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("investigation_steps.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String, nullable=False)
    parameters = Column(Text, nullable=False)  # JSON string
    result = Column(Text)  # JSON string
    duration_ms = Column(Float, nullable=False)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    step = relationship("InvestigationStep", back_populates="tool_invocations")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, default="medium")      # low / medium / high / critical
    recommended_action = Column(String)              # no_action_required, monitor, isolate_host, block_ip, escalate_to_human
    status = Column(String, default="open")          # open / in_review / resolved / false_positive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    investigation = relationship("Investigation", back_populates="finding")
    feedback_entries = relationship("Feedback", back_populates="finding", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer)  # 1-5
    correctness = Column(String)  # correct, incorrect, partially_correct
    comment = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    submitted_by = Column(String)
    
    # Relationships
    finding = relationship("Finding", back_populates="feedback_entries")
