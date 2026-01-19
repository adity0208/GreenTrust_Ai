"""
LangGraph workflow orchestration for multi-agent ESG audit.
Defines the agent execution graph and state transitions with human review logic.
"""

from langgraph.graph import StateGraph, END
from .state import AuditState
from .extraction_agent import extraction_agent
from .verification_agent import verification_agent
from .compliance_agent import compliance_agent
import logging

logger = logging.getLogger(__name__)


def should_continue_after_extraction(state: AuditState) -> str:
    """Conditional edge: decide whether to continue after extraction."""
    if state.workflow_status == "extraction_failed":
        logger.warning("Extraction failed, skipping to end")
        return "end"
    return "verification"


def should_continue_after_verification(state: AuditState) -> str:
    """Conditional edge: decide whether to continue after verification."""
    if state.workflow_status == "verification_failed":
        logger.warning("Verification failed, proceeding to compliance with limited data")
    return "compliance"


def should_require_human_review(state: AuditState) -> str:
    """Conditional edge: decide if human review is needed after compliance."""
    if state.requires_human_review and not state.human_review_completed:
        logger.info(f"Flagging for human review: {state.human_review_reason}")
        return "human_review"
    return "end"


def human_review_node(state: AuditState) -> AuditState:
    """
    Human Review node - simulates human reviewer decision.
    In production, this would pause the workflow and wait for human input.
    """
    logger.info(f"Human review required: {state.human_review_reason}")
    
    # Log reasoning
    from .state import ReasoningStep
    from datetime import datetime
    
    state.reasoning_history.append(ReasoningStep(
        agent="human_review",
        timestamp=datetime.now(),
        action="review_flagged",
        reasoning=f"Invoice flagged for human review: {state.human_review_reason}",
        result="PENDING_REVIEW"
    ))
    
    # In production with HITL:
    # 1. Workflow pauses before this node (interrupt_before)
    # 2. Human updates state.human_review_decision via UI
    # 3. Workflow resumes and executes this node
    
    decision = state.human_review_decision
    if not decision:
        # Fallback if no decision provided (shouldn't happen with proper HITL)
        logger.warning("No human decision found in state, defaulting to REJECT")
        decision = "reject"
    
    state.human_review_completed = True
    state.workflow_status = f"human_review_{decision.lower()}"
    
    state.reasoning_history.append(ReasoningStep(
        agent="human_review",
        timestamp=datetime.now(),
        action="review_decision",
        reasoning=f"Human reviewer decision: {decision.upper()}",
        result=decision.upper()
    ))
    
    logger.info(f"Human review decision processed: {decision}")
    return state


def create_audit_workflow():
    """
    Create the LangGraph workflow for ESG audit with human review.
    
    Workflow:
    1. Extraction Agent → extracts data from PDF
    2. Verification Agent → validates against benchmarks
    3. Compliance Agent → evaluates BRSR compliance
    4. Human Review (conditional) → if flagged for review
    
    Returns:
        Compiled LangGraph workflow
    """
    # Initialize the state graph
    workflow = StateGraph(AuditState)
    
    # Add agent nodes
    workflow.add_node("extraction", extraction_agent)
    workflow.add_node("verification", verification_agent)
    workflow.add_node("compliance", compliance_agent)
    workflow.add_node("human_review", human_review_node)
    
    # Define the flow
    workflow.set_entry_point("extraction")
    
    # Conditional edge after extraction
    workflow.add_conditional_edges(
        "extraction",
        should_continue_after_extraction,
        {
            "verification": "verification",
            "end": END
        }
    )
    
    # Conditional edge after verification
    workflow.add_conditional_edges(
        "verification",
        should_continue_after_verification,
        {
            "compliance": "compliance"
        }
    )
    
    # Conditional edge after compliance (check for human review)
    workflow.add_conditional_edges(
        "compliance",
        should_require_human_review,
        {
            "human_review": "human_review",
            "end": END
        }
    )
    
    # Edge from human review to end
    workflow.add_edge("human_review", END)
    
    # Initialize checkpointer (SQLite)
    import sqlite3
    from langgraph.checkpoint.sqlite import SqliteSaver
    
    # Use distinct connection per thread? No, Checkpointer handles it.
    # Note: connect outside or ensure reuse. For simplicity in Streamlit, we create new connection
    # or rely on SqliteSaver opening it.
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    # Compile the graph with persistence and interrupt
    # interrupt_before=["human_review"]: Pause before entering human review node
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]
    )
    
    logger.info("Audit workflow created with persistence (SQLite) and HITL interrupts")
    return app

