"""
Compliance Agent: Evaluates audit findings against SEBI BRSR standards.
Generates a Trust Score and compliance recommendations.
"""

from .state import AuditState, ComplianceResult
from langchain_core.prompts import ChatPromptTemplate
from llm_providers import get_llm_with_fallback
import config
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Load BRSR standards
brsr_standards_path = config.KNOWLEDGE_BASE_DIR / "sebi_brsr_standards.md"
with open(brsr_standards_path, "r", encoding="utf-8") as f:
    BRSR_STANDARDS = f.read()

# Get LLM with automatic fallback
llm, provider_used = get_llm_with_fallback()
logger.info(f"Compliance agent using provider: {provider_used}")

# Compliance evaluation prompt
compliance_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an ESG compliance expert specializing in SEBI BRSR standards.

Evaluate the audit findings against the SEBI BRSR Value Chain disclosure requirements, 
**specifically Principle 6 Question 2: Non-renewable energy consumption and related disclosures**.

BRSR Standards:
{brsr_standards}

Provide:
1. A Trust Score (0-100) based on:
   - Data Completeness (30%)
   - Verification Quality (40%)
   - Disclosure Standards (30%)

2. Whether the audit aligns with BRSR Principle 6 requirements (true/false)

3. Specific recommendations for improvement, including:
   - Energy consumption disclosure requirements
   - Emission factor source citation
   - Methodology transparency

4. Detailed compliance assessment against SEBI Principle 6 Question 2

Be strict but fair. A Trust Score ≥60 indicates acceptable compliance."""),
    ("user", """Audit Findings:

**Extraction Results:**
- CO2e Claimed: {co2e_claimed} kg
- Supplier ID: {supplier_id}
- Route: {route}
- Transport Mode: {transport_mode}
- Weight: {weight_kg} kg
- Distance: {distance_km} km
- Extraction Confidence: {extraction_confidence}
- Extraction Errors: {extraction_errors}

**Verification Results:**
- Benchmark CO2e: {benchmark_co2e} kg
- Deviation: {deviation_percent}%
- Status: {verification_status}
- Discrepancies: {discrepancies}
- Verification Confidence: {verification_confidence}

**SEBI Principle 6 Question 2 Checklist:**
- Energy consumption data disclosed: {energy_disclosed}
- Emission factor source cited: {emission_factor_cited}
- Calculation methodology explained: {methodology_explained}

Provide your compliance evaluation in the following JSON format:
{{
  "trust_score": <float 0-100>,
  "brsr_aligned": <boolean>,
  "recommendations": [<list of strings>],
  "compliance_details": {{
    "data_completeness_score": <float 0-30>,
    "verification_quality_score": <float 0-40>,
    "disclosure_standards_score": <float 0-30>,
    "principle_6_q2_compliance": <boolean>,
    "key_strengths": [<list of strings>],
    "key_weaknesses": [<list of strings>]
  }}
}}""")
])


def calculate_base_trust_score(state: AuditState) -> float:
    """Calculate a base trust score from quantitative metrics."""
    score = 0.0
    extraction = state.extraction
    verification = state.verification
    
    if not extraction or not verification:
        return 0.0
    
    # Data Completeness (30 points)
    completeness_score = 0.0
    required_fields = [
        extraction.co2e_claimed,
        extraction.supplier_id,
        extraction.route,
        extraction.transport_mode,
        extraction.weight_kg,
        extraction.distance_km
    ]
    fields_present = sum(1 for field in required_fields if field is not None)
    completeness_score = (fields_present / len(required_fields)) * 30.0
    
    # Verification Quality (40 points)
    verification_score = 0.0
    if verification.status == "acceptable":
        verification_score = 40.0
    elif verification.status == "flagged":
        # Partial credit based on deviation
        if verification.deviation_percent is not None:
            max_dev = config.BRSR_THRESHOLDS["max_deviation_percent"]
            if verification.deviation_percent < max_dev * 2:
                verification_score = 20.0
            else:
                verification_score = 10.0
    
    # Apply confidence multiplier
    verification_score *= verification.verification_confidence
    
    # Disclosure Standards (30 points)
    disclosure_score = 0.0
    # Base score for having extraction
    disclosure_score += 15.0
    # Bonus for high extraction confidence
    disclosure_score += extraction.extraction_confidence * 15.0
    
    score = completeness_score + verification_score + disclosure_score
    return min(score, 100.0)


def compliance_agent(state: AuditState) -> AuditState:
    """
    Compliance Agent node for LangGraph workflow.
    Evaluates findings against SEBI BRSR standards and generates Trust Score.
    """
    from .state import ReasoningStep
    from datetime import datetime
    
    logger.info(f"Starting compliance evaluation for document: {state.document_id}")
    
    state.reasoning_history.append(ReasoningStep(
        agent="compliance",
        timestamp=datetime.now(),
        action="start_compliance_evaluation",
        reasoning="Beginning SEBI BRSR compliance evaluation and Trust Score calculation"
    ))
    
    # Check if previous steps completed
    if not state.extraction or not state.verification:
        state.reasoning_history.append(ReasoningStep(
            agent="compliance",
            timestamp=datetime.now(),
            action="compliance_failed",
            reasoning="Cannot evaluate compliance because extraction or verification failed",
            result="FAILED"
        ))
        state.compliance = ComplianceResult(
            trust_score=0.0,
            brsr_aligned=False,
            recommendations=["Cannot evaluate compliance: extraction or verification failed"]
        )
        state.workflow_status = "compliance_failed"
        return state
    
    try:
        extraction = state.extraction
        verification = state.verification
        
        # Calculate base trust score
        base_score = calculate_base_trust_score(state)
        
        state.reasoning_history.append(ReasoningStep(
            agent="compliance",
            timestamp=datetime.now(),
            action="calculate_base_score",
            reasoning="Calculated quantitative Trust Score from data completeness, verification quality, and disclosure standards",
            result=f"Base score: {base_score:.1f}/100"
        ))
        
        # Check for demo mode
        try:
            from demo_config import DEMO_MODE
        except ImportError:
            DEMO_MODE = False
        
        if DEMO_MODE:
            # Demo mode - use only quantitative scoring
            logger.info("Demo mode enabled - using quantitative scoring only")
            
            state.reasoning_history.append(ReasoningStep(
                agent="compliance",
                timestamp=datetime.now(),
                action="demo_mode_compliance",
                reasoning="Demo mode enabled - using quantitative Trust Score calculation (no LLM evaluation)",
                result=f"Trust Score: {base_score:.1f}/100"
            ))
            
            state.compliance = ComplianceResult(
                trust_score=round(base_score, 1),
                brsr_aligned=base_score >= config.BRSR_THRESHOLDS["min_trust_score"],
                category="Scope 3 - Category 4",
                recommendations=[
                    "Request supplier-specific emission factors" if base_score >= 60 else "Require third-party verification",
                    "Implement continuous monitoring",
                    "Enhance data completeness" if base_score < 80 else "Maintain current disclosure standards"
                ],
                compliance_details={
                    "data_completeness_score": min(base_score * 0.3, 30),
                    "verification_quality_score": min(base_score * 0.4, 40),
                    "disclosure_standards_score": min(base_score * 0.3, 30),
                    "demo_mode": True
                }
            )
        else:
            # Normal mode - try LLM evaluation
            # Prepare data for LLM evaluation
            chain = compliance_prompt | llm
            
            response = chain.invoke({
                "brsr_standards": BRSR_STANDARDS[:3000],  # Truncate for context window
                "co2e_claimed": extraction.co2e_claimed or "Not found",
                "supplier_id": extraction.supplier_id or "Not found",
                "route": extraction.route or "Not found",
                "transport_mode": extraction.transport_mode or "Not found",
                "weight_kg": extraction.weight_kg or "Not found",
                "distance_km": extraction.distance_km or "Not found",
                "extraction_confidence": f"{extraction.extraction_confidence:.2f}",
                "extraction_errors": ", ".join(extraction.errors) if extraction.errors else "None",
                "benchmark_co2e": verification.benchmark_co2e or "Not calculated",
                "deviation_percent": f"{verification.deviation_percent:.1f}" if verification.deviation_percent else "N/A",
                "verification_status": verification.status,
                "discrepancies": ", ".join(verification.discrepancies) if verification.discrepancies else "None",
                "verification_confidence": f"{verification.verification_confidence:.2f}",
                # SEBI Principle 6 Question 2 checklist
                "energy_disclosed": "Yes" if extraction.co2e_claimed else "No",
                "emission_factor_cited": "Partial (benchmark-based)" if verification.benchmark_co2e else "No",
                "methodology_explained": "Yes (GHG Protocol)" if extraction.transport_mode else "No"
            })
            
            # Parse LLM response (expecting JSON)
            import json
            response_text = response.content
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]
            
            compliance_data = json.loads(response_text)
            
            # Blend LLM score with base score (70% LLM, 30% base)
            final_score = compliance_data["trust_score"] * 0.7 + base_score * 0.3
            
            state.reasoning_history.append(ReasoningStep(
                agent="compliance",
                timestamp=datetime.now(),
                action="final_trust_score",
                reasoning=f"Blended LLM evaluation ({compliance_data['trust_score']:.1f}) with quantitative score ({base_score:.1f})",
                result=f"Final Trust Score: {final_score:.1f}/100"
            ))
            
            state.compliance = ComplianceResult(
                trust_score=round(final_score, 1),
                brsr_aligned=compliance_data["brsr_aligned"],
                category="Scope 3 - Category 4",
                recommendations=compliance_data["recommendations"],
                compliance_details=compliance_data["compliance_details"]
            )
        
        # Check if low trust score requires human review
        if final_score < config.BRSR_THRESHOLDS["min_trust_score"]:
            state.requires_human_review = True
            if not state.human_review_reason:
                state.human_review_reason = f"Low Trust Score: {final_score:.1f} (threshold: {config.BRSR_THRESHOLDS['min_trust_score']})"
        
        state.workflow_status = "compliance_complete"
        logger.info(f"Compliance evaluation complete. Trust Score: {final_score:.1f}")
        
    except Exception as e:
        logger.error(f"Compliance agent error: {e}")
        # Fallback to base score
        state.compliance = ComplianceResult(
            trust_score=round(base_score, 1),
            brsr_aligned=base_score >= config.BRSR_THRESHOLDS["min_trust_score"],
            category="Scope 3 - Category 4",
            recommendations=[
                "LLM evaluation failed, using quantitative metrics only",
                "Manual review recommended"
            ],
            compliance_details={
                "error": str(e)
            }
        )
        state.workflow_status = "compliance_complete_with_errors"
        state.errors.append(f"Compliance error: {str(e)}")
    
    return state
