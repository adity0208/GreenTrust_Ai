"""
Extraction Agent: Extracts carbon metrics and supplier information from PDF invoices.
Uses PyMuPDF for PDF parsing and LLM for structured data extraction.
"""

import fitz  # PyMuPDF
from .state import AuditState, ExtractionResult, ReasoningStep
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from llm_providers import get_llm_with_fallback
import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# Get LLM with automatic fallback
llm, provider_used = get_llm_with_fallback()
logger.info(f"Extraction agent using provider: {provider_used}")

# Output parser
parser = PydanticOutputParser(pydantic_object=ExtractionResult)

# Extraction prompt
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting carbon emission data from shipping invoices.
Extract the following information from the invoice text:
- CO2 equivalent emissions (co2e_claimed) in kg
- Supplier identifier (supplier_id)
- Shipping route (route) as "Origin-Destination"
- Transport mode (transport_mode): air, sea, road, or rail
- Shipment weight (weight_kg) in kilograms
- Distance traveled (distance_km) in kilometers

If any field cannot be found, set it to null. Provide an extraction_confidence score (0-1).
List any extraction errors or ambiguities in the errors field.

{format_instructions}"""),
    ("user", "Invoice text:\n\n{invoice_text}")
])


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        max_pages = min(len(doc), config.EXTRACTION_CONFIG["max_pages"])
        
        for page_num in range(max_pages):
            page = doc[page_num]
            text += page.get_text()
        
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise


def extraction_agent(state: AuditState) -> AuditState:
    """
    Extraction Agent node for LangGraph workflow.
    Extracts structured carbon metrics from PDF invoices.
    """
    from .state import ReasoningStep
    from datetime import datetime
    
    logger.info(f"Starting extraction for document: {state.document_id}")
    
    # Log reasoning step
    state.reasoning_history.append(ReasoningStep(
        agent="extraction",
        timestamp=datetime.now(),
        action="extract_pdf_text",
        reasoning="Attempting to extract text from PDF invoice using PyMuPDF"
    ))
    
    try:
        # Extract text from PDF
        invoice_text = extract_text_from_pdf(state.pdf_path)
        
        if not invoice_text:
            state.reasoning_history.append(ReasoningStep(
                agent="extraction",
                timestamp=datetime.now(),
                action="extraction_failed",
                reasoning="No text could be extracted from PDF - file may be corrupted or image-based",
                result="FAILED"
            ))
            state.extraction = ExtractionResult(
                extracted_text="",
                extraction_confidence=0.0,
                errors=["No text could be extracted from PDF"]
            )
            state.workflow_status = "extraction_failed"
            return state
        
        state.reasoning_history.append(ReasoningStep(
            agent="extraction",
            timestamp=datetime.now(),
            action="text_extracted",
            reasoning=f"Successfully extracted {len(invoice_text)} characters from PDF",
            result=f"Extracted {len(invoice_text)} chars"
        ))
        
        # PII Redaction
        from utils.privacy import pii_guard
        
        # Check for PII
        pii_types = pii_guard.contains_pii(invoice_text)
        if pii_types:
            logger.info(f"PII detected: {pii_types}. Redacting...")
            redacted_text, _ = pii_guard.redact_text(invoice_text)
            
            state.reasoning_history.append(ReasoningStep(
                agent="extraction",
                timestamp=datetime.now(),
                action="pii_redaction",
                reasoning=f"Detected potential PII ({', '.join(set(pii_types))}). Masking sensitive data before LLM processing.",
                result="PII_REDACTED"
            ))
            
            # Use redacted text for LLM
            llm_input_text = redacted_text
        else:
            llm_input_text = invoice_text
        
        # Use LLM to extract structured data
        state.reasoning_history.append(ReasoningStep(
            agent="extraction",
            timestamp=datetime.now(),
            action="llm_extraction",
            reasoning="Using LLM to extract structured carbon metrics (CO2e, supplier ID, route, mode, weight, distance)",
            result="PROCESSING"
        ))
        
        # Check for demo mode
        try:
            from demo_config import DEMO_MODE
        except ImportError:
            DEMO_MODE = False
        
        if DEMO_MODE:
            # Skip LLM entirely in demo mode
            logger.info("Demo mode enabled - using regex extraction directly")
            state.reasoning_history.append(ReasoningStep(
                agent="extraction",
                timestamp=datetime.now(),
                action="demo_mode_activated",
                reasoning="Demo mode enabled - bypassing LLM to use regex extraction directly (no API calls)",
                result="DEMO_MODE"
            ))
            
            from .regex_extractor import extract_with_regex
            
            regex_result = extract_with_regex(invoice_text)
            
            extraction_result = ExtractionResult(
                co2e_claimed=regex_result.get("co2e_claimed"),
                supplier_id=regex_result.get("supplier_id"),
                route=regex_result.get("route"),
                transport_mode=regex_result.get("transport_mode"),
                weight_kg=regex_result.get("weight_kg"),
                distance_km=regex_result.get("distance_km"),
                extracted_text=invoice_text[:1000],
                extraction_confidence=regex_result.get("extraction_confidence", 0.75),  # Higher confidence in demo
                errors=[]
            )
            
            state.extraction = extraction_result
            state.workflow_status = "extraction_complete"
            
            state.reasoning_history.append(ReasoningStep(
                agent="extraction",
                timestamp=datetime.now(),
                action="regex_extraction_complete",
                reasoning=f"Regex extraction successful with {extraction_result.extraction_confidence:.2f} confidence",
                result=f"CO2e: {extraction_result.co2e_claimed}, Supplier: {extraction_result.supplier_id}"
            ))
            
            logger.info(f"Demo mode extraction complete. Confidence: {extraction_result.extraction_confidence}")
        else:
            # Normal mode - try LLM first
            try:
                # Attempt LLM extraction
                chain = extraction_prompt | llm | parser
                
                extraction_result = chain.invoke({
                    "invoice_text": llm_input_text[:5000],
                    "format_instructions": parser.get_format_instructions()
                })
                
                extraction_result.extracted_text = invoice_text[:1000]
                
                state.extraction = extraction_result
                state.workflow_status = "extraction_complete"
                
                state.reasoning_history.append(ReasoningStep(
                    agent="extraction",
                    timestamp=datetime.now(),
                    action="extraction_complete",
                    reasoning=f"Extracted data with {extraction_result.extraction_confidence:.2f} confidence using LLM",
                    result=f"CO2e: {extraction_result.co2e_claimed}, Supplier: {extraction_result.supplier_id}"
                ))
                
                logger.info(f"LLM extraction complete. Confidence: {extraction_result.extraction_confidence}")
                
            except Exception as llm_error:
                # Fallback to regex extraction
                logger.warning(f"LLM extraction failed ({str(llm_error)}), falling back to regex extractor")
                
                state.reasoning_history.append(ReasoningStep(
                    agent="extraction",
                    timestamp=datetime.now(),
                    action="llm_fallback",
                    reasoning=f"LLM extraction failed: {str(llm_error)[:100]}. Switching to regex-based fallback extractor",
                    result="FALLBACK_ACTIVATED"
                ))
                
                try:
                    from .regex_extractor import extract_with_regex
                    
                    regex_result = extract_with_regex(invoice_text)
                    
                    extraction_result = ExtractionResult(
                        co2e_claimed=regex_result.get("co2e_claimed"),
                        supplier_id=regex_result.get("supplier_id"),
                        route=regex_result.get("route"),
                        transport_mode=regex_result.get("transport_mode"),
                        weight_kg=regex_result.get("weight_kg"),
                        distance_km=regex_result.get("distance_km"),
                        extracted_text=invoice_text[:1000],
                        extraction_confidence=regex_result.get("extraction_confidence", 0.6),
                        errors=[]
                    )
                    
                    state.extraction = extraction_result
                    state.workflow_status = "extraction_complete"
                    
                    state.reasoning_history.append(ReasoningStep(
                        agent="extraction",
                        timestamp=datetime.now(),
                        action="regex_extraction_complete",
                        reasoning=f"Regex fallback successful with {extraction_result.extraction_confidence:.2f} confidence (lower than LLM)",
                        result=f"CO2e: {extraction_result.co2e_claimed}, Supplier: {extraction_result.supplier_id}"
                    ))
                    
                    logger.info(f"Regex fallback extraction complete. Confidence: {extraction_result.extraction_confidence}")
                    
                except Exception as regex_error:
                    logger.error(f"Both LLM and regex extraction failed: {regex_error}")
                    state.reasoning_history.append(ReasoningStep(
                        agent="extraction",
                        timestamp=datetime.now(),
                        action="extraction_error",
                        reasoning=f"Both LLM and regex extraction failed. LLM: {str(llm_error)[:50]}, Regex: {str(regex_error)[:50]}",
                        result="ERROR"
                    ))
                    state.extraction = ExtractionResult(
                        extracted_text="",
                        extraction_confidence=0.0,
                        errors=[f"LLM failed: {str(llm_error)}", f"Regex failed: {str(regex_error)}"]
                    )
                    state.workflow_status = "extraction_failed"
                    state.errors.append(f"Extraction error: {str(llm_error)}")
        
    except Exception as e:
        logger.error(f"Extraction agent error: {e}")
        state.reasoning_history.append(ReasoningStep(
            agent="extraction",
            timestamp=datetime.now(),
            action="extraction_error",
            reasoning=f"Extraction failed due to error: {str(e)}",
            result="ERROR"
        ))
        state.extraction = ExtractionResult(
            extracted_text="",
            extraction_confidence=0.0,
            errors=[f"Extraction failed: {str(e)}"]
        )
        state.workflow_status = "extraction_failed"
        state.errors.append(f"Extraction error: {str(e)}")
    
    return state
