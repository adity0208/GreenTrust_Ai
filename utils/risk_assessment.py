"""
Risk assessment utilities for high-risk regions and suppliers.
"""

from typing import Dict, List, Tuple

# High-risk regions database (for demo purposes)
HIGH_RISK_REGIONS = {
    "conflict_zones": [
        "Afghanistan", "Syria", "Yemen", "Somalia", "South Sudan",
        "Libya", "Myanmar", "Ukraine (certain areas)", "Iraq"
    ],
    "sanctioned_countries": [
        "North Korea", "Iran", "Cuba", "Venezuela", "Belarus"
    ],
    "high_corruption": [
        "Turkmenistan", "Equatorial Guinea", "Eritrea", "Libya", "Yemen"
    ],
    "environmental_risk": [
        "Amazon Basin (illegal logging)", "Congo Basin", "Southeast Asia (palm oil)"
    ]
}

# Risk scoring weights
RISK_WEIGHTS = {
    "conflict_zones": 10,
    "sanctioned_countries": 10,
    "high_corruption": 7,
    "environmental_risk": 5
}


def assess_region_risk(region: str) -> Tuple[int, List[str], bool]:
    """
    Assess risk level for a given region.
    
    Args:
        region: Region name or country
        
    Returns:
        Tuple of (risk_score, risk_factors, requires_review)
    """
    region_lower = region.lower()
    risk_score = 0
    risk_factors = []
    
    for category, regions in HIGH_RISK_REGIONS.items():
        for high_risk_region in regions:
            if high_risk_region.lower() in region_lower:
                risk_score += RISK_WEIGHTS[category]
                risk_factors.append(f"{category.replace('_', ' ').title()}: {high_risk_region}")
    
    # Determine if human review is required (risk score >= 7)
    requires_review = risk_score >= 7
    
    return risk_score, risk_factors, requires_review


def assess_supplier_risk(supplier_id: str, region: str, claimed_co2e: float, benchmark_co2e: float) -> Dict:
    """
    Comprehensive supplier risk assessment.
    
    Args:
        supplier_id: Supplier identifier
        region: Supplier region/route
        claimed_co2e: Claimed emissions
        benchmark_co2e: Benchmark emissions
        
    Returns:
        Risk assessment dictionary
    """
    assessment = {
        "supplier_id": supplier_id,
        "overall_risk_score": 0,
        "risk_factors": [],
        "requires_human_review": False,
        "risk_level": "low"  # low, medium, high, critical
    }
    
    # 1. Region risk
    region_score, region_factors, region_review = assess_region_risk(region)
    assessment["overall_risk_score"] += region_score
    assessment["risk_factors"].extend(region_factors)
    assessment["requires_human_review"] = assessment["requires_human_review"] or region_review
    
    # 2. Emission deviation risk
    if claimed_co2e and benchmark_co2e:
        deviation = abs((claimed_co2e - benchmark_co2e) / benchmark_co2e) * 100
        
        if deviation > 50:
            assessment["overall_risk_score"] += 8
            assessment["risk_factors"].append(f"Extreme emission deviation: {deviation:.1f}%")
            assessment["requires_human_review"] = True
        elif deviation > 25:
            assessment["overall_risk_score"] += 5
            assessment["risk_factors"].append(f"High emission deviation: {deviation:.1f}%")
        
        # Suspiciously low emissions (potential greenwashing)
        if claimed_co2e < benchmark_co2e * 0.3:
            assessment["overall_risk_score"] += 6
            assessment["risk_factors"].append("Suspiciously low emissions (potential greenwashing)")
            assessment["requires_human_review"] = True
    
    # 3. Supplier ID pattern risk (basic check)
    if not supplier_id or len(supplier_id) < 5:
        assessment["overall_risk_score"] += 3
        assessment["risk_factors"].append("Invalid or missing supplier ID")
    
    # Determine risk level
    if assessment["overall_risk_score"] >= 15:
        assessment["risk_level"] = "critical"
        assessment["requires_human_review"] = True
    elif assessment["overall_risk_score"] >= 10:
        assessment["risk_level"] = "high"
        assessment["requires_human_review"] = True
    elif assessment["overall_risk_score"] >= 5:
        assessment["risk_level"] = "medium"
    else:
        assessment["risk_level"] = "low"
    
    return assessment


if __name__ == "__main__":
    # Test risk assessment
    print("Region Risk Assessment:")
    
    test_regions = [
        "Mumbai to Delhi",
        "Afghanistan to Pakistan",
        "Iran to UAE",
        "London to Paris"
    ]
    
    for region in test_regions:
        score, factors, review = assess_region_risk(region)
        print(f"\n  {region}:")
        print(f"    Risk Score: {score}")
        print(f"    Factors: {factors if factors else 'None'}")
        print(f"    Review Required: {review}")
    
    print("\n" + "="*60)
    print("Supplier Risk Assessment:")
    
    assessment = assess_supplier_risk(
        supplier_id="SUP-AF-2024-001",
        region="Kabul to Islamabad",
        claimed_co2e=50.0,
        benchmark_co2e=200.0
    )
    
    print(f"\n  Supplier: {assessment['supplier_id']}")
    print(f"  Overall Risk Score: {assessment['overall_risk_score']}")
    print(f"  Risk Level: {assessment['risk_level'].upper()}")
    print(f"  Review Required: {assessment['requires_human_review']}")
    print(f"  Risk Factors:")
    for factor in assessment['risk_factors']:
        print(f"    - {factor}")
