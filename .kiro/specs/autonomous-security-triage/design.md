# Technical Design Document: SentinelOps

## Overview

SentinelOps is a bounded autonomous security triage infrastructure platform built for hackathon demonstration. The system processes security alerts through an intelligent, multi-step investigation workflow powered by LangGraph. When an alert arrives, a bounded autonomous agent launches an investigation by calling specialized tools, gathering evidence, dynamically updating risk assessments, and selecting appropriate actions—all while maintaining complete execution traces for auditability.

### Design Philosophy

This design prioritizes hackathon-realistic implementation with these core principles:

1. **Bounded Autonomy**: The agent operates within clear constraints (6 tools, 15 step limit, explicit stopping conditions)
2. **LangGraph as Core Runtime**: All investigation orchestration runs through LangGraph state machines
3. **Database as Audit Layer**: Every decision, tool call, and state transition is persisted
4. **Modular and Demonstrable**: Each component can be developed and demoed independently
5. **Deterministic by Default**: Prefer reliable, predictable behavior over complex autonomy

### Key Technologies

- **Backend**: FastAPI (Python 3.11+) for REST API and agent hosting
- **Agent Orchestration**: LangGraph for bounded autonomous investigation workflows
- **Database**: SQLite (dev) with PostgreSQL compatibility for production
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS
- **Containerization**: Docker Compose for local development

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Investigation│  │  Execution   │  │   Findings   │          │
│  │     List     │  │    Trace     │  │   Dashboard  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     REST API Layer                        │  │
│  │  /api/alerts  /api/investigations  /api/findings         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              LangGraph Orchestration Layer                │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │         Triage Agent (LangGraph StateGraph)        │  │  │
│  │  │  • Investigation State Management                  │  │  │
│  │  │  • Tool Selection & Invocation                     │  │  │
│  │  │  • Risk Score Updates                              │  │  │
│  │  │  • Stopping Condition Evaluation                   │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Tool Registry                          │  │
│  │  • IP Reputation Lookup                                   │  │
│  │  • Privileged User Lookup                                 │  │
│  │  • Recent Related Alerts Lookup                           │  │
│  │  • Geo Anomaly Check                                      │  │
│  │  • Playbook Lookup                                        │  │
│  │  • Action Simulator                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Database Layer (SQLAlchemy)              │  │
│  │  • SecurityEvent  • Investigation  • InvestigationStep   │  │
│  │  • ToolInvocation • Finding        • Feedback            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────────────┐
                    │  SQLite / Postgres │
                    │  (data/sentinelops.db) │
                    └─────────────────┘
```

### Data Flow

1. **Alert Ingestion**: Security event arrives via POST /api/alerts
2. **Investigation Trigger**: Backend creates Investigation record and launches LangGraph workflow
3. **Autonomous Triage**: LangGraph agent executes bounded investigation loop:
   - Analyze current state and evidence
   - Select next tool to invoke
   - Execute tool and gather evidence
   - Update risk score based on new evidence
   - Check stopping conditions (max steps, sufficient evidence, error)
   - Repeat or terminate
4. **Trace Persistence**: Every step, tool call, and decision is written to database
5. **Finding Generation**: Agent produces final Finding with recommended action
6. **UI Visualization**: Frontend fetches investigation trace and displays timeline

### Component Responsibilities

**FastAPI Backend**:
- REST API endpoints for alert ingestion, investigation queries, findings
- LangGraph workflow initialization and execution
- Tool registry and invocation framework
- Database persistence via SQLAlchemy
- Configuration management

**LangGraph Agent**:
- Investigation state management across multiple steps
- Tool selection logic based on alert content and gathered evidence
- Risk score calculation and updates
- Stopping condition evaluation
- Action selection based on final risk assessment

**Database**:
- Persistent storage for all alerts, investigations, steps, tool calls, findings
- Audit trail for every agent decision
- Query interface for frontend visualization
- Feedback storage for continuous improvement

**React Frontend**:
- Investigation list with filtering and search
- Execution trace timeline visualization
- Finding dashboard with priority indicators
- Feedback submission interface

## Backend Module Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization, CORS, health endpoint
│   ├── config.py                  # Configuration loading from env vars
│   ├── db.py                      # SQLAlchemy engine and session management
│   ├── models.py                  # SQLAlchemy ORM models
│   ├── schemas.py                 # Pydantic schemas for API request/response
│   │
│   ├── api/                       # REST API route handlers
│   │   ├── __init__.py
│   │   ├── alerts.py              # POST /api/alerts, GET /api/alerts
│   │   ├── investigations.py     # GET /api/investigations, GET /api/investigations/{id}
│   │   ├── findings.py            # GET /api/findings, POST /api/findings/{id}/feedback
│   │   └── health.py              # GET /health
│   │
│   ├── agents/                    # LangGraph agent definitions
│   │   ├── __init__.py
│   │   ├── triage_agent.py       # Main LangGraph StateGraph definition
│   │   ├── state.py               # InvestigationState TypedDict
│   │   ├── nodes.py               # LangGraph node functions
│   │   └── edges.py               # Conditional edge functions
│   │
│   ├── tools/                     # Tool implementations
│   │   ├── __init__.py
│   │   ├── registry.py            # Tool registry and invocation framework
│   │   ├── ip_reputation.py      # IP reputation lookup tool
│   │   ├── privileged_user.py    # Privileged user lookup tool
│   │   ├── related_alerts.py     # Recent related alerts lookup tool
│   │   ├── geo_anomaly.py        # Geo anomaly check tool
│   │   ├── playbook.py            # Playbook lookup tool
│   │   └── action_simulator.py   # Action simulator tool
│   │
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── investigation_service.py  # Investigation orchestration
│   │   ├── risk_calculator.py        # Risk score calculation logic
│   │   └── trace_recorder.py         # Execution trace persistence
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       └── logging.py             # Structured logging setup
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_tools.py              # Unit tests for tools
│   ├── test_agent.py              # Integration tests for LangGraph workflow
│   └── test_api.py                # API endpoint tests
│
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container definition
└── README.md                      # Backend documentation
```

## LangGraph State Design

### InvestigationState TypedDict

The LangGraph workflow maintains investigation state across all nodes using a TypedDict:

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class ToolInvocationRecord(TypedDict):
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    timestamp: datetime
    duration_ms: float
    error: Optional[str]

class RiskScoreUpdate(TypedDict):
    old_score: float
    new_score: float
    justification: str
    timestamp: datetime

class InvestigationState(TypedDict):
    # Investigation metadata
    investigation_id: int
    alert_id: int
    alert_data: Dict[str, Any]
    
    # Execution tracking
    step_count: int
    max_steps: int
    status: str  # "running", "completed", "failed", "max_steps_reached"
    
    # Evidence accumulation
    evidence: List[Dict[str, Any]]
    tool_invocations: List[ToolInvocationRecord]
    
    # Risk assessment
    current_risk_score: float
    risk_score_history: List[RiskScoreUpdate]
    
    # Decision tracking
    reasoning_log: List[str]
    next_action: Optional[str]  # "call_tool", "conclude", "escalate"
    
    # Final output
    recommended_action: Optional[str]
    finding_title: Optional[str]
    finding_description: Optional[str]
    
    # Error handling
    errors: List[str]
```

### State Update Strategy

- **Immutable Updates**: Each node returns a partial state dict that gets merged
- **Evidence Accumulation**: New evidence is appended to the evidence list
- **Risk Score Evolution**: Risk score updates are tracked in history for auditability
- **Step Counting**: Incremented after each node execution to enforce max_steps limit


## LangGraph Nodes and Conditional Edges

### Node Definitions

The LangGraph workflow consists of these nodes:

**1. initialize_investigation**
- **Purpose**: Set up initial investigation state from alert data
- **Inputs**: Alert data from database
- **Outputs**: Initialized InvestigationState with alert context, initial risk score
- **Logic**: 
  - Parse alert severity and map to initial risk score (0-100)
  - Initialize empty evidence list and tool invocation history
  - Set step_count to 0, max_steps to 15
  - Set status to "running"

**2. analyze_evidence**
- **Purpose**: Analyze accumulated evidence and determine next action
- **Inputs**: Current InvestigationState with evidence
- **Outputs**: Updated state with reasoning_log entry and next_action decision
- **Logic**:
  - Review all evidence gathered so far
  - Identify information gaps
  - Determine if sufficient evidence exists to conclude
  - Set next_action to "call_tool", "conclude", or "escalate"
  - Log reasoning for decision

**3. select_tool**
- **Purpose**: Choose which tool to invoke based on current evidence gaps
- **Inputs**: InvestigationState with next_action="call_tool"
- **Outputs**: Updated state with selected tool name and parameters
- **Logic**:
  - Analyze alert type and existing evidence
  - Select most relevant tool from registry
  - Prepare tool parameters from alert data and evidence
  - Log tool selection reasoning

**4. invoke_tool**
- **Purpose**: Execute selected tool and gather evidence
- **Inputs**: InvestigationState with selected tool and parameters
- **Outputs**: Updated state with tool result added to evidence and tool_invocations
- **Logic**:
  - Call tool via registry with timeout handling
  - Record tool invocation with timestamp and duration
  - Add tool result to evidence list
  - Handle tool errors gracefully (log error, continue investigation)
  - Increment step_count

**5. update_risk_score**
- **Purpose**: Recalculate risk score based on new evidence
- **Inputs**: InvestigationState with new evidence
- **Outputs**: Updated state with new risk score and justification
- **Logic**:
  - Apply risk calculation rules based on evidence type
  - Compare new score to old score
  - Record risk score update with justification
  - Check if score crosses critical threshold (>80 = escalate)

**6. check_stopping_conditions**
- **Purpose**: Determine if investigation should continue or terminate
- **Inputs**: Current InvestigationState
- **Outputs**: Updated state with status and next_action
- **Logic**:
  - Check if step_count >= max_steps (terminate with "max_steps_reached")
  - Check if sufficient evidence gathered (terminate with "completed")
  - Check if critical risk threshold crossed (set next_action="escalate")
  - Check if errors prevent continuation (terminate with "failed")
  - Otherwise, set next_action to continue investigation

**7. generate_finding**
- **Purpose**: Produce final finding with recommended action
- **Inputs**: InvestigationState with status="completed" or "max_steps_reached"
- **Outputs**: Updated state with finding_title, finding_description, recommended_action
- **Logic**:
  - Synthesize all evidence into finding description
  - Map final risk score to priority (low/medium/high/critical)
  - Select recommended action based on risk score and evidence:
    - 0-20: "no_action_required"
    - 21-40: "monitor"
    - 41-60: "isolate_host"
    - 61-80: "block_ip"
    - 81-100: "escalate_to_human"
  - Generate descriptive finding title

**8. handle_error**
- **Purpose**: Handle investigation failures gracefully
- **Inputs**: InvestigationState with errors
- **Outputs**: Updated state with status="failed" and error summary
- **Logic**:
  - Log all errors encountered
  - Set status to "failed"
  - Generate minimal finding indicating investigation failure

### Conditional Edge Functions

**should_continue_investigation**
- **From**: check_stopping_conditions
- **To**: analyze_evidence (if continue) OR generate_finding (if terminate)
- **Logic**: 
  - If status == "running" and next_action != "conclude": route to analyze_evidence
  - Otherwise: route to generate_finding

**should_call_tool**
- **From**: analyze_evidence
- **To**: select_tool (if call_tool) OR generate_finding (if conclude)
- **Logic**:
  - If next_action == "call_tool": route to select_tool
  - If next_action == "conclude": route to generate_finding
  - If next_action == "escalate": route to generate_finding

**has_errors**
- **From**: Any node
- **To**: handle_error (if errors exist) OR next node (if no errors)
- **Logic**:
  - If len(state["errors"]) > 0: route to handle_error
  - Otherwise: continue to next node

### LangGraph Workflow Diagram

```
                    START
                      │
                      ▼
          ┌───────────────────────┐
          │ initialize_investigation │
          └───────────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │   analyze_evidence     │◄─────┐
          └───────────────────────┘      │
                      │                   │
                      ▼                   │
              [should_call_tool?]         │
                 /          \             │
          call_tool      conclude         │
             /                \           │
            ▼                  ▼          │
    ┌──────────────┐    ┌──────────────┐│
    │ select_tool  │    │generate_finding│
    └──────────────┘    └──────────────┘
            │                   │
            ▼                   │
    ┌──────────────┐           │
    │ invoke_tool  │           │
    └──────────────┘           │
            │                   │
            ▼                   │
    ┌──────────────────┐       │
    │update_risk_score │       │
    └──────────────────┘       │
            │                   │
            ▼                   │
    ┌──────────────────────┐   │
    │check_stopping_conditions│ │
    └──────────────────────┘   │
            │                   │
            ▼                   │
    [should_continue?]          │
         /        \             │
    continue    terminate       │
       │            \           │
       └─────────────┘          │
                                ▼
                              END
```

## Tool Interface Design

### Tool Registry Architecture

All tools implement a common interface for consistent invocation:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool description"""
        pass
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema for tool parameters"""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute tool with given parameters"""
        pass
    
    @property
    def timeout_seconds(self) -> int:
        """Maximum execution time"""
        return 10

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema
            }
            for tool in self._tools.values()
        ]
    
    async def invoke(self, name: str, parameters: Dict[str, Any]) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, error=f"Tool {name} not found")
        
        try:
            result = await asyncio.wait_for(
                tool.execute(parameters),
                timeout=tool.timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            return ToolResult(success=False, error=f"Tool {name} timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

### MVP Tool Specifications

**1. IP Reputation Lookup**
- **Name**: `ip_reputation_lookup`
- **Description**: Check if an IP address has known malicious activity
- **Parameters**:
  - `ip_address` (string, required): IP address to check
- **Returns**:
  - `reputation_score` (0-100): Higher = more suspicious
  - `threat_categories` (list): e.g., ["malware", "botnet"]
  - `last_seen` (datetime): When IP was last flagged
- **Implementation**: Simulated lookup with deterministic hash-based scoring for demo

**2. Privileged User Lookup**
- **Name**: `privileged_user_lookup`
- **Description**: Check if a user has privileged access rights
- **Parameters**:
  - `user_id` (string, required): User identifier
- **Returns**:
  - `is_privileged` (boolean): True if user has elevated privileges
  - `roles` (list): User's assigned roles
  - `last_privilege_change` (datetime): When privileges were last modified
- **Implementation**: Simulated lookup against in-memory user database

**3. Recent Related Alerts Lookup**
- **Name**: `recent_related_alerts_lookup`
- **Description**: Find similar alerts in recent history
- **Parameters**:
  - `alert_type` (string, required): Type of alert to match
  - `time_window_hours` (int, default=24): How far back to search
  - `source_ip` (string, optional): Filter by source IP
- **Returns**:
  - `related_alerts` (list): List of similar alerts with timestamps
  - `count` (int): Total number of related alerts
- **Implementation**: Query SecurityEvent table with filters

**4. Geo Anomaly Check**
- **Name**: `geo_anomaly_check`
- **Description**: Detect unusual geographic access patterns
- **Parameters**:
  - `user_id` (string, required): User identifier
  - `source_ip` (string, required): IP address of current access
- **Returns**:
  - `is_anomalous` (boolean): True if location is unusual for user
  - `expected_country` (string): User's typical location
  - `actual_country` (string): Location of source IP
  - `distance_km` (float): Distance between locations
- **Implementation**: Simulated geo-IP lookup with user baseline comparison

**5. Playbook Lookup**
- **Name**: `playbook_lookup`
- **Description**: Find recommended response playbooks for alert type
- **Parameters**:
  - `alert_type` (string, required): Type of security alert
  - `severity` (string, required): Alert severity level
- **Returns**:
  - `playbooks` (list): List of applicable playbooks with steps
  - `recommended_playbook_id` (string): Best match for this scenario
- **Implementation**: Static playbook database with keyword matching

**6. Action Simulator**
- **Name**: `action_simulator`
- **Description**: Simulate execution of a response action
- **Parameters**:
  - `action_type` (string, required): Type of action (block_ip, isolate_host, etc.)
  - `target` (string, required): Target of action (IP, hostname, etc.)
  - `dry_run` (boolean, default=true): If false, actually execute action
- **Returns**:
  - `simulated` (boolean): True if action was simulated
  - `would_succeed` (boolean): Predicted success of action
  - `impact_assessment` (string): Description of action impact
- **Implementation**: Always simulates by default; real execution requires config flag


## Database Schema Design

### Entity Relationship Diagram

```
┌─────────────────┐
│ SecurityEvent   │
│─────────────────│
│ id (PK)         │
│ source          │
│ event_type      │
│ severity        │
│ raw_payload     │
│ received_at     │
└─────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────┐
│ Investigation   │
│─────────────────│
│ id (PK)         │
│ alert_id (FK)   │
│ status          │
│ started_at      │
│ completed_at    │
│ final_risk_score│
│ step_count      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│InvestigationStep│
│─────────────────│
│ id (PK)         │
│ investigation_id│
│ step_number     │
│ step_type       │
│ timestamp       │
│ inputs          │
│ outputs         │
│ reasoning       │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│ ToolInvocation  │
│─────────────────│
│ id (PK)         │
│ step_id (FK)    │
│ tool_name       │
│ parameters      │
│ result          │
│ duration_ms     │
│ error           │
│ timestamp       │
└─────────────────┘

┌─────────────────┐
│ Finding         │
│─────────────────│
│ id (PK)         │
│ investigation_id│
│ title           │
│ description     │
│ priority        │
│ recommended_act │
│ status          │
│ created_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│ Feedback        │
│─────────────────│
│ id (PK)         │
│ finding_id (FK) │
│ rating          │
│ correctness     │
│ comment         │
│ submitted_at    │
│ submitted_by    │
└─────────────────┘
```

### Table Definitions

**SecurityEvent**
```sql
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(255) NOT NULL,           -- e.g., "cloudtrail", "siem", "simulated"
    event_type VARCHAR(255) NOT NULL,       -- e.g., "login_failure", "privilege_escalation"
    severity VARCHAR(50) DEFAULT 'unknown', -- "low", "medium", "high", "critical"
    raw_payload TEXT NOT NULL,              -- JSON string of original event
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_severity (severity),
    INDEX idx_received_at (received_at)
);
```

**Investigation**
```sql
CREATE TABLE investigations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'running',   -- "running", "completed", "failed", "max_steps_reached"
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    final_risk_score FLOAT NULL,            -- 0-100
    step_count INTEGER DEFAULT 0,
    FOREIGN KEY (alert_id) REFERENCES security_events(id) ON DELETE CASCADE,
    INDEX idx_alert_id (alert_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
);
```

**InvestigationStep**
```sql
CREATE TABLE investigation_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investigation_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    step_type VARCHAR(100) NOT NULL,        -- "initialize", "analyze_evidence", "select_tool", etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inputs TEXT,                             -- JSON string of node inputs
    outputs TEXT,                            -- JSON string of node outputs
    reasoning TEXT,                          -- Human-readable reasoning log
    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE,
    INDEX idx_investigation_id (investigation_id),
    INDEX idx_step_number (step_number)
);
```

**ToolInvocation**
```sql
CREATE TABLE tool_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    parameters TEXT NOT NULL,                -- JSON string of tool parameters
    result TEXT,                             -- JSON string of tool result
    duration_ms FLOAT NOT NULL,
    error TEXT NULL,                         -- Error message if tool failed
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (step_id) REFERENCES investigation_steps(id) ON DELETE CASCADE,
    INDEX idx_step_id (step_id),
    INDEX idx_tool_name (tool_name)
);
```

**Finding**
```sql
CREATE TABLE findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investigation_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium',  -- "low", "medium", "high", "critical"
    recommended_action VARCHAR(100),         -- "no_action_required", "monitor", "isolate_host", etc.
    status VARCHAR(50) DEFAULT 'open',      -- "open", "in_review", "resolved", "false_positive"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE,
    INDEX idx_investigation_id (investigation_id),
    INDEX idx_priority (priority),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**Feedback**
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),  -- 1-5 star rating
    correctness VARCHAR(50),                 -- "correct", "incorrect", "partially_correct"
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_by VARCHAR(255),               -- User identifier (future: auth integration)
    FOREIGN KEY (finding_id) REFERENCES findings(id) ON DELETE CASCADE,
    INDEX idx_finding_id (finding_id)
);
```

### SQLAlchemy Model Enhancements

The existing `models.py` needs to be extended with these additional models:

```python
class Investigation(Base):
    __tablename__ = "investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("security_events.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="running")
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
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    inputs = Column(Text)  # JSON
    outputs = Column(Text)  # JSON
    reasoning = Column(Text)
    
    # Relationships
    investigation = relationship("Investigation", back_populates="steps")
    tool_invocations = relationship("ToolInvocation", back_populates="step", cascade="all, delete-orphan")

class ToolInvocation(Base):
    __tablename__ = "tool_invocations"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("investigation_steps.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String, nullable=False)
    parameters = Column(Text, nullable=False)  # JSON
    result = Column(Text)  # JSON
    duration_ms = Column(Float, nullable=False)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    step = relationship("InvestigationStep", back_populates="tool_invocations")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer)  # 1-5
    correctness = Column(String)  # "correct", "incorrect", "partially_correct"
    comment = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    submitted_by = Column(String)
    
    # Relationships
    finding = relationship("Finding", back_populates="feedback_entries")
```

### PostgreSQL Compatibility Notes

To ensure smooth migration from SQLite to PostgreSQL:

1. **Use SQLAlchemy types**: Avoid database-specific types
2. **Autoincrement**: Use `autoincrement=True` (works on both)
3. **JSON columns**: Use SQLAlchemy's `JSON` type instead of `Text` for production
4. **Timestamps**: Use `DateTime` with `timezone=True` for PostgreSQL
5. **Connection strings**: Make database URL configurable via environment variable


## REST API Design

### API Endpoints

All endpoints are prefixed with `/api` and return JSON responses.

#### Alert Endpoints

**POST /api/alerts**
- **Purpose**: Ingest a new security alert and trigger investigation
- **Request Body**:
  ```json
  {
    "source": "cloudtrail",
    "event_type": "login_failure",
    "severity": "high",
    "raw_payload": {
      "user_id": "user123",
      "source_ip": "192.168.1.100",
      "timestamp": "2024-01-15T10:30:00Z",
      "details": {...}
    }
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "alert_id": 42,
    "investigation_id": 15,
    "status": "investigation_started",
    "message": "Alert ingested and investigation triggered"
  }
  ```
- **Validation**: Requires source, event_type, raw_payload
- **Side Effect**: Creates SecurityEvent record and launches LangGraph workflow

**GET /api/alerts**
- **Purpose**: List all alerts with pagination
- **Query Parameters**:
  - `page` (int, default=1): Page number
  - `page_size` (int, default=20): Items per page
  - `severity` (string, optional): Filter by severity
  - `event_type` (string, optional): Filter by event type
- **Response** (200 OK):
  ```json
  {
    "alerts": [
      {
        "id": 42,
        "source": "cloudtrail",
        "event_type": "login_failure",
        "severity": "high",
        "received_at": "2024-01-15T10:30:00Z",
        "has_investigation": true
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20
  }
  ```

**GET /api/alerts/{id}**
- **Purpose**: Retrieve a specific alert with full details
- **Response** (200 OK):
  ```json
  {
    "id": 42,
    "source": "cloudtrail",
    "event_type": "login_failure",
    "severity": "high",
    "raw_payload": {...},
    "received_at": "2024-01-15T10:30:00Z",
    "investigation_id": 15
  }
  ```
- **Response** (404 Not Found): If alert doesn't exist

#### Investigation Endpoints

**GET /api/investigations**
- **Purpose**: List all investigations with filtering
- **Query Parameters**:
  - `page` (int, default=1): Page number
  - `page_size` (int, default=20): Items per page
  - `status` (string, optional): Filter by status
  - `start_date` (ISO datetime, optional): Filter by start date
  - `end_date` (ISO datetime, optional): Filter by end date
  - `min_risk_score` (float, optional): Filter by minimum risk score
- **Response** (200 OK):
  ```json
  {
    "investigations": [
      {
        "id": 15,
        "alert_id": 42,
        "status": "completed",
        "started_at": "2024-01-15T10:30:05Z",
        "completed_at": "2024-01-15T10:30:45Z",
        "final_risk_score": 75.5,
        "step_count": 8
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
  ```

**GET /api/investigations/{id}**
- **Purpose**: Retrieve complete investigation details including all steps
- **Response** (200 OK):
  ```json
  {
    "id": 15,
    "alert_id": 42,
    "status": "completed",
    "started_at": "2024-01-15T10:30:05Z",
    "completed_at": "2024-01-15T10:30:45Z",
    "final_risk_score": 75.5,
    "step_count": 8,
    "alert": {
      "id": 42,
      "source": "cloudtrail",
      "event_type": "login_failure",
      "severity": "high"
    },
    "steps": [
      {
        "id": 100,
        "step_number": 1,
        "step_type": "initialize_investigation",
        "timestamp": "2024-01-15T10:30:05Z",
        "reasoning": "Initialized investigation for high-severity login failure"
      }
    ],
    "finding": {
      "id": 25,
      "title": "Suspicious login attempt from anomalous location",
      "priority": "high",
      "recommended_action": "block_ip"
    }
  }
  ```

**GET /api/investigations/{id}/trace**
- **Purpose**: Retrieve full execution trace with all tool invocations
- **Response** (200 OK):
  ```json
  {
    "investigation_id": 15,
    "alert_id": 42,
    "status": "completed",
    "started_at": "2024-01-15T10:30:05Z",
    "completed_at": "2024-01-15T10:30:45Z",
    "final_risk_score": 75.5,
    "trace": [
      {
        "step_number": 1,
        "step_type": "initialize_investigation",
        "timestamp": "2024-01-15T10:30:05Z",
        "inputs": {...},
        "outputs": {...},
        "reasoning": "Initialized investigation",
        "tool_invocations": []
      },
      {
        "step_number": 2,
        "step_type": "invoke_tool",
        "timestamp": "2024-01-15T10:30:10Z",
        "reasoning": "Checking IP reputation",
        "tool_invocations": [
          {
            "tool_name": "ip_reputation_lookup",
            "parameters": {"ip_address": "192.168.1.100"},
            "result": {"reputation_score": 85, "threat_categories": ["malware"]},
            "duration_ms": 150.5,
            "error": null
          }
        ]
      }
    ]
  }
  ```

#### Finding Endpoints

**GET /api/findings**
- **Purpose**: List all findings with filtering
- **Query Parameters**:
  - `page` (int, default=1): Page number
  - `page_size` (int, default=20): Items per page
  - `priority` (string, optional): Filter by priority
  - `status` (string, optional): Filter by status
  - `start_date` (ISO datetime, optional): Filter by creation date
- **Response** (200 OK):
  ```json
  {
    "findings": [
      {
        "id": 25,
        "investigation_id": 15,
        "title": "Suspicious login attempt from anomalous location",
        "description": "User user123 attempted login from IP 192.168.1.100...",
        "priority": "high",
        "recommended_action": "block_ip",
        "status": "open",
        "created_at": "2024-01-15T10:30:45Z"
      }
    ],
    "total": 30,
    "page": 1,
    "page_size": 20
  }
  ```

**GET /api/findings/{id}**
- **Purpose**: Retrieve a specific finding with full details
- **Response** (200 OK):
  ```json
  {
    "id": 25,
    "investigation_id": 15,
    "title": "Suspicious login attempt from anomalous location",
    "description": "User user123 attempted login from IP 192.168.1.100...",
    "priority": "high",
    "recommended_action": "block_ip",
    "status": "open",
    "created_at": "2024-01-15T10:30:45Z",
    "investigation": {
      "id": 15,
      "alert_id": 42,
      "final_risk_score": 75.5,
      "step_count": 8
    },
    "feedback_count": 2
  }
  ```

**POST /api/findings/{id}/feedback**
- **Purpose**: Submit human feedback on a finding
- **Request Body**:
  ```json
  {
    "rating": 4,
    "correctness": "correct",
    "comment": "Good catch, this was indeed a malicious attempt",
    "submitted_by": "analyst@example.com"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "feedback_id": 10,
    "finding_id": 25,
    "message": "Feedback submitted successfully"
  }
  ```

**PATCH /api/findings/{id}**
- **Purpose**: Update finding status (e.g., mark as resolved)
- **Request Body**:
  ```json
  {
    "status": "resolved"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": 25,
    "status": "resolved",
    "message": "Finding status updated"
  }
  ```

#### Feedback Endpoints

**GET /api/feedback/summary**
- **Purpose**: Get aggregated feedback metrics
- **Response** (200 OK):
  ```json
  {
    "total_feedback_count": 50,
    "average_rating": 4.2,
    "correctness_breakdown": {
      "correct": 35,
      "incorrect": 5,
      "partially_correct": 10
    },
    "accuracy_rate": 0.70
  }
  ```

#### Health Endpoint

**GET /health**
- **Purpose**: Service health check
- **Response** (200 OK):
  ```json
  {
    "status": "ok",
    "database": "connected",
    "version": "0.1.0"
  }
  ```

### API Error Responses

All error responses follow this format:

```json
{
  "error": "Error type",
  "message": "Human-readable error description",
  "details": {...}  // Optional additional context
}
```

**Common HTTP Status Codes**:
- 200 OK: Successful GET/PATCH
- 201 Created: Successful POST
- 400 Bad Request: Invalid request body or parameters
- 404 Not Found: Resource doesn't exist
- 422 Unprocessable Entity: Validation error
- 500 Internal Server Error: Server-side error
- 503 Service Unavailable: Database connection failure

### CORS Configuration

The backend enables CORS for the frontend origin:
- Development: `http://localhost:5173` (Vite default)
- Production: Configurable via environment variable


## Frontend Architecture

### Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS for utility-first styling
- **State Management**: React Context API + hooks (no Redux needed for MVP)
- **HTTP Client**: Fetch API with custom hooks
- **Routing**: React Router v6
- **Data Visualization**: Recharts for risk score charts (optional enhancement)

### Component Structure

```
frontend/
├── src/
│   ├── main.tsx                    # App entry point
│   ├── App.tsx                     # Root component with routing
│   ├── index.css                   # Tailwind imports
│   │
│   ├── components/                 # Reusable UI components
│   │   ├── Layout.tsx              # Main layout with navigation
│   │   ├── Header.tsx              # Top navigation bar
│   │   ├── Sidebar.tsx             # Side navigation (optional)
│   │   ├── Card.tsx                # Generic card component
│   │   ├── Badge.tsx               # Status/priority badges
│   │   ├── Button.tsx              # Styled button component
│   │   ├── LoadingSpinner.tsx     # Loading indicator
│   │   └── ErrorMessage.tsx        # Error display component
│   │
│   ├── pages/                      # Page-level components
│   │   ├── Dashboard.tsx           # Main dashboard with findings overview
│   │   ├── InvestigationList.tsx  # List of all investigations
│   │   ├── InvestigationDetail.tsx # Single investigation with trace
│   │   ├── FindingList.tsx         # List of all findings
│   │   ├── FindingDetail.tsx       # Single finding with feedback form
│   │   └── AlertList.tsx           # List of ingested alerts
│   │
│   ├── features/                   # Feature-specific components
│   │   ├── trace/
│   │   │   ├── TraceTimeline.tsx   # Main execution trace visualization
│   │   │   ├── TraceStep.tsx       # Individual step in timeline
│   │   │   ├── ToolInvocation.tsx  # Tool call display
│   │   │   └── RiskScoreChart.tsx  # Risk score evolution chart
│   │   │
│   │   ├── feedback/
│   │   │   ├── FeedbackForm.tsx    # Feedback submission form
│   │   │   └── FeedbackSummary.tsx # Aggregated feedback metrics
│   │   │
│   │   └── filters/
│   │       ├── StatusFilter.tsx    # Filter by status
│   │       ├── PriorityFilter.tsx  # Filter by priority
│   │       └── DateRangeFilter.tsx # Filter by date range
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── useApi.ts               # Generic API call hook
│   │   ├── useInvestigations.ts   # Investigation data fetching
│   │   ├── useFindings.ts          # Finding data fetching
│   │   ├── useAlerts.ts            # Alert data fetching
│   │   └── usePagination.ts        # Pagination logic
│   │
│   ├── services/                   # API service layer
│   │   ├── api.ts                  # Base API client configuration
│   │   ├── investigations.ts       # Investigation API calls
│   │   ├── findings.ts             # Finding API calls
│   │   ├── alerts.ts               # Alert API calls
│   │   └── feedback.ts             # Feedback API calls
│   │
│   ├── types/                      # TypeScript type definitions
│   │   ├── investigation.ts        # Investigation-related types
│   │   ├── finding.ts              # Finding-related types
│   │   ├── alert.ts                # Alert-related types
│   │   └── api.ts                  # API response types
│   │
│   └── utils/                      # Utility functions
│       ├── formatters.ts           # Date/time formatting
│       ├── constants.ts            # App constants
│       └── helpers.ts              # Helper functions
│
├── public/                         # Static assets
├── index.html                      # HTML entry point
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript configuration
├── vite.config.ts                  # Vite configuration
└── tailwind.config.js              # Tailwind configuration
```

### Key Components

#### TraceTimeline Component

The core visualization component for execution traces:

```typescript
interface TraceTimelineProps {
  investigationId: number;
}

// Displays:
// - Vertical timeline of investigation steps
// - Each step shows: timestamp, step type, reasoning
// - Tool invocations nested under their steps
// - Risk score updates highlighted
// - Color coding by step type
// - Expandable/collapsible steps for details
```

**Visual Design**:
- Vertical timeline with connecting lines
- Step cards with icons for step types
- Tool invocations indented with different background color
- Risk score badges showing progression
- Timestamps in relative format ("2 minutes ago")

#### InvestigationList Component

Displays all investigations with filtering:

```typescript
interface InvestigationListProps {
  filters?: {
    status?: string;
    startDate?: Date;
    endDate?: Date;
    minRiskScore?: number;
  };
}

// Features:
// - Sortable table/card view
// - Status badges (running, completed, failed)
// - Risk score indicators with color coding
// - Click to navigate to detail view
// - Pagination controls
```

#### FeedbackForm Component

Allows analysts to provide feedback on findings:

```typescript
interface FeedbackFormProps {
  findingId: number;
  onSubmit: (feedback: Feedback) => void;
}

// Fields:
// - Star rating (1-5)
// - Correctness radio buttons (correct/incorrect/partially_correct)
// - Free-text comment textarea
// - Submit button
```

### State Management Strategy

For the MVP, use React Context API for global state:

```typescript
// contexts/AppContext.tsx
interface AppState {
  investigations: Investigation[];
  findings: Finding[];
  filters: FilterState;
  loading: boolean;
  error: string | null;
}

// Contexts:
// - InvestigationContext: Investigation data and operations
// - FindingContext: Finding data and operations
// - FilterContext: Filter state across pages
```

### Routing Structure

```typescript
// App.tsx routes
<Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/alerts" element={<AlertList />} />
  <Route path="/investigations" element={<InvestigationList />} />
  <Route path="/investigations/:id" element={<InvestigationDetail />} />
  <Route path="/findings" element={<FindingList />} />
  <Route path="/findings/:id" element={<FindingDetail />} />
</Routes>
```

### API Service Layer

Centralized API calls with error handling:

```typescript
// services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiCall<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }
  
  return response.json();
}

// services/investigations.ts
export async function getInvestigations(params?: {
  page?: number;
  status?: string;
}): Promise<InvestigationListResponse> {
  const query = new URLSearchParams(params as any).toString();
  return apiCall(`/api/investigations?${query}`);
}

export async function getInvestigationTrace(
  id: number
): Promise<InvestigationTrace> {
  return apiCall(`/api/investigations/${id}/trace`);
}
```

### Styling Approach

Use Tailwind CSS with custom color palette for security context:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'risk-low': '#10b981',      // green
        'risk-medium': '#f59e0b',   // amber
        'risk-high': '#ef4444',     // red
        'risk-critical': '#7f1d1d', // dark red
        'status-running': '#3b82f6', // blue
        'status-completed': '#10b981', // green
        'status-failed': '#ef4444',   // red
      },
    },
  },
};
```

### Responsive Design

- Mobile-first approach with Tailwind breakpoints
- Collapsible sidebar on mobile
- Stacked cards on small screens
- Horizontal scrolling for tables on mobile


## Configuration Model

### Environment Variables

The backend uses environment variables for configuration:

```bash
# Database
DATABASE_URL=sqlite:///./data/sentinelops.db  # or postgresql://...

# Agent Configuration
MAX_INVESTIGATION_STEPS=15
TOOL_TIMEOUT_SECONDS=10
ENABLE_REAL_ACTIONS=false  # Set to true to execute real actions (not simulated)

# Risk Score Thresholds
RISK_THRESHOLD_LOW=20
RISK_THRESHOLD_MEDIUM=40
RISK_THRESHOLD_HIGH=60
RISK_THRESHOLD_CRITICAL=80

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json or text

# LangGraph Configuration
LANGCHAIN_API_KEY=  # Optional: for LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=sentinelops

# Tool Configuration
ENABLE_IP_REPUTATION_TOOL=true
ENABLE_PRIVILEGED_USER_TOOL=true
ENABLE_RELATED_ALERTS_TOOL=true
ENABLE_GEO_ANOMALY_TOOL=true
ENABLE_PLAYBOOK_TOOL=true
ENABLE_ACTION_SIMULATOR_TOOL=true

# External API Keys (for real tool implementations)
VIRUSTOTAL_API_KEY=  # For real IP reputation lookups
IPINFO_API_KEY=      # For real geo-IP lookups
```

### Configuration File

For more complex configuration, use a YAML config file:

```yaml
# config/default.yaml
agent:
  max_steps: 15
  step_timeout_seconds: 30
  enable_real_actions: false

risk_scoring:
  thresholds:
    low: 20
    medium: 40
    high: 60
    critical: 80
  
  weights:
    ip_reputation: 0.3
    privileged_user: 0.2
    geo_anomaly: 0.25
    related_alerts: 0.15
    playbook_match: 0.1

tools:
  ip_reputation_lookup:
    enabled: true
    timeout_seconds: 10
    use_simulation: true
  
  privileged_user_lookup:
    enabled: true
    timeout_seconds: 5
    use_simulation: true
  
  related_alerts_lookup:
    enabled: true
    timeout_seconds: 10
    lookback_hours: 24
  
  geo_anomaly_check:
    enabled: true
    timeout_seconds: 10
    use_simulation: true
    anomaly_distance_km: 500
  
  playbook_lookup:
    enabled: true
    timeout_seconds: 5
    playbook_directory: ./config/playbooks
  
  action_simulator:
    enabled: true
    timeout_seconds: 5
    always_simulate: true

database:
  url: sqlite:///./data/sentinelops.db
  echo: false  # Log SQL queries
  pool_size: 5
  max_overflow: 10

api:
  title: SentinelOps API
  version: 0.1.0
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - http://localhost:5173

logging:
  level: INFO
  format: json
  file: ./logs/sentinelops.log
```

### Configuration Loading

```python
# app/config.py
from pydantic import BaseSettings
from typing import List, Dict, Any
import yaml
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/sentinelops.db"
    
    # Agent
    max_investigation_steps: int = 15
    tool_timeout_seconds: int = 10
    enable_real_actions: bool = False
    
    # Risk Thresholds
    risk_threshold_low: int = 20
    risk_threshold_medium: int = 40
    risk_threshold_high: int = 60
    risk_threshold_critical: int = 80
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:5173"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Tool Configuration
    enable_ip_reputation_tool: bool = True
    enable_privileged_user_tool: bool = True
    enable_related_alerts_tool: bool = True
    enable_geo_anomaly_tool: bool = True
    enable_playbook_tool: bool = True
    enable_action_simulator_tool: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def load_config() -> Settings:
    """Load configuration from environment and config file"""
    settings = Settings()
    
    # Optionally load from YAML if exists
    config_path = os.getenv("CONFIG_FILE", "config/default.yaml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)
            # Merge YAML config with settings (env vars take precedence)
            # Implementation details omitted for brevity
    
    return settings

settings = load_config()
```

### Tool Registry Configuration

Tools are registered based on configuration:

```python
# app/tools/registry.py
from app.config import settings
from app.tools import (
    IPReputationTool,
    PrivilegedUserTool,
    RelatedAlertsTool,
    GeoAnomalyTool,
    PlaybookTool,
    ActionSimulatorTool,
)

def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    
    if settings.enable_ip_reputation_tool:
        registry.register(IPReputationTool())
    
    if settings.enable_privileged_user_tool:
        registry.register(PrivilegedUserTool())
    
    if settings.enable_related_alerts_tool:
        registry.register(RelatedAlertsTool())
    
    if settings.enable_geo_anomaly_tool:
        registry.register(GeoAnomalyTool())
    
    if settings.enable_playbook_tool:
        registry.register(PlaybookTool())
    
    if settings.enable_action_simulator_tool:
        registry.register(ActionSimulatorTool())
    
    return registry
```

## Error Handling Strategy

### Error Categories

1. **Validation Errors**: Invalid input data (HTTP 400/422)
2. **Not Found Errors**: Resource doesn't exist (HTTP 404)
3. **Tool Execution Errors**: Tool fails during investigation
4. **Database Errors**: Database connection or query failures (HTTP 503)
5. **LangGraph Errors**: Agent workflow failures
6. **Timeout Errors**: Operations exceed time limits

### Error Handling Principles

1. **Fail Gracefully**: Never crash the entire service due to a single error
2. **Log Everything**: All errors logged with full context for debugging
3. **User-Friendly Messages**: Return clear error messages to frontend
4. **Audit Trail**: Record errors in execution trace for investigation failures
5. **Retry Logic**: Retry transient failures (database connections, external APIs)
6. **Circuit Breaker**: Disable failing tools temporarily to prevent cascading failures

### Implementation

**API Error Handler**:
```python
# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )
```

**Tool Error Handling**:
```python
# app/tools/registry.py
async def invoke_tool_safe(
    tool_name: str,
    parameters: Dict[str, Any],
    investigation_id: int
) -> ToolResult:
    """Invoke tool with comprehensive error handling"""
    try:
        tool = registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool {tool_name} not found or disabled"
            )
        
        result = await asyncio.wait_for(
            tool.execute(parameters),
            timeout=tool.timeout_seconds
        )
        return result
        
    except asyncio.TimeoutError:
        logger.warning(f"Tool {tool_name} timed out for investigation {investigation_id}")
        return ToolResult(
            success=False,
            error=f"Tool execution timed out after {tool.timeout_seconds}s"
        )
    
    except Exception as e:
        logger.error(
            f"Tool {tool_name} failed for investigation {investigation_id}: {e}",
            exc_info=True
        )
        return ToolResult(
            success=False,
            error=f"Tool execution failed: {str(e)}"
        )
```

**LangGraph Error Handling**:
```python
# app/agents/nodes.py
def invoke_tool_node(state: InvestigationState) -> Dict[str, Any]:
    """Node that invokes a tool and handles errors"""
    try:
        tool_result = await invoke_tool_safe(
            state["selected_tool"],
            state["tool_parameters"],
            state["investigation_id"]
        )
        
        if not tool_result.success:
            # Log error but continue investigation
            return {
                "errors": state["errors"] + [tool_result.error],
                "reasoning_log": state["reasoning_log"] + [
                    f"Tool {state['selected_tool']} failed: {tool_result.error}"
                ],
                "step_count": state["step_count"] + 1
            }
        
        # Success: add evidence
        return {
            "evidence": state["evidence"] + [tool_result.data],
            "tool_invocations": state["tool_invocations"] + [
                {
                    "tool_name": state["selected_tool"],
                    "parameters": state["tool_parameters"],
                    "result": tool_result.data,
                    "timestamp": datetime.utcnow(),
                    "duration_ms": tool_result.metadata.get("duration_ms", 0),
                    "error": None
                }
            ],
            "step_count": state["step_count"] + 1
        }
    
    except Exception as e:
        logger.error(f"Node execution failed: {e}", exc_info=True)
        return {
            "errors": state["errors"] + [str(e)],
            "status": "failed",
            "step_count": state["step_count"] + 1
        }
```

**Database Error Handling**:
```python
# app/services/investigation_service.py
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def save_investigation_step(
    db: Session,
    step_data: Dict[str, Any]
) -> InvestigationStep:
    """Save investigation step with retry logic"""
    try:
        step = InvestigationStep(**step_data)
        db.add(step)
        db.commit()
        db.refresh(step)
        return step
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error saving step: {e}")
        raise
```

### Frontend Error Handling

```typescript
// hooks/useApi.ts
export function useApi<T>(endpoint: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall<T>(endpoint);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('API error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return { data, loading, error, refetch: fetchData };
}

// components/ErrorMessage.tsx
export function ErrorMessage({ error }: { error: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center">
        <svg className="w-5 h-5 text-red-600 mr-2" /* ... */>
        <p className="text-red-800">{error}</p>
      </div>
    </div>
  );
}
```


## Implementation Order

To prioritize a working end-to-end MVP, follow this implementation sequence:

### Phase 1: Foundation (Days 1-2)
**Goal**: Basic infrastructure and database working

1. **Database Setup**
   - Extend `models.py` with Investigation, InvestigationStep, ToolInvocation, Feedback models
   - Create database migration/initialization script
   - Verify tables created in `data/sentinelops.db`
   - Write basic CRUD operations for each model

2. **Configuration System**
   - Implement `config.py` with Settings class
   - Create `.env.example` file with all configuration options
   - Add configuration validation on startup

3. **Basic API Endpoints**
   - Implement POST /api/alerts (without investigation trigger)
   - Implement GET /api/alerts and GET /api/alerts/{id}
   - Implement GET /health
   - Test with curl/Postman

**Milestone**: Can ingest alerts via API and retrieve them from database

### Phase 2: Tool Layer (Days 2-3)
**Goal**: All 6 tools implemented and testable

4. **Tool Registry Framework**
   - Implement `BaseTool` abstract class
   - Implement `ToolRegistry` with registration and invocation
   - Add timeout handling and error wrapping

5. **Implement MVP Tools** (simulated versions first)
   - IP reputation lookup (hash-based scoring)
   - Privileged user lookup (in-memory user database)
   - Recent related alerts lookup (database query)
   - Geo anomaly check (simulated geo-IP)
   - Playbook lookup (static playbook database)
   - Action simulator (always simulates)

6. **Tool Testing**
   - Unit tests for each tool
   - Test timeout handling
   - Test error cases

**Milestone**: Can invoke all 6 tools independently via registry

### Phase 3: LangGraph Agent (Days 3-5)
**Goal**: Autonomous investigation workflow working end-to-end

7. **State Definition**
   - Implement `InvestigationState` TypedDict in `agents/state.py`
   - Define state update helpers

8. **Node Implementation**
   - Implement all 8 nodes (initialize, analyze, select_tool, invoke_tool, update_risk, check_stopping, generate_finding, handle_error)
   - Start with simple logic, refine later
   - Add logging to each node

9. **Edge Implementation**
   - Implement conditional edge functions
   - Wire up the LangGraph StateGraph

10. **Trace Recording**
    - Implement `trace_recorder.py` service
    - Record each step to database as it executes
    - Record tool invocations with timing

11. **Risk Calculator**
    - Implement `risk_calculator.py` with scoring logic
    - Map alert severity to initial score
    - Update score based on evidence

12. **Investigation Service**
    - Implement `investigation_service.py` to orchestrate workflow
    - Connect alert ingestion to investigation trigger
    - Handle workflow errors gracefully

**Milestone**: Can ingest alert and see complete investigation trace in database

### Phase 4: API Completion (Day 5)
**Goal**: All API endpoints working

13. **Investigation Endpoints**
    - Implement GET /api/investigations with filtering
    - Implement GET /api/investigations/{id}
    - Implement GET /api/investigations/{id}/trace

14. **Finding Endpoints**
    - Implement GET /api/findings with filtering
    - Implement GET /api/findings/{id}
    - Implement POST /api/findings/{id}/feedback
    - Implement PATCH /api/findings/{id}

15. **Feedback Endpoints**
    - Implement GET /api/feedback/summary

**Milestone**: All API endpoints functional and tested

### Phase 5: Frontend (Days 6-7)
**Goal**: UI for visualizing investigations

16. **Project Setup**
    - Initialize Vite + React + TypeScript project
    - Configure Tailwind CSS
    - Set up React Router

17. **API Service Layer**
    - Implement API client with error handling
    - Create custom hooks for data fetching

18. **Core Components**
    - Layout, Header, Card, Badge, Button components
    - LoadingSpinner, ErrorMessage components

19. **Investigation List Page**
    - Display all investigations in table/card view
    - Add status and risk score badges
    - Add filtering by status
    - Add pagination

20. **Investigation Detail Page**
    - Fetch investigation trace
    - Implement TraceTimeline component
    - Display steps chronologically
    - Show tool invocations nested under steps
    - Display risk score evolution

21. **Finding Pages**
    - Finding list page with filtering
    - Finding detail page
    - Feedback form component

**Milestone**: Can visualize complete investigation traces in browser

### Phase 6: Polish and Testing (Day 8)
**Goal**: Hackathon-ready demo

22. **Integration Testing**
    - End-to-end test: ingest alert → investigation → finding → feedback
    - Test error scenarios
    - Test with multiple concurrent investigations

23. **Sample Data**
    - Create seed script with realistic sample investigations
    - Generate variety of alert types and severities
    - Populate feedback data

24. **Documentation**
    - Update README with setup instructions
    - Document API endpoints
    - Add architecture diagram
    - Create demo script

25. **Demo Preparation**
    - Prepare sample alerts for live demo
    - Test Docker Compose setup
    - Verify frontend/backend integration
    - Practice demo flow

**Milestone**: Fully functional demo-ready system

### Optional Enhancements (If Time Permits)

- Real-time investigation updates (WebSocket)
- Risk score visualization chart
- Export investigation trace as JSON/PDF
- Advanced filtering and search
- Dark mode UI
- Real tool implementations (VirusTotal, IPInfo APIs)

### Development Tips

1. **Start Simple**: Get basic flow working before adding complexity
2. **Test Incrementally**: Test each phase before moving to next
3. **Use Docker Compose**: Keep backend and frontend running together
4. **Mock Data**: Use simulated tools and sample data for rapid iteration
5. **Log Everything**: Verbose logging helps debug LangGraph workflow
6. **Commit Often**: Commit after each working milestone


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Valid Alert Ingestion Round Trip

For any valid alert with required fields (source, event_type, severity, raw_payload), when the alert is posted to /api/alerts, then retrieving it by the returned ID should return an alert with the same field values.

**Validates: Requirements 1.1, 1.2**

### Property 2: Invalid Alert Rejection

For any alert missing required fields or containing invalid data types, when posted to /api/alerts, then the API should return HTTP 400 status with a descriptive error message.

**Validates: Requirements 1.3**

### Property 3: Alert ID Uniqueness

For any set of alerts ingested into the system, all alert IDs should be unique.

**Validates: Requirements 1.4**

### Property 4: Investigation Trigger on Alert Ingestion

For any valid alert successfully ingested, an Investigation record should be created with a unique investigation_id and status="running", and the investigation should reference the alert_id.

**Validates: Requirements 1.5, 2.1**

### Property 5: Investigation Step Limit Enforcement

For any investigation, the step_count should never exceed the configured max_steps limit (default 15), and when the limit is reached, the investigation status should be set to "max_steps_reached".

**Validates: Requirements 2.7**

### Property 6: Investigation State Persistence

For any investigation, all state fields (evidence, tool_invocations, risk_score_history, reasoning_log) should be persisted across steps and retrievable from the database.

**Validates: Requirements 2.3**

### Property 7: Tool Invocation Recording

For any tool invocation during an investigation, there should be a corresponding ToolInvocation record in the database containing tool_name, parameters, result, duration_ms, and timestamp.

**Validates: Requirements 3.5, 6.4**

### Property 8: Tool Error Handling

For any tool that fails or times out during execution, the tool invocation should return a ToolResult with success=false and an error message, and the investigation should continue rather than fail completely.

**Validates: Requirements 3.4, 3.6, 12.1**

### Property 9: Risk Score Bounds

For any investigation at any step, all risk scores (initial and updated) should be numerical values in the range [0, 100].

**Validates: Requirements 4.4**

### Property 10: Risk Score Update Recording

For any risk score update during an investigation, there should be a record in the risk_score_history containing old_score, new_score, justification, and timestamp.

**Validates: Requirements 4.3, 6.5**

### Property 11: Risk Score to Priority Mapping

For any completed investigation with a final_risk_score, the Finding priority should be deterministically mapped based on configured thresholds: 0-20 → low, 21-40 → medium, 41-60 → high, 61-100 → critical.

**Validates: Requirements 4.5**

### Property 12: Critical Risk Escalation

For any investigation where the risk_score crosses the critical threshold (default 80) during execution, the investigation should be marked for escalation and the next_action should be set to "escalate".

**Validates: Requirements 4.6**

### Property 13: Finding Generation on Investigation Completion

For any investigation that reaches status="completed" or status="max_steps_reached", a Finding record should be created containing title, description, priority, recommended_action, and a reference to the investigation_id.

**Validates: Requirements 5.1, 5.3**

### Property 14: Action Simulation by Default

For any investigation where enable_real_actions configuration is false (default), all selected actions should be simulated and recorded as recommendations rather than executed.

**Validates: Requirements 5.5, 5.6**

### Property 15: Complete Execution Trace Storage

For any investigation, the database should contain a complete execution trace including: Investigation record, all InvestigationStep records ordered by step_number, all ToolInvocation records linked to steps, and a Finding record.

**Validates: Requirements 6.1, 6.2, 6.3**

### Property 16: Trace Immutability After Completion

For any investigation with status="completed" or status="failed", no modifications should be allowed to the Investigation, InvestigationStep, or ToolInvocation records associated with that investigation.

**Validates: Requirements 6.6**

### Property 17: Foreign Key Referential Integrity

For any Investigation record, the alert_id must reference an existing SecurityEvent. For any InvestigationStep, the investigation_id must reference an existing Investigation. For any ToolInvocation, the step_id must reference an existing InvestigationStep. For any Finding, the investigation_id must reference an existing Investigation. Deleting a parent record should cascade to children.

**Validates: Requirements 7.7**

### Property 18: API Pagination Consistency

For any paginated API endpoint (alerts, investigations, findings), the sum of items across all pages should equal the total count, and no items should be duplicated or missing across pages.

**Validates: Requirements 8.2**

### Property 19: API Filter Correctness

For any filtered API request (investigations by status, findings by priority, etc.), all returned items should match the filter criteria, and no items matching the criteria should be excluded.

**Validates: Requirements 8.4, 8.7**

### Property 20: Feedback Persistence

For any feedback submitted via POST /api/findings/{id}/feedback, a Feedback record should be created in the database linked to the finding_id, containing rating, correctness, comment, and submitted_at timestamp.

**Validates: Requirements 10.4**

### Property 21: Feedback Metrics Calculation

For any set of feedback records, the calculated metrics (average_rating, correct_rate, incorrect_rate) should accurately reflect the aggregated feedback data.

**Validates: Requirements 10.6**

### Property 22: Tool Registry Configuration

For any tool with enabled=false in configuration, that tool should not appear in the tool registry, and the Triage_Agent should not attempt to invoke it during investigations.

**Validates: Requirements 11.3, 11.5**

### Property 23: Configuration Effect on Behavior

For any configurable parameter (max_steps, tool_timeout, risk_thresholds), changing the configuration value should deterministically affect system behavior according to the new value.

**Validates: Requirements 11.2**

### Property 24: Investigation Error Recovery

For any investigation that encounters an error during workflow execution, the investigation status should be set to "failed", the error should be recorded in the errors list, and the error should be stored in the execution trace.

**Validates: Requirements 2.8, 12.2**

### Property 25: API Error Response Format

For any API request that results in an error (validation, not found, server error), the response should contain a JSON object with "error" and "message" fields, and an appropriate HTTP status code (400, 404, 500, 503).

**Validates: Requirements 8.11**

### Property 26: Investigation Performance Bound

For any investigation with 5 or fewer tool invocations, the total investigation duration (completed_at - started_at) should be less than 30 seconds under normal conditions.

**Validates: Requirements 13.1**

### Property 27: Frontend Investigation List Ordering

For any investigation list displayed in the frontend, investigations should be ordered chronologically by started_at timestamp (newest first by default), and filtering should preserve this ordering.

**Validates: Requirements 9.9**

### Property 28: Frontend Search Relevance

For any search query on investigations, all returned results should contain the search term in either the alert content, tool results, or finding description.

**Validates: Requirements 9.8**


## Testing Strategy

### Dual Testing Approach

SentinelOps employs both unit testing and property-based testing to ensure comprehensive correctness:

- **Unit Tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property Tests**: Verify universal properties across all inputs through randomization

Both approaches are complementary and necessary. Unit tests catch concrete bugs and verify specific scenarios, while property tests verify general correctness across a wide input space.

### Property-Based Testing

**Framework**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: autonomous-security-triage, Property {number}: {property_text}`

**Example Property Test**:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: autonomous-security-triage, Property 1: Valid Alert Ingestion Round Trip
@given(
    source=st.text(min_size=1, max_size=100),
    event_type=st.text(min_size=1, max_size=100),
    severity=st.sampled_from(["low", "medium", "high", "critical"]),
    raw_payload=st.dictionaries(st.text(), st.text())
)
@pytest.mark.property_test
def test_alert_ingestion_round_trip(source, event_type, severity, raw_payload):
    """For any valid alert, ingestion and retrieval should preserve field values"""
    # Create alert
    alert_data = {
        "source": source,
        "event_type": event_type,
        "severity": severity,
        "raw_payload": raw_payload
    }
    
    # POST to /api/alerts
    response = client.post("/api/alerts", json=alert_data)
    assert response.status_code == 201
    alert_id = response.json()["alert_id"]
    
    # GET from /api/alerts/{id}
    response = client.get(f"/api/alerts/{alert_id}")
    assert response.status_code == 200
    retrieved = response.json()
    
    # Verify fields match
    assert retrieved["source"] == source
    assert retrieved["event_type"] == event_type
    assert retrieved["severity"] == severity
    assert retrieved["raw_payload"] == raw_payload
```

### Unit Testing Strategy

**Framework**: Use `pytest` for Python unit testing

**Test Organization**:
```
tests/
├── unit/
│   ├── test_tools.py              # Individual tool tests
│   ├── test_risk_calculator.py    # Risk scoring logic tests
│   ├── test_models.py             # Database model tests
│   └── test_config.py             # Configuration loading tests
├── integration/
│   ├── test_api.py                # API endpoint tests
│   ├── test_investigation_flow.py # End-to-end investigation tests
│   └── test_trace_recording.py    # Trace persistence tests
└── property/
    ├── test_alert_properties.py   # Alert-related property tests
    ├── test_investigation_properties.py  # Investigation property tests
    └── test_api_properties.py     # API property tests
```

**Unit Test Examples**:

```python
# tests/unit/test_tools.py
def test_ip_reputation_lookup_malicious_ip():
    """Specific example: known malicious IP should return high reputation score"""
    tool = IPReputationTool()
    result = await tool.execute({"ip_address": "192.0.2.1"})
    
    assert result.success is True
    assert result.data["reputation_score"] > 70
    assert "malware" in result.data["threat_categories"]

def test_ip_reputation_lookup_timeout():
    """Edge case: tool should handle timeout gracefully"""
    tool = IPReputationTool()
    tool.timeout_seconds = 0.001  # Force timeout
    
    result = await tool.execute({"ip_address": "192.0.2.1"})
    
    assert result.success is False
    assert "timeout" in result.error.lower()

# tests/integration/test_investigation_flow.py
def test_complete_investigation_flow():
    """Integration test: alert ingestion through finding generation"""
    # Ingest alert
    alert_response = client.post("/api/alerts", json={
        "source": "cloudtrail",
        "event_type": "login_failure",
        "severity": "high",
        "raw_payload": {"user_id": "user123", "source_ip": "192.0.2.1"}
    })
    assert alert_response.status_code == 201
    investigation_id = alert_response.json()["investigation_id"]
    
    # Wait for investigation to complete (or poll status)
    time.sleep(5)
    
    # Verify investigation completed
    inv_response = client.get(f"/api/investigations/{investigation_id}")
    assert inv_response.status_code == 200
    investigation = inv_response.json()
    assert investigation["status"] in ["completed", "max_steps_reached"]
    assert investigation["step_count"] > 0
    assert investigation["final_risk_score"] is not None
    
    # Verify finding created
    assert investigation["finding"] is not None
    finding = investigation["finding"]
    assert finding["title"] is not None
    assert finding["recommended_action"] is not None
    
    # Verify trace recorded
    trace_response = client.get(f"/api/investigations/{investigation_id}/trace")
    assert trace_response.status_code == 200
    trace = trace_response.json()
    assert len(trace["trace"]) == investigation["step_count"]
```

### Test Data Generation

**Simulated Alert Generator**:
```python
# app/utils/test_data.py
import random
from typing import Dict, Any

def generate_random_alert() -> Dict[str, Any]:
    """Generate realistic random alert for testing"""
    sources = ["cloudtrail", "siem", "ids", "firewall"]
    event_types = ["login_failure", "privilege_escalation", "data_exfiltration", "malware_detected"]
    severities = ["low", "medium", "high", "critical"]
    
    return {
        "source": random.choice(sources),
        "event_type": random.choice(event_types),
        "severity": random.choice(severities),
        "raw_payload": {
            "user_id": f"user{random.randint(1, 1000)}",
            "source_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {"action": "login_attempt", "result": "failure"}
        }
    }
```

### Test Coverage Goals

- **Unit Test Coverage**: >80% for critical paths (tools, risk calculator, API endpoints)
- **Property Test Coverage**: All 28 correctness properties implemented as property tests
- **Integration Test Coverage**: At least 3 end-to-end scenarios (successful investigation, max steps reached, investigation failure)

### Continuous Testing

**Pre-commit Hooks**:
- Run unit tests before allowing commits
- Run linting (black, flake8, mypy)

**CI Pipeline** (if time permits):
- Run full test suite on push
- Run property tests with 100 iterations
- Generate coverage report

### Manual Testing Checklist

For hackathon demo preparation:

1. **Alert Ingestion**
   - [ ] POST valid alert returns 201 and triggers investigation
   - [ ] POST invalid alert returns 400 with error message
   - [ ] GET /api/alerts returns paginated list

2. **Investigation Execution**
   - [ ] Investigation completes within reasonable time
   - [ ] All tools are invoked correctly
   - [ ] Risk score updates throughout investigation
   - [ ] Investigation terminates at max_steps if needed

3. **Trace Visualization**
   - [ ] GET /api/investigations/{id}/trace returns complete trace
   - [ ] Frontend displays trace timeline correctly
   - [ ] Tool invocations are nested under steps
   - [ ] Risk score evolution is visible

4. **Finding and Feedback**
   - [ ] Finding is generated with correct priority
   - [ ] Recommended action matches risk score
   - [ ] Feedback can be submitted
   - [ ] Feedback metrics are calculated correctly

5. **Error Handling**
   - [ ] Tool failures don't crash investigation
   - [ ] Database errors return 503
   - [ ] Frontend displays error messages

6. **Configuration**
   - [ ] Changing max_steps affects investigation behavior
   - [ ] Disabling tools removes them from registry
   - [ ] enable_real_actions=false simulates actions

### Performance Testing

**Load Testing** (optional):
- Use `locust` to simulate concurrent alert ingestion
- Target: 10 concurrent investigations without degradation
- Monitor database connection pool usage

**Profiling** (if performance issues arise):
- Use `cProfile` to identify bottlenecks
- Monitor LangGraph node execution times
- Optimize database queries with EXPLAIN

