"""
Pydantic models for agent state management.
Defines the data structures passed between agents in the LangGraph workflow.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ReasoningStep(BaseModel):
    """A single reasoning step in the audit process."""
    
    agent: str = Field(description="Agent name (extraction, verification, compliance)")
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str = Field(description="Action taken by the agent")
    reasoning: str = Field(description="Reasoning behind the action")
    result: Optional[str] = Field(None, description="Result of the action")


class ExtractionResult(BaseModel):
    """Results from the Extraction Agent."""
    
    co2e_claimed: Optional[float] = Field(
        None, 
        description="Claimed CO2 equivalent emissions in kg"
    )
    supplier_id: Optional[str] = Field(
        None, 
        description="Supplier identifier extracted from invoice"
    )
    route: Optional[str] = Field(
        None, 
        description="Shipping route (origin-destination)"
    )
    transport_mode: Optional[str] = Field(
        None, 
        description="Mode of transportation (air, sea, road, rail)"
    )
    weight_kg: Optional[float] = Field(
        None, 
        description="Shipment weight in kilograms"
    )
    distance_km: Optional[float] = Field(
        None, 
        description="Distance traveled in kilometers"
    )
    extracted_text: str = Field(
        default="", 
        description="Raw text extracted from PDF"
    )
    extraction_confidence: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0,
        description="Confidence score for extraction quality"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="List of extraction errors or warnings"
    )


class VerificationResult(BaseModel):
    """Results from the Verification Agent."""
    
    benchmark_co2e: Optional[float] = Field(
        None, 
        description="Benchmark CO2e from logistics API"
    )
    deviation_percent: Optional[float] = Field(
        None, 
        description="Percentage deviation from benchmark"
    )
    status: str = Field(
        default="pending",
        description="Verification status: acceptable, flagged, or failed"
    )
    discrepancies: List[str] = Field(
        default_factory=list,
        description="List of identified discrepancies"
    )
    verification_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in verification results"
    )


class ComplianceResult(BaseModel):
    """Results from the Compliance Agent."""
    
    trust_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall trust score (0-100)"
    )
    brsr_aligned: bool = Field(
        default=False,
        description="Whether the audit aligns with SEBI BRSR standards"
    )
    category: str = Field(
        default="Scope 3 - Category 4",
        description="ESG category classification"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Compliance recommendations"
    )
    compliance_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed compliance assessment"
    )


class AuditState(BaseModel):
    """Overall state for the audit workflow."""
    
    # Input
    pdf_path: str = Field(
        description="Path to the PDF invoice being audited"
    )
    document_id: str = Field(
        description="Unique identifier for the document"
    )
    
    # Agent Results
    extraction: Optional[ExtractionResult] = None
    verification: Optional[VerificationResult] = None
    compliance: Optional[ComplianceResult] = None
    
    # Reasoning History
    reasoning_history: List[ReasoningStep] = Field(
        default_factory=list,
        description="History of reasoning steps taken by agents"
    )
    
    # Human Review
    requires_human_review: bool = Field(
        default=False,
        description="Whether this audit requires human review"
    )
    human_review_reason: Optional[str] = Field(
        None,
        description="Reason for requiring human review"
    )
    human_review_completed: bool = Field(
        default=False,
        description="Whether human review has been completed"
    )
    human_review_decision: Optional[str] = Field(
        None,
        description="Human reviewer's decision (approve/reject/modify)"
    )
    
    # Metadata
    audit_date: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the audit"
    )
    workflow_status: str = Field(
        default="initialized",
        description="Current workflow status"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Workflow-level errors"
    )
    
    class Config:
        arbitrary_types_allowed = True
