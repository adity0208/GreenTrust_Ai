"""
Demo mode runner - works without OpenAI API key.
Uses mock data to demonstrate the complete workflow.
"""

from agents.state import AuditState, ExtractionResult, VerificationResult, ComplianceResult, ReasoningStep
from agents.workflow import create_audit_workflow
from knowledge_base.logistics_api import logistics_api
from datetime import datetime
import json
from pathlib import Path

def run_demo_audit(pdf_path: str, is_suspicious: bool = False):
    """Run a demo audit with mock LLM responses."""
    
    print(f"\n{'='*60}")
    print(f"DEMO MODE: Auditing {Path(pdf_path).name}")
    print(f"{'='*60}\n")
    
    # Create initial state
    state = AuditState(
        pdf_path=pdf_path,
        document_id=Path(pdf_path).stem
    )
    
    # Simulate extraction (without LLM)
    print("[1/4] Extraction Agent...")
    state.reasoning_history.append(ReasoningStep(
        agent="extraction",
        timestamp=datetime.now(),
        action="extract_pdf_text",
        reasoning="Extracting text from PDF using PyMuPDF"
    ))
    
    if is_suspicious:
        # Suspicious invoice data
        state.extraction = ExtractionResult(
            co2e_claimed=125.0,  # SUSPICIOUSLY LOW
            supplier_id="SUP-DL-2024-156",
            route="Delhi-Mumbai",
            transport_mode="road",
            weight_kg=3200,
            distance_km=1420,
            extraction_confidence=0.88,
            extracted_text="Quick Freight Services invoice..."
        )
    else:
        # Valid invoice data
        state.extraction = ExtractionResult(
            co2e_claimed=348.0,
            supplier_id="SUP-MH-2024-089",
            route="Mumbai Port-Delhi Warehouse",
            transport_mode="road",
            weight_kg=2500,
            distance_km=1450,
            extraction_confidence=0.92,
            extracted_text="Global Logistics Co. invoice..."
        )
    
    state.reasoning_history.append(ReasoningStep(
        agent="extraction",
        timestamp=datetime.now(),
        action="extraction_complete",
        reasoning=f"Extracted CO2e: {state.extraction.co2e_claimed} kg, Supplier: {state.extraction.supplier_id}",
        result="SUCCESS"
    ))
    print(f"   ✓ Extracted: {state.extraction.co2e_claimed} kg CO2e from {state.extraction.supplier_id}")
    
    # Simulate verification
    print("\n[2/4] Verification Agent...")
    benchmark_data = logistics_api.get_benchmark_emissions(
        transport_mode=state.extraction.transport_mode,
        weight_kg=state.extraction.weight_kg,
        distance_km=state.extraction.distance_km
    )
    
    benchmark_co2e = benchmark_data["benchmark_co2e"]
    deviation = abs((state.extraction.co2e_claimed - benchmark_co2e) / benchmark_co2e) * 100
    
    state.reasoning_history.append(ReasoningStep(
        agent="verification",
        timestamp=datetime.now(),
        action="calculate_deviation",
        reasoning=f"Claimed: {state.extraction.co2e_claimed} kg vs Benchmark: {benchmark_co2e} kg",
        result=f"Deviation: {deviation:.1f}%"
    ))
    
    if deviation > 15:
        status = "flagged"
        state.requires_human_review = True
        state.human_review_reason = f"High emission deviation: {deviation:.1f}% (threshold: 15%)"
        print(f"   ⚠ FLAGGED: {deviation:.1f}% deviation (benchmark: {benchmark_co2e} kg)")
    else:
        status = "acceptable"
        print(f"   ✓ ACCEPTABLE: {deviation:.1f}% deviation (benchmark: {benchmark_co2e} kg)")
    
    state.verification = VerificationResult(
        benchmark_co2e=benchmark_co2e,
        deviation_percent=deviation,
        status=status,
        discrepancies=[] if status == "acceptable" else [f"Deviation of {deviation:.1f}% exceeds threshold"],
        verification_confidence=0.85
    )
    
    # Simulate compliance
    print("\n[3/4] Compliance Agent...")
    
    # Calculate trust score
    if is_suspicious:
        trust_score = 42.3
        brsr_aligned = False
        recommendations = [
            "Request third-party verification",
            "Investigate proprietary emission calculation method",
            "Require supplier-specific emission factors"
        ]
    else:
        trust_score = 78.5
        brsr_aligned = True
        recommendations = [
            "Request supplier-specific emission factors",
            "Implement continuous monitoring",
            "Consider third-party verification for material emissions"
        ]
    
    state.compliance = ComplianceResult(
        trust_score=trust_score,
        brsr_aligned=brsr_aligned,
        category="Scope 3 - Category 4",
        recommendations=recommendations,
        compliance_details={
            "data_completeness_score": 28.5 if not is_suspicious else 25.0,
            "verification_quality_score": 35.0 if not is_suspicious else 10.0,
            "disclosure_standards_score": 15.0 if not is_suspicious else 7.3
        }
    )
    
    state.reasoning_history.append(ReasoningStep(
        agent="compliance",
        timestamp=datetime.now(),
        action="final_trust_score",
        reasoning=f"Calculated Trust Score based on SEBI BRSR compliance criteria",
        result=f"Trust Score: {trust_score}/100"
    ))
    
    print(f"   ✓ Trust Score: {trust_score}/100 (BRSR Aligned: {brsr_aligned})")
    
    # Human review if needed
    if state.requires_human_review:
        print("\n[4/4] Human Review...")
        state.reasoning_history.append(ReasoningStep(
            agent="human_review",
            timestamp=datetime.now(),
            action="review_flagged",
            reasoning=f"Invoice flagged: {state.human_review_reason}",
            result="PENDING_REVIEW"
        ))
        
        # Auto-decision for demo
        decision = "approve" if trust_score > 40 else "reject"
        state.human_review_completed = True
        state.human_review_decision = decision
        
        state.reasoning_history.append(ReasoningStep(
            agent="human_review",
            timestamp=datetime.now(),
            action="review_decision",
            reasoning=f"Human reviewer decision: {decision.upper()}",
            result=decision.upper()
        ))
        
        print(f"   ⚠ Review Required: {state.human_review_reason}")
        print(f"   → Decision: {decision.upper()}")
    else:
        print("\n[4/4] Human Review...")
        print("   ✓ No review required")
    
    state.workflow_status = "compliance_complete"
    
    # Print summary
    print(f"\n{'='*60}")
    print("AUDIT SUMMARY")
    print(f"{'='*60}")
    print(f"Document: {state.document_id}")
    print(f"Trust Score: {state.compliance.trust_score}/100")
    print(f"BRSR Aligned: {state.compliance.brsr_aligned}")
    
    if state.requires_human_review:
        print(f"\n[!] HUMAN REVIEW REQUIRED")
        print(f"Reason: {state.human_review_reason}")
        print(f"Decision: {state.human_review_decision.upper()}")
    
    print(f"\nRecommendations:")
    for rec in state.compliance.recommendations:
        print(f"  • {rec}")
    
    print(f"\nReasoning Steps ({len(state.reasoning_history)} total):")
    for i, step in enumerate(state.reasoning_history[-5:], 1):
        print(f"  {i}. [{step.agent}] {step.action}: {step.reasoning[:60]}...")
    
    print(f"{'='*60}\n")
    
    # Save output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output = {
        "document_id": state.document_id,
        "audit_date": state.audit_date.isoformat(),
        "workflow_status": state.workflow_status,
        "extraction": {
            "co2e_claimed": state.extraction.co2e_claimed,
            "supplier_id": state.extraction.supplier_id,
            "route": state.extraction.route,
            "transport_mode": state.extraction.transport_mode,
            "weight_kg": state.extraction.weight_kg,
            "distance_km": state.extraction.distance_km,
            "extraction_confidence": state.extraction.extraction_confidence
        },
        "verification": {
            "benchmark_co2e": state.verification.benchmark_co2e,
            "deviation_percent": state.verification.deviation_percent,
            "status": state.verification.status,
            "discrepancies": state.verification.discrepancies
        },
        "compliance": {
            "trust_score": state.compliance.trust_score,
            "brsr_aligned": state.compliance.brsr_aligned,
            "recommendations": state.compliance.recommendations
        },
        "reasoning_history": [
            {
                "agent": step.agent,
                "timestamp": step.timestamp.isoformat(),
                "action": step.action,
                "reasoning": step.reasoning,
                "result": step.result
            }
            for step in state.reasoning_history
        ],
        "human_review": {
            "required": state.requires_human_review,
            "reason": state.human_review_reason,
            "completed": state.human_review_completed,
            "decision": state.human_review_decision
        }
    }
    
    output_file = output_dir / f"{state.document_id}_audit.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Results saved to: {output_file}\n")
    
    return output


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GREENTRUST AI - DEMO MODE (No API Key Required)")
    print("="*60)
    
    # Run demo on valid invoice
    run_demo_audit("data_samples/valid_invoice.pdf", is_suspicious=False)
    
    # Run demo on suspicious invoice
    run_demo_audit("data_samples/suspicious_invoice.pdf", is_suspicious=True)
    
    print("="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("\nTo run with real LLM:")
    print("1. Add OPENAI_API_KEY to .env file")
    print("2. Run: python main.py --input data_samples/valid_invoice.pdf")
    print("="*60)
