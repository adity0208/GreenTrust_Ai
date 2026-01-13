"""
Regex-based fallback extractor for when LLM fails.
Ensures zero downtime during live demos.
"""

import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def extract_with_regex(text: str) -> Dict[str, Any]:
    """
    Extract carbon metrics using regex patterns.
    Fallback when OpenAI API fails.
    
    Args:
        text: Raw invoice text
        
    Returns:
        Dictionary with extracted fields
    """
    logger.info("Using regex fallback extractor")
    
    result = {
        "co2e_claimed": None,
        "supplier_id": None,
        "route": None,
        "transport_mode": None,
        "weight_kg": None,
        "distance_km": None,
        "extraction_confidence": 0.6  # Lower confidence for regex
    }
    
    # Extract CO2e emissions
    co2e_patterns = [
        r'(\d+\.?\d*)\s*kg\s*CO2e',
        r'CO2e[:\s]+(\d+\.?\d*)\s*kg',
        r'emissions[:\s]+(\d+\.?\d*)\s*kg',
        r'carbon[:\s]+(\d+\.?\d*)\s*kg'
    ]
    
    for pattern in co2e_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["co2e_claimed"] = float(match.group(1))
            break
    
    # Extract supplier ID
    supplier_patterns = [
        r'SUP-[A-Z]{2}-\d{4}-\d{3,4}',
        r'Supplier\s+ID[:\s]+([A-Z0-9-]+)',
        r'Vendor[:\s]+([A-Z0-9-]+)'
    ]
    
    for pattern in supplier_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["supplier_id"] = match.group(0) if 'SUP-' in pattern else match.group(1)
            break
    
    # Extract route
    route_patterns = [
        r'([A-Za-z\s]+)\s*(?:→|->|to)\s*([A-Za-z\s]+)',
        r'Origin[:\s]+([A-Za-z\s]+).*?Destination[:\s]+([A-Za-z\s]+)',
        r'From[:\s]+([A-Za-z\s]+).*?To[:\s]+([A-Za-z\s]+)'
    ]
    
    for pattern in route_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            origin = match.group(1).strip()
            destination = match.group(2).strip()
            result["route"] = f"{origin}-{destination}"
            break
    
    # Extract transport mode
    mode_keywords = {
        "road": ["truck", "road", "highway", "lorry", "vehicle"],
        "air": ["air", "flight", "aircraft", "cargo plane"],
        "sea": ["sea", "ship", "vessel", "maritime", "ocean"],
        "rail": ["rail", "train", "railway"]
    }
    
    text_lower = text.lower()
    for mode, keywords in mode_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            result["transport_mode"] = mode
            break
    
    # Extract weight
    weight_patterns = [
        r'(\d+,?\d*\.?\d*)\s*kg',
        r'(\d+,?\d*\.?\d*)\s*kilograms',
        r'weight[:\s]+(\d+,?\d*\.?\d*)',
        r'(\d+\.?\d*)\s*(?:metric\s*)?tons?'
    ]
    
    for pattern in weight_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            weight_str = match.group(1).replace(',', '')
            weight = float(weight_str)
            
            # Convert tons to kg if needed
            if 'ton' in match.group(0).lower():
                weight *= 1000
            
            result["weight_kg"] = weight
            break
    
    # Extract distance
    distance_patterns = [
        r'(\d+,?\d*\.?\d*)\s*km',
        r'(\d+,?\d*\.?\d*)\s*kilometers',
        r'distance[:\s]+(\d+,?\d*\.?\d*)',
        r'(\d+,?\d*\.?\d*)\s*miles?'
    ]
    
    for pattern in distance_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            distance_str = match.group(1).replace(',', '')
            distance = float(distance_str)
            
            # Convert miles to km if needed
            if 'mile' in match.group(0).lower():
                distance *= 1.60934
            
            result["distance_km"] = distance
            break
    
    # Log extraction results
    extracted_fields = [k for k, v in result.items() if v is not None and k != "extraction_confidence"]
    logger.info(f"Regex extraction complete. Extracted fields: {extracted_fields}")
    
    return result


def validate_extraction(result: Dict[str, Any]) -> bool:
    """
    Validate that minimum required fields were extracted.
    
    Args:
        result: Extraction result dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["co2e_claimed", "transport_mode", "weight_kg", "distance_km"]
    
    for field in required_fields:
        if result.get(field) is None:
            logger.warning(f"Missing required field: {field}")
            return False
    
    return True


if __name__ == "__main__":
    # Test the regex extractor
    test_text = """
    GLOBAL LOGISTICS CO.
    Invoice No: INV-2024-00145
    Supplier ID: SUP-MH-2024-089
    
    Origin: Mumbai Port
    Destination: Delhi Warehouse
    Transport Mode: Road Freight - Heavy Truck
    Weight: 2,500 kg
    Distance: 1,450 kilometers
    
    Total CO2e Emissions: 348.0 kg CO2e
    """
    
    result = extract_with_regex(test_text)
    print("Extraction Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\nValidation: {'PASS' if validate_extraction(result) else 'FAIL'}")
