import logging
from langgraph.graph import StateGraph, END
from app.agents.state import InvestigationState
from app.agents import nodes
from app.agents import edges

logger = logging.getLogger(__name__)


def create_triage_agent() -> StateGraph:
    """Create the LangGraph StateGraph for autonomous triage"""
    
    # Create the graph
    workflow = StateGraph(InvestigationState)
    
    # Add nodes
    workflow.add_node("initialize_investigation", nodes.initialize_investigation)
    workflow.add_node("analyze_evidence", nodes.analyze_evidence)
    workflow.add_node("select_tool", nodes.select_tool)
    workflow.add_node("invoke_tool", nodes.invoke_tool)
    workflow.add_node("update_risk_score", nodes.update_risk_score)
    workflow.add_node("check_stopping_conditions", nodes.check_stopping_conditions)
    workflow.add_node("generate_finding", nodes.generate_finding)
    workflow.add_node("handle_error", nodes.handle_error)
    
    # Set entry point
    workflow.set_entry_point("initialize_investigation")
    
    # Add edges
    # initialize_investigation -> analyze_evidence
    workflow.add_edge("initialize_investigation", "analyze_evidence")
    
    # analyze_evidence -> (select_tool OR generate_finding)
    workflow.add_conditional_edges(
        "analyze_evidence",
        edges.should_call_tool,
        {
            "select_tool": "select_tool",
            "generate_finding": "generate_finding"
        }
    )
    
    # select_tool -> invoke_tool
    workflow.add_edge("select_tool", "invoke_tool")
    
    # invoke_tool -> update_risk_score
    workflow.add_edge("invoke_tool", "update_risk_score")
    
    # update_risk_score -> check_stopping_conditions
    workflow.add_edge("update_risk_score", "check_stopping_conditions")
    
    # check_stopping_conditions -> (analyze_evidence OR generate_finding)
    workflow.add_conditional_edges(
        "check_stopping_conditions",
        edges.should_continue_investigation,
        {
            "analyze_evidence": "analyze_evidence",
            "generate_finding": "generate_finding"
        }
    )
    
    # generate_finding -> END
    workflow.add_edge("generate_finding", END)
    
    # handle_error -> END
    workflow.add_edge("handle_error", END)
    
    logger.info("Triage agent workflow created successfully")
    
    return workflow.compile()


# Global compiled workflow
triage_workflow = create_triage_agent()
