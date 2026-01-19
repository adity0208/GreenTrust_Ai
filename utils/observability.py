"""
Observability and Forensic Logging for GreenTrust AI.
Handles structured logging of LLM interactions and generates audit trail PDFs.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

class AuditLogger:
    """Handles structured logging for audit forensics."""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOGS_DIR / f"audit_log_{self.session_id}.jsonl"
    
    def log_interaction(self, 
                       provider: str, 
                       model: str, 
                       prompt: str, 
                       response: str, 
                       metadata: Dict[str, Any] = None):
        """Log a single LLM interaction."""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "full_prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    @staticmethod
    def generate_forensic_log_pdf(document_id: str, reasoning_history: List[Any], logs: List[Dict] = None):
        """Generate a forensic PDF report of the audit trail."""
        
        filename = f"output/{document_id}_forensic_log.pdf"
        os.makedirs("output", exist_ok=True)
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30
        )
        story.append(Paragraph("GreenTrust AI - Forensic Audit Log", title_style))
        story.append(Paragraph(f"Document ID: {document_id}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Reasoning History Section
        story.append(Paragraph("1. Agent Reasoning Trail", styles['Heading2']))
        
        data = [['Agent', 'Action', 'Timestamp', 'Result']]
        for step in reasoning_history:
            # Handle both object and dict
            if isinstance(step, dict):
                agent = step.get("agent", "")
                action = step.get("action", "")
                ts = step.get("timestamp", "")
                res = str(step.get("result", ""))
            else:
                agent = step.agent
                action = step.action
                ts = step.timestamp.strftime('%H:%M:%S') if hasattr(step.timestamp, 'strftime') else str(step.timestamp)
                res = str(step.result)
                
            data.append([agent.upper(), action, ts, res[:50]])
            
        t = Table(data, colWidths=[100, 150, 100, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # LLM Interaction Log (if provided)
        if logs:
            story.append(Paragraph("2. LLM Interaction Forensics", styles['Heading2']))
            for i, log in enumerate(logs, 1):
                story.append(Paragraph(f"Interaction #{i} ({log.get('provider')})", styles['Heading3']))
                
                # Prompt
                story.append(Paragraph("<b>Prompt:</b>", styles['Normal']))
                p_text = log.get('full_prompt', '')[:500] + "..." if len(log.get('full_prompt', '')) > 500 else log.get('full_prompt', '')
                story.append(Paragraph(p_text.replace('\n', '<br/>'), styles['Code']))
                story.append(Spacer(1, 5))
                
                # Response
                story.append(Paragraph("<b>Response:</b>", styles['Normal']))
                r_text = log.get('response', '')[:500] + "..." if len(log.get('response', '')) > 500 else log.get('response', '')
                story.append(Paragraph(r_text.replace('\n', '<br/>'), styles['Code']))
                story.append(Spacer(1, 15))

        doc.build(story)
        return filename


class LoggingCallbackHandler(BaseCallbackHandler):
    """LangChain callback handler to capture LLM inputs/outputs."""
    
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.logger = AuditLogger()
        self.current_prompts = {}
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        # Store prompts to map to completion
        run_id = kwargs.get("run_id")
        if run_id:
            self.current_prompts[run_id] = prompts[0] if prompts else ""

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        run_id = kwargs.get("run_id")
        prompt = self.current_prompts.get(run_id, "")
        
        generation = response.generations[0][0].text
        
        self.logger.log_interaction(
            provider=self.provider,
            model=self.model,
            prompt=prompt,
            response=generation
        )
