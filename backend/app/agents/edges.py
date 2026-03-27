import logging
from app.agents.state import InvestigationState

logger = logging.getLogger(__name__)


def should_continue_investigation(state: InvestigationState) -> str:
    """Determine if investigation should continue or terminate"""
    status = state.get("status", "running")
    next_action = state.get("next_action")
    
    # If status is not running, go to generate_finding
    if status != "running":
        logger.info(f"Investigation {state['investigation_id']} status is {status}. Routing to generate_finding.")
        return "generate_finding"
    
    # If next_action is conclude or escalate, go to generate_finding
    if next_action in ["conclude", "escalate"]:
        logger.info(f"Investigation {state['investigation_id']} next_action is {next_action}. Routing to generate_finding.")
        return "generate_finding"
    
    # Otherwise continue investigation
    logger.info(f"Investigation {state['investigation_id']} continuing. Routing to analyze_evidence.")
    return "analyze_evidence"


def should_call_tool(state: InvestigationState) -> str:
    """Determine if we should call a tool or conclude"""
    next_action = state.get("next_action")
    
    if next_action == "call_tool":
        logger.info(f"Investigation {state['investigation_id']} calling tool. Routing to select_tool.")
        return "select_tool"
    elif next_action in ["conclude", "escalate"]:
        logger.info(f"Investigation {state['investigation_id']} concluding. Routing to generate_finding.")
        return "generate_finding"
    else:
        # Default to conclude
        logger.info(f"Investigation {state['investigation_id']} defaulting to conclude. Routing to generate_finding.")
        return "generate_finding"


def has_errors(state: InvestigationState) -> str:
    """Check if investigation has critical errors"""
    errors = state.get("errors", [])
    
    # If more than 5 errors, route to error handler
    if len(errors) > 5:
        logger.error(f"Investigation {state['investigation_id']} has {len(errors)} errors. Routing to handle_error.")
        return "handle_error"
    
    # Otherwise continue normally
    return "continue"
