"""
KYRON Service Intent Detection
Detects user intent for government/private services from natural language
"""

import re
from typing import Dict, Optional, List, Tuple
from services_catalog import get_service_catalog, ServiceType

# Service keywords mapping
SERVICE_KEYWORDS = {
    ServiceType.PAN_CARD: [
        "pan", "pan card", "permanent account number", "pan application",
        "apply pan", "new pan", "pan card apply", "pan card application"
    ],
    ServiceType.INCOME_CERTIFICATE: [
        "income certificate", "income proof", "salary certificate",
        "income certificate apply", "income certificate application"
    ],
    ServiceType.CASTE_CERTIFICATE: [
        "caste certificate", "caste proof", "category certificate",
        "sc certificate", "st certificate", "obc certificate"
    ],
    ServiceType.DOMICILE: [
        "domicile", "domicile certificate", "residence certificate",
        "domicile proof", "domicile apply"
    ],
    ServiceType.BIHAR_RESIDENCE_CERTIFICATE: [
        "bihar residence certificate", "bihar residence", "brc",
        "niwas praman patra", "niwas praman patra bihar",
        "bihar residence certificate apply", "residence certificate bihar",
        "residence banwana hai", "bihar ka residence certificate"
    ]
}

def detect_service_intent(text: str) -> Optional[Tuple[ServiceType, float]]:
    """
    Detect service intent from user text
    
    Returns:
        Tuple of (ServiceType, confidence_score) or None if no match
    """
    text_lower = text.lower().strip()
    
    best_match = None
    best_confidence = 0.0
    
    for service_type, keywords in SERVICE_KEYWORDS.items():
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword in text_lower:
                matches += 1
                # Longer keywords get more weight
                weight = len(keyword.split())
                matches += weight * 0.1
        
        if matches > 0:
            confidence = min(matches / total_keywords, 1.0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = service_type
    
    # Require minimum confidence threshold
    if best_match and best_confidence >= 0.3:
        return (best_match, best_confidence)
    
    return None

def extract_service_parameters(text: str, service_type: ServiceType) -> Dict[str, any]:
    """
    Extract service-specific parameters from user text
    """
    text_lower = text.lower()
    params = {}
    
    if service_type == ServiceType.PAN_CARD:
        # Check for delivery type
        if "digital" in text_lower or "epan" in text_lower or "online" in text_lower:
            params["delivery_type"] = "digital"
        elif "physical" in text_lower or "card" in text_lower:
            params["delivery_type"] = "physical"
        
        # Check for applicant type
        if "company" in text_lower or "business" in text_lower or "huf" in text_lower:
            params["applicant_type"] = "company"
        elif "individual" in text_lower or "personal" in text_lower:
            params["applicant_type"] = "individual"
        
        # Check for application type
        if "new" in text_lower or "first time" in text_lower:
            params["application_type"] = "new"
        elif "correction" in text_lower or "update" in text_lower or "change" in text_lower:
            params["application_type"] = "correction"
    
    return params

