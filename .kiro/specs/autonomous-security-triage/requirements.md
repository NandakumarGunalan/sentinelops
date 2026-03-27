# Requirements Document

## Introduction

SentinelOps is a bounded autonomous security triage infrastructure platform that processes security alerts through an intelligent, multi-step investigation workflow. When an ML detector or simulated source raises a threat alert, a LangGraph-powered autonomous agent launches an investigation by calling specialized tools within defined boundaries, gathering evidence, dynamically updating risk assessments, selecting appropriate actions, and storing complete execution traces for auditability and continuous improvement.

This is infrastructure for bounded autonomous agents, not a chatbot interface. The agent operates within clear constraints: a fixed set of 6 investigation tools, defined step limits, and explicit stopping conditions. The system prioritizes transparency and auditability of all decisions and actions.

## Glossary

- **Triage_Agent**: The LangGraph-powered bounded autonomous agent that orchestrates multi-step security investigations within defined constraints
- **Alert**: A security event raised by an ML detector or simulated ML detector requiring investigation
- **Investigation**: A multi-step autonomous workflow that gathers evidence and assesses risk
- **Tool**: A specialized function the Triage_Agent can invoke to gather evidence or perform actions
- **Execution_Trace**: A complete, timestamped record of all agent steps, tool calls, and decisions
- **Risk_Score**: A numerical assessment of threat severity that can be updated during investigation
- **Action**: A response selected or simulated by the Triage_Agent based on investigation findings
- **Evidence**: Data gathered by tools during an investigation
- **Finding**: The final output of an investigation including risk assessment and recommended action
- **Feedback_Loop**: A mechanism for capturing human feedback to improve future triage decisions
- **Backend**: The FastAPI Python service that hosts the Triage_Agent and API
- **Frontend**: The React TypeScript UI that visualizes execution traces
- **Database**: SQLite or Postgres persistence layer for alerts, traces, and findings

## Requirements

### Requirement 1: Alert Ingestion

**User Story:** As a security platform, I want to ingest alerts from ML detectors or simulated ML detectors, so that the Triage_Agent can begin autonomous investigations.

#### Acceptance Criteria

1. WHEN an alert is received via REST API, THE Backend SHALL validate the alert schema and store it in the Database
2. THE Backend SHALL accept alerts containing source identifier, event type, severity, timestamp, and raw payload
3. WHEN an invalid alert is received, THE Backend SHALL return a descriptive error with HTTP 400 status
4. THE Backend SHALL assign a unique identifier to each ingested alert
5. WHEN an alert is successfully ingested, THE Backend SHALL trigger the Triage_Agent to begin an investigation
6. THE Backend SHALL support alerts from both real ML detectors and simulated ML detectors for demonstration purposes

### Requirement 2: Bounded LangGraph Investigation Workflow

**User Story:** As a security operations team, I want the Triage_Agent to conduct multi-step investigations autonomously within defined boundaries, so that threats are analyzed systematically without manual intervention.

#### Acceptance Criteria

1. WHEN an alert is ingested, THE Triage_Agent SHALL initialize a new investigation with a unique investigation identifier
2. THE Triage_Agent SHALL execute a LangGraph workflow consisting of multiple decision nodes and tool-calling nodes
3. WHILE an investigation is active, THE Triage_Agent SHALL maintain investigation state across multiple steps
4. THE Triage_Agent SHALL determine which tools to call based on alert content and previous investigation steps
5. WHEN a tool returns evidence, THE Triage_Agent SHALL incorporate that evidence into its decision-making process
6. THE Triage_Agent SHALL terminate an investigation when sufficient evidence is gathered, a maximum step limit is reached, or explicit stopping conditions are met
7. THE Triage_Agent SHALL enforce a maximum step limit of 15 steps per investigation to ensure bounded execution
8. IF an investigation fails due to an error, THEN THE Triage_Agent SHALL log the error and mark the investigation as failed

### Requirement 3: MVP Tool Layer

**User Story:** As the Triage_Agent, I want to call a focused set of specialized tools to gather evidence, so that I can make informed triage decisions within a bounded investigation scope.

#### Acceptance Criteria

1. THE Backend SHALL provide a registry of exactly 6 available tools that the Triage_Agent can invoke
2. WHEN the Triage_Agent calls a tool, THE Backend SHALL execute the tool with provided parameters and return results
3. THE Backend SHALL implement these 6 specialized tools: IP reputation lookup, privileged user lookup, recent related alerts lookup, geo anomaly check, playbook lookup, and action simulator
4. WHEN a tool execution fails, THE Backend SHALL return an error message to the Triage_Agent
5. THE Backend SHALL record every tool invocation with parameters and results in the Execution_Trace
6. WHERE a tool requires external API calls, THE Backend SHALL handle timeouts gracefully
7. THE Backend SHALL support both real tool implementations and simulated tool responses for demonstration purposes

### Requirement 4: Dynamic Risk Assessment

**User Story:** As a security analyst, I want the Triage_Agent to update risk scores dynamically during investigations, so that threat severity reflects accumulated evidence.

#### Acceptance Criteria

1. WHEN an investigation begins, THE Triage_Agent SHALL initialize a Risk_Score based on the alert severity
2. WHEN new evidence is gathered, THE Triage_Agent SHALL recalculate the Risk_Score incorporating the new evidence
3. THE Triage_Agent SHALL store each Risk_Score update with a timestamp and justification in the Execution_Trace
4. THE Risk_Score SHALL be a numerical value between 0 and 100 with defined severity thresholds
5. THE Triage_Agent SHALL use the final Risk_Score to determine the priority of the Finding
6. WHEN the Risk_Score crosses a critical threshold during investigation, THE Triage_Agent SHALL escalate the investigation priority

### Requirement 5: Action Selection

**User Story:** As a security operations team, I want the Triage_Agent to select or simulate appropriate response actions, so that threats are addressed systematically.

#### Acceptance Criteria

1. WHEN an investigation concludes, THE Triage_Agent SHALL select an action based on the final Risk_Score and evidence
2. THE Triage_Agent SHALL support action types including: no action required, monitor, isolate host, block IP, escalate to human, and trigger automated response
3. THE Triage_Agent SHALL record the selected action with justification in the Finding
4. WHERE automated action execution is enabled, THE Triage_Agent SHALL execute the selected action and record the outcome
5. WHERE automated action execution is disabled, THE Triage_Agent SHALL simulate the action and record it as a recommendation
6. THE Triage_Agent SHALL never execute destructive actions without explicit configuration enabling such actions

### Requirement 6: Execution Trace Storage

**User Story:** As a security auditor, I want complete execution traces of all investigations stored permanently, so that I can audit agent decisions and improve the system.

#### Acceptance Criteria

1. THE Backend SHALL store a complete Execution_Trace for every investigation in the Database
2. THE Execution_Trace SHALL include investigation identifier, alert identifier, start time, end time, status, and final Finding
3. THE Execution_Trace SHALL record every agent step with timestamp, step type, inputs, outputs, and reasoning
4. THE Execution_Trace SHALL record every tool invocation with tool name, parameters, results, and execution duration
5. THE Execution_Trace SHALL record every Risk_Score update with old value, new value, and justification
6. THE Execution_Trace SHALL be immutable once an investigation is complete
7. THE Backend SHALL support querying Execution_Traces by alert identifier, time range, risk score, and investigation status

### Requirement 7: Database Persistence Model

**User Story:** As a platform operator, I want all alerts, investigations, and findings persisted reliably, so that no data is lost.

#### Acceptance Criteria

1. THE Backend SHALL use SQLite for development and support Postgres for production environments
2. THE Database SHALL store security events with fields: id, source, event_type, severity, raw_payload, received_at
3. THE Database SHALL store investigations with fields: id, alert_id, status, started_at, completed_at, final_risk_score, step_count
4. THE Database SHALL store investigation steps with fields: id, investigation_id, step_number, step_type, timestamp, inputs, outputs, reasoning
5. THE Database SHALL store tool invocations with fields: id, step_id, tool_name, parameters, results, duration_ms
6. THE Database SHALL store findings with fields: id, investigation_id, title, description, priority, recommended_action, status, created_at
7. THE Database SHALL enforce foreign key constraints to maintain referential integrity
8. THE Backend SHALL create all required tables on application startup
9. THE Database SHALL write SQLite files to the data/ directory for local development

### Requirement 8: REST API Surface

**User Story:** As a frontend developer, I want a well-defined REST API, so that I can build UI features to visualize investigations and findings.

#### Acceptance Criteria

1. THE Backend SHALL expose a POST /api/alerts endpoint to ingest new alerts
2. THE Backend SHALL expose a GET /api/alerts endpoint to list all alerts with pagination
3. THE Backend SHALL expose a GET /api/alerts/{id} endpoint to retrieve a specific alert
4. THE Backend SHALL expose a GET /api/investigations endpoint to list all investigations with filtering by status and time range
5. THE Backend SHALL expose a GET /api/investigations/{id} endpoint to retrieve a complete investigation including all steps and tool calls
6. THE Backend SHALL expose a GET /api/investigations/{id}/trace endpoint to retrieve the full Execution_Trace in a structured format
7. THE Backend SHALL expose a GET /api/findings endpoint to list all findings with filtering by priority and status
8. THE Backend SHALL expose a GET /api/findings/{id} endpoint to retrieve a specific finding
9. THE Backend SHALL expose a POST /api/findings/{id}/feedback endpoint to submit human feedback on a finding
10. THE Backend SHALL expose a GET /health endpoint that returns service status
11. THE Backend SHALL return appropriate HTTP status codes and error messages for all endpoints
12. THE Backend SHALL support CORS for the Frontend origin

### Requirement 9: Frontend Execution Trace Visualization

**User Story:** As a security analyst, I want to visualize investigation execution traces in the UI, so that I can understand how the Triage_Agent reached its conclusions.

#### Acceptance Criteria

1. THE Frontend SHALL display a list of all investigations with status, start time, and final risk score
2. WHEN a user selects an investigation, THE Frontend SHALL display the complete Execution_Trace in a timeline view
3. THE Frontend SHALL display each investigation step with timestamp, step type, and reasoning
4. THE Frontend SHALL display each tool invocation with tool name, parameters, results, and duration
5. THE Frontend SHALL display Risk_Score updates with old value, new value, and justification
6. THE Frontend SHALL highlight the final Finding with recommended action
7. THE Frontend SHALL support filtering investigations by status, time range, and risk score
8. THE Frontend SHALL support searching investigations by alert content or tool results
9. THE Frontend SHALL display investigation steps in chronological order with visual indicators for step types

### Requirement 10: Feedback and Improvement Loop

**User Story:** As a security operations team, I want to provide feedback on agent decisions, so that the system can learn and improve over time.

#### Acceptance Criteria

1. THE Frontend SHALL provide a feedback interface on each Finding allowing users to rate the triage decision
2. THE Frontend SHALL allow users to mark a Finding as correct, incorrect, or partially correct
3. THE Frontend SHALL allow users to provide free-text comments explaining their feedback
4. WHEN feedback is submitted, THE Backend SHALL store the feedback linked to the Finding in the Database
5. THE Backend SHALL expose a GET /api/feedback/summary endpoint that aggregates feedback metrics
6. THE Backend SHALL calculate accuracy metrics based on feedback: correct rate, incorrect rate, and average rating
7. THE Backend SHALL support exporting feedback data for offline analysis and model retraining

### Requirement 11: Configuration and Tool Management

**User Story:** As a platform operator, I want to configure agent behavior and manage available tools, so that I can customize the system for different environments.

#### Acceptance Criteria

1. THE Backend SHALL load configuration from environment variables and configuration files
2. THE Backend SHALL support configuring maximum investigation steps, tool timeout durations, and risk score thresholds
3. THE Backend SHALL support enabling or disabling individual tools via configuration
4. THE Backend SHALL support configuring whether automated actions are executed or simulated
5. WHERE a tool is disabled, THE Triage_Agent SHALL not attempt to call that tool
6. THE Backend SHALL validate configuration on startup and fail fast with descriptive errors if configuration is invalid

### Requirement 12: Error Handling and Resilience

**User Story:** As a platform operator, I want the system to handle errors gracefully, so that individual failures do not crash the entire service.

#### Acceptance Criteria

1. WHEN a tool invocation fails, THE Triage_Agent SHALL log the error and continue the investigation with available evidence
2. WHEN the LangGraph workflow encounters an error, THE Backend SHALL mark the investigation as failed and store the error in the Execution_Trace
3. IF the Database connection fails, THEN THE Backend SHALL return HTTP 503 status and log the error
4. THE Backend SHALL implement request timeouts to prevent indefinite blocking
5. THE Backend SHALL log all errors with sufficient context for debugging
6. THE Frontend SHALL display user-friendly error messages when API calls fail

### Requirement 13: Performance Requirements

**User Story:** As a platform operator, I want the system to process investigations efficiently, so that alert processing is responsive for demonstration purposes.

#### Acceptance Criteria

1. THE Backend SHALL complete a typical investigation with 5 tool calls within 30 seconds
2. THE Frontend SHALL load the investigation list page within 3 seconds for up to 100 investigations
3. THE Frontend SHALL render an Execution_Trace with 15 steps within 2 seconds
4. THE Database SHALL use indexes on alert_id and investigation_id fields to optimize common queries

### Requirement 14: Development and Testing Support

**User Story:** As a developer, I want testing and development tools, so that I can develop and debug the system efficiently during the hackathon.

#### Acceptance Criteria

1. THE Backend SHALL provide a simulated alert generator for testing purposes
2. THE Backend SHALL provide simulated tool implementations that return realistic test data
3. THE Backend SHALL support a development mode that enables verbose logging and debugging features
4. THE Backend SHALL include unit tests for critical tool implementations
5. THE Backend SHALL include at least one integration test for the complete investigation workflow
6. THE Backend SHALL provide a seed script to populate the Database with sample investigations for UI development

## Implementation Milestones

### Milestone 1: Core Infrastructure
- Database schema and models (SQLite in data/ directory)
- FastAPI application structure
- Basic REST API endpoints for alerts and findings
- Docker Compose setup for local development

### Milestone 2: MVP Tool Layer
- Tool registry and invocation framework
- All 6 MVP tool implementations (IP reputation, privileged user lookup, recent related alerts, geo anomaly check, playbook lookup, action simulator)
- Tool error handling and timeout logic

### Milestone 3: Bounded LangGraph Agent
- LangGraph workflow definition with step limits
- Investigation state management
- Tool calling integration
- Risk score calculation logic
- Stopping condition enforcement

### Milestone 4: Execution Trace Storage
- Trace data model using Database tables
- Complete trace recording during investigations
- Trace retrieval API endpoints

### Milestone 5: Frontend Visualization
- Investigation list view
- Execution trace timeline component
- Risk score visualization
- Finding detail view

### Milestone 6: Feedback Loop
- Feedback submission UI
- Feedback storage and retrieval
- Basic feedback metrics

### Milestone 7: Hackathon Polish
- Error handling for critical paths
- Sample data generation
- Basic integration test
- README documentation
