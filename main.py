"""
GreenTrust AI - Main Entry Point
Autonomous multi-agent auditor for ESG Scope 3 compliance.

Usage:
    python main.py --input data_samples/sample_invoice_1.pdf
    python main.py --input data_samples/ --batch
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

from agents import create_audit_workflow, AuditState
from evaluation import evaluate_audit_faithfulness
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_audit(pdf_path: str, output_dir: Path) -> dict:
    """
    Run ESG audit on a single PDF invoice.
    
    Args:
        pdf_path: Path to PDF invoice
        output_dir: Directory for output files
        
    Returns:
        Audit results as dictionary
    """
    logger.info(f"Starting audit for: {pdf_path}")
    
    # Create document ID from filename
    document_id = Path(pdf_path).stem
    
    # Initialize audit state
    initial_state = AuditState(
        pdf_path=pdf_path,
        document_id=document_id
    )
    
    # Create and run workflow
    workflow = create_audit_workflow()
    result = workflow.invoke(initial_state)
    
    # LangGraph returns a dict, convert back to AuditState
    if isinstance(result, dict):
        final_state = AuditState(**result)
    else:
        final_state = result
    
    # Build output JSON
    output = {
        "document_id": final_state.document_id,
        "audit_date": final_state.audit_date.isoformat(),
        "workflow_status": final_state.workflow_status,
        "extraction": None,
        "verification": None,
        "compliance": None,
        "errors": final_state.errors
    }
    
    # Add extraction results
    if final_state.extraction:
        output["extraction"] = {
            "co2e_claimed": final_state.extraction.co2e_claimed,
            "supplier_id": final_state.extraction.supplier_id,
            "route": final_state.extraction.route,
            "transport_mode": final_state.extraction.transport_mode,
            "weight_kg": final_state.extraction.weight_kg,
            "distance_km": final_state.extraction.distance_km,
            "extraction_confidence": final_state.extraction.extraction_confidence,
            "errors": final_state.extraction.errors
        }
    
    # Add verification results
    if final_state.verification:
        output["verification"] = {
            "benchmark_co2e": final_state.verification.benchmark_co2e,
            "deviation_percent": final_state.verification.deviation_percent,
            "status": final_state.verification.status,
            "discrepancies": final_state.verification.discrepancies,
            "verification_confidence": final_state.verification.verification_confidence
        }
    
    # Add compliance results
    if final_state.compliance:
        output["compliance"] = {
            "trust_score": final_state.compliance.trust_score,
            "brsr_aligned": final_state.compliance.brsr_aligned,
            "category": final_state.compliance.category,
            "recommendations": final_state.compliance.recommendations,
            "compliance_details": final_state.compliance.compliance_details
        }
    
    # Add reasoning history
    output["reasoning_history"] = [
        {
            "agent": step.agent,
            "timestamp": step.timestamp.isoformat(),
            "action": step.action,
            "reasoning": step.reasoning,
            "result": step.result
        }
        for step in final_state.reasoning_history
    ]
    
    # Add human review status
    output["human_review"] = {
        "required": final_state.requires_human_review,
        "reason": final_state.human_review_reason,
        "completed": final_state.human_review_completed,
        "decision": final_state.human_review_decision
    }
    
    # Save output
    output_file = output_dir / f"{document_id}_audit.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Audit complete. Results saved to: {output_file}")
    
    # Optional: Run RAGAS evaluation
    try:
        eval_scores = evaluate_audit_faithfulness(final_state)
        logger.info(f"Faithfulness score: {eval_scores.get('faithfulness', 'N/A')}")
    except Exception as e:
        logger.warning(f"Evaluation skipped: {e}")
    
    return output


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GreenTrust AI - ESG Scope 3 Auditor")
    parser.add_argument(
        "--input",
        type=str,
        default="data_samples/sample_invoice_1.pdf",
        help="Path to PDF invoice or directory of invoices"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all PDFs in input directory"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: output/)"
    )
    
    args = parser.parse_args()
    
    # Setup output directory
    output_dir = Path(args.output) if args.output else config.OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    
    # Process files
    input_path = Path(args.input)
    
    if args.batch and input_path.is_dir():
        # Batch processing
        pdf_files = list(input_path.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files for batch processing")
        
        results = []
        for pdf_file in pdf_files:
            try:
                result = run_audit(str(pdf_file), output_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
        
        # Save batch summary
        summary_file = output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({
                "total_processed": len(results),
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2)
        
        logger.info(f"Batch processing complete. Summary: {summary_file}")
        
    else:
        # Single file processing
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return
        
        result = run_audit(str(input_path), output_dir)
        
        # Print summary
        print("\n" + "="*60)
        print("GREENTRUST AI - AUDIT SUMMARY")
        print("="*60)
        print(f"Document: {result['document_id']}")
        print(f"Status: {result['workflow_status']}")
        
        if result.get('compliance'):
            print(f"\nTrust Score: {result['compliance']['trust_score']}/100")
            print(f"BRSR Aligned: {result['compliance']['brsr_aligned']}")
            
            # Human review status
            if result['human_review']['required']:
                print(f"\n[!] HUMAN REVIEW REQUIRED")
                print(f"Reason: {result['human_review']['reason']}")
                if result['human_review']['completed']:
                    print(f"Decision: {result['human_review']['decision'].upper()}")
            
            print(f"\nRecommendations:")
            for rec in result['compliance']['recommendations']:
                print(f"  • {rec}")
            
            # Show reasoning steps
            print(f"\nReasoning Steps ({len(result['reasoning_history'])} total):")
            for i, step in enumerate(result['reasoning_history'][-5:], 1):  # Show last 5
                print(f"  {i}. [{step['agent']}] {step['action']}: {step['reasoning'][:60]}...")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
