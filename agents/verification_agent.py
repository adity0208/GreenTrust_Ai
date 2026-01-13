"""
Verification Agent: Validates shipping claims against logistics API benchmarks.
Compares claimed emissions with expected values and flags discrepancies.
"""

from .state import AuditState, VerificationResult
from knowledge_base.logistics_api import logistics_api
import config
import logging

logger = logging.getLogger(__name__)


def calculate_deviation(claimed: float, benchmark: float) -> float:
    """Calculate percentage deviation from benchmark."""
    if benchmark == 0:
        return 100.0
    return abs((claimed - benchmark) / benchmark) * 100.0


def verification_agent(state: AuditState) -> AuditState:
    """
    Verification Agent node for LangGraph workflow.
    Validates emission claims against logistics API benchmarks.
    """
    from .state import ReasoningStep
    from datetime import datetime
    
    logger.info(f"Starting verification for document: {state.document_id}")
    
    state.reasoning_history.append(ReasoningStep(
        agent="verification",
        timestamp=datetime.now(),
        action="start_verification",
        reasoning="Beginning verification of emission claims against logistics benchmarks"
    ))
    
    # Check if extraction was successful
    if not state.extraction or state.workflow_status == "extraction_failed":
        state.reasoning_history.append(ReasoningStep(
            agent="verification",
            timestamp=datetime.now(),
            action="verification_skipped",
            reasoning="Cannot verify because extraction failed",
            result="SKIPPED"
        ))
        state.verification = VerificationResult(
            status="failed",
            discrepancies=["Cannot verify: extraction failed"]
        )
        state.workflow_status = "verification_failed"
        return state
    
    extraction = state.extraction
    discrepancies = []
    
    try:
        # Validate required fields
        if not all([extraction.transport_mode, extraction.weight_kg, extraction.distance_km]):
            state.reasoning_history.append(ReasoningStep(
                agent="verification",
                timestamp=datetime.now(),
                action="missing_fields",
                reasoning="Missing required fields (transport_mode, weight, or distance) for verification",
                result="FAILED"
            ))
            state.verification = VerificationResult(
                status="failed",
                discrepancies=["Missing required fields for verification"],
                verification_confidence=0.0
            )
            state.workflow_status = "verification_failed"
            return state
        
        # Determine route type from route string
        route_type = "domestic"
        if extraction.route:
            route_lower = extraction.route.lower()
            if any(keyword in route_lower for keyword in ["international", "overseas", "export"]):
                route_type = "international"
            if any(keyword in route_lower for keyword in ["express", "urgent", "priority"]):
                route_type = "express"
        
        state.reasoning_history.append(ReasoningStep(
            agent="verification",
            timestamp=datetime.now(),
            action="call_logistics_api",
            reasoning=f"Calling logistics API with mode={extraction.transport_mode}, weight={extraction.weight_kg}kg, distance={extraction.distance_km}km, route_type={route_type}"
        ))
        
        # Get benchmark from logistics API
        benchmark_data = logistics_api.get_benchmark_emissions(
            transport_mode=extraction.transport_mode,
            weight_kg=extraction.weight_kg,
            distance_km=extraction.distance_km,
            route_type=route_type
        )
        
        benchmark_co2e = benchmark_data["benchmark_co2e"]
        api_confidence = benchmark_data["confidence"]
        
        state.reasoning_history.append(ReasoningStep(
            agent="verification",
            timestamp=datetime.now(),
            action="benchmark_received",
            reasoning=f"Received benchmark: {benchmark_co2e} kg CO2e (confidence: {api_confidence})",
            result=f"Benchmark: {benchmark_co2e} kg"
        ))
        
        # Calculate deviation
        if extraction.co2e_claimed is not None:
            deviation = calculate_deviation(extraction.co2e_claimed, benchmark_co2e)
            state.reasoning_history.append(ReasoningStep(
                agent="verification",
                timestamp=datetime.now(),
                action="calculate_deviation",
                reasoning=f"Claimed: {extraction.co2e_claimed} kg vs Benchmark: {benchmark_co2e} kg",
                result=f"Deviation: {deviation:.1f}%"
            ))
        else:
            deviation = None
            discrepancies.append("No CO2e claim found in invoice")
        
        # Determine verification status
        status = "pending"
        if deviation is not None:
            max_deviation = config.BRSR_THRESHOLDS["max_deviation_percent"]
            
            if deviation <= max_deviation:
                status = "acceptable"
                state.reasoning_history.append(ReasoningStep(
                    agent="verification",
                    timestamp=datetime.now(),
                    action="status_acceptable",
                    reasoning=f"Deviation {deviation:.1f}% is within acceptable threshold of {max_deviation}%",
                    result="ACCEPTABLE"
                ))
            else:
                status = "flagged"
                discrepancies.append(
                    f"Deviation of {deviation:.1f}% exceeds threshold of {max_deviation}%"
                )
                state.reasoning_history.append(ReasoningStep(
                    agent="verification",
                    timestamp=datetime.now(),
                    action="status_flagged",
                    reasoning=f"Deviation {deviation:.1f}% exceeds threshold - flagging for human review",
                    result="FLAGGED"
                ))
                
                # Flag for human review if deviation is significant
                state.requires_human_review = True
                state.human_review_reason = f"High emission deviation: {deviation:.1f}% (threshold: {max_deviation}%)"
            
            # Additional checks
            if extraction.co2e_claimed > benchmark_co2e * 2:
                discrepancies.append("Claimed emissions are more than double the benchmark")
                state.requires_human_review = True
                state.human_review_reason = "Claimed emissions >200% of benchmark - suspicious"
            
            if extraction.co2e_claimed < benchmark_co2e * 0.5:
                discrepancies.append("Claimed emissions are less than half the benchmark")
        
        # Create verification result
        state.verification = VerificationResult(
            benchmark_co2e=benchmark_co2e,
            deviation_percent=deviation,
            status=status,
            discrepancies=discrepancies,
            verification_confidence=api_confidence * extraction.extraction_confidence
        )
        
        state.workflow_status = "verification_complete"
        logger.info(f"Verification complete. Status: {status}, Deviation: {deviation}%")
        
    except Exception as e:
        logger.error(f"Verification agent error: {e}")
        state.reasoning_history.append(ReasoningStep(
            agent="verification",
            timestamp=datetime.now(),
            action="verification_error",
            reasoning=f"Verification failed with error: {str(e)}",
            result="ERROR"
        ))
        state.verification = VerificationResult(
            status="failed",
            discrepancies=[f"Verification error: {str(e)}"],
            verification_confidence=0.0
        )
        state.workflow_status = "verification_failed"
        state.errors.append(f"Verification error: {str(e)}")
    
    return state
