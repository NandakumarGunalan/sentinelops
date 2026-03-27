# Implementation Plan: Autonomous Security Triage - Backend MVP Foundation

## Overview

This implementation plan focuses on building the backend MVP foundation for the autonomous security triage system. The scope includes extending database models, implementing the tool framework with 6 deterministic mock tools, creating a minimal LangGraph agent skeleton, and exposing essential API endpoints. This is a hackathon-realistic implementation using SQLite, deterministic logic, and complete investigation trace persistence.

## Tasks

- [x] 1. Extend database models and configuration
  - [x] 1.1 Add new database models to models.py
    - Add Investigation, InvestigationStep, ToolInvocation, and Feedback models with relationships
    - Update SecurityEvent model to include investigation relationship
    - Update Finding model to reference investigation_id instead of event_id
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6_
  
  - [x] 1.2 Create configuration module
    - Create backend/app/config.py with environment variable loading
    - Support DATABASE_URL, MAX_INVESTIGATION_STEPS, TOOL_TIMEOUT_SECONDS, ENABLE_REAL_ACTIONS
    - Provide sensible defaults (max_steps=15, timeout=10s, real_actions=false)
    - _Requirements: 11.1, 11.2, 11.4_

- [x] 2. Implement tool framework
  - [x] 2.1 Create tool registry and base classes
    - Create backend/app/tools/registry.py with BaseTool, ToolResult, ToolRegistry classes
    - Implement tool registration, lookup, and invocation with timeout handling
    - _Requirements: 3.1, 3.2, 3.4, 3.6_
  
  - [x] 2.2 Implement IP reputation lookup tool
    - Create backend/app/tools/ip_reputation.py
    - Use deterministic hash-based scoring for demo (hash IP to get 0-100 score)
    - Return reputation_score, threat_categories, last_seen
    - _Requirements: 3.3_
  
  - [x] 2.3 Implement privileged user lookup tool
    - Create backend/app/tools/privileged_user.py
    - Use in-memory user database with deterministic lookups
    - Return is_privileged, roles, last_privilege_change
    - _Requirements: 3.3_
  
  - [x] 2.4 Implement recent related alerts lookup tool
    - Create backend/app/tools/related_alerts.py
    - Query SecurityEvent table with filters for alert_type, time_window, source_ip
    - Return related_alerts list and count
    - _Requirements: 3.3_
  
  - [x] 2.5 Implement geo anomaly check tool
    - Create backend/app/tools/geo_anomaly.py
    - Use simulated geo-IP lookup with user baseline comparison
    - Return is_anomalous, expected_country, actual_country, distance_km
    - _Requirements: 3.3_
  
  - [x] 2.6 Implement playbook lookup tool
    - Create backend/app/tools/playbook.py
    - Use static playbook database with keyword matching
    - Return playbooks list and recommended_playbook_id
    - _Requirements: 3.3_
  
  - [x] 2.7 Implement action simulator tool
    - Create backend/app/tools/action_simulator.py
    - Always simulate by default, check ENABLE_REAL_ACTIONS config
    - Return simulated, would_succeed, impact_assessment
    - _Requirements: 3.3, 5.4, 5.5_

- [ ] 3. Checkpoint - Verify tool framework
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement LangGraph agent skeleton
  - [x] 4.1 Create investigation state definition
    - Create backend/app/agents/state.py with InvestigationState, ToolInvocationRecord, RiskScoreUpdate TypedDicts
    - _Requirements: 2.3_
  
  - [x] 4.2 Implement LangGraph node functions
    - Create backend/app/agents/nodes.py with all 8 node functions
    - Implement initialize_investigation, analyze_evidence, select_tool, invoke_tool, update_risk_score, check_stopping_conditions, generate_finding, handle_error
    - Use deterministic logic for tool selection and risk scoring
    - _Requirements: 2.2, 2.4, 2.5, 4.1, 4.2, 4.3, 5.1, 5.2_
  
  - [x] 4.3 Implement conditional edge functions
    - Create backend/app/agents/edges.py with should_continue_investigation, should_call_tool, has_errors
    - _Requirements: 2.6, 2.7_
  
  - [x] 4.4 Create main LangGraph StateGraph
    - Create backend/app/agents/triage_agent.py with complete workflow definition
    - Wire all nodes and conditional edges together
    - Add LangGraph dependency to requirements.txt
    - _Requirements: 2.1, 2.2_

- [x] 5. Implement trace persistence service
  - [x] 5.1 Create trace recorder service
    - Create backend/app/services/trace_recorder.py
    - Implement functions to persist investigation steps, tool invocations, and risk score updates to database
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 5.2 Create investigation orchestration service
    - Create backend/app/services/investigation_service.py
    - Implement function to launch LangGraph workflow and persist complete trace
    - _Requirements: 2.1, 6.1_
  
  - [x] 5.3 Create risk calculator service
    - Create backend/app/services/risk_calculator.py
    - Implement deterministic risk score calculation based on evidence
    - _Requirements: 4.1, 4.2, 4.4, 4.5_

- [ ] 6. Checkpoint - Verify agent and persistence
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement API endpoints
  - [x] 7.1 Update POST /api/alerts endpoint
    - Modify backend/app/api/events.py (currently named alerts.py in design)
    - Trigger investigation workflow after alert ingestion
    - _Requirements: 1.1, 1.5, 8.1_
  
  - [x] 7.2 Create investigations API endpoints
    - Create backend/app/api/investigations.py
    - Implement GET /api/investigations/{id}/trace endpoint to return complete execution trace
    - _Requirements: 8.6_
  
  - [x] 7.3 Update findings API endpoints
    - Modify backend/app/api/findings.py to work with investigation_id
    - Ensure Finding creation happens at end of investigation workflow
    - _Requirements: 8.8_
  
  - [x] 7.4 Wire new API routes into main.py
    - Import and include investigations router
    - Ensure all routes are registered
    - _Requirements: 8.1, 8.6, 8.10_

- [x] 8. Add Pydantic schemas for new endpoints
  - [x] 8.1 Create investigation schemas
    - Add schemas to backend/app/schemas.py for InvestigationResponse, InvestigationTraceResponse, InvestigationStepResponse, ToolInvocationResponse
    - _Requirements: 8.6_

- [ ] 9. Final integration and testing
  - [ ] 9.1 Test complete alert-to-finding flow
    - Submit test alert via POST /api/alerts
    - Verify investigation runs and completes
    - Verify trace is persisted correctly
    - Verify finding is created
    - _Requirements: 1.1, 2.1, 6.1, 8.1_
  
  - [ ] 9.2 Test investigation trace retrieval
    - Call GET /api/investigations/{id}/trace
    - Verify all steps, tool invocations, and risk updates are returned
    - _Requirements: 6.7, 8.6_

- [ ] 10. Final checkpoint - End-to-end verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- This implementation focuses exclusively on the backend MVP foundation
- All tools use deterministic logic for hackathon demonstration
- LangGraph agent uses simple rule-based logic, not complex LLM behavior
- SQLite database persists to data/sentinelops.db
- Frontend implementation is out of scope for this task list
- Testing tasks are integrated into checkpoint tasks for faster MVP delivery
