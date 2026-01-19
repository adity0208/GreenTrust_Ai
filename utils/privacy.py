"""
PII Protection Layer (Privacy Guard).
Redacts sensitive personal information from text before LLM processing.
"""

import re
from typing import Tuple, Dict, List

class PIIGuard:
    """Handles redaction of Personally Identifiable Information (PII)."""
    
    def __init__(self):
        # Regex patterns for common PII
        self.patterns = {
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "PHONE": r'\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            "CREDIT_CARD": r'\b(?:\d{4}[-\s]){3}\d{4}\b|\b\d{16}\b',
            "SSN_US": r'\b\d{3}-\d{2}-\d{4}\b',
            # GST is public business info, usually fine, but PAN might be sensitive
            "PAN_INDIA": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
            "AADHAAR": r'\b\d{4}\s\d{4}\s\d{4}\b'
        }
    
    def redact_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Redact PII from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (redacted_text, mapping_dict)
            mapping_dict allows purely reversing if needed locally, although mainly we want to hide it from LLM.
        """
        redacted_text = text
        mapping = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for i, match in enumerate(matches):
                original = match.group()
                replacement = f"[{pii_type}_{i+1}]"
                redacted_text = redacted_text.replace(original, replacement)
                mapping[replacement] = original
                
        return redacted_text, mapping

    def contains_pii(self, text: str) -> List[str]:
        """Check if text contains potential PII."""
        found_types = []
        for pii_type, pattern in self.patterns.items():
            if re.search(pattern, text):
                found_types.append(pii_type)
        return found_types

# Singleton instance
pii_guard = PIIGuard()
