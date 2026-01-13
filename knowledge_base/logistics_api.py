"""
Mock Logistics API for emission benchmarking.
Simulates real logistics provider APIs with realistic CO2e benchmarks.
"""

import random
from typing import Optional, Dict


# Emission factors (kg CO2e per ton-km) by transport mode
# Based on typical industry averages
EMISSION_FACTORS = {
    "air": 0.602,      # Air freight
    "sea": 0.016,      # Sea freight
    "road": 0.096,     # Road freight (truck)
    "rail": 0.028,     # Rail freight
}

# Route-specific adjustments (simulating real-world variance)
ROUTE_ADJUSTMENTS = {
    "domestic": 1.0,
    "international": 1.15,
    "express": 1.3,
}


class MockLogisticsAPI:
    """Mock logistics API for emission benchmarking."""
    
    @staticmethod
    def get_benchmark_emissions(
        transport_mode: str,
        weight_kg: float,
        distance_km: float,
        route_type: str = "domestic"
    ) -> Dict[str, float]:
        """
        Calculate benchmark CO2e emissions for a shipment.
        
        Args:
            transport_mode: Mode of transport (air, sea, road, rail)
            weight_kg: Shipment weight in kilograms
            distance_km: Distance in kilometers
            route_type: Route classification (domestic, international, express)
            
        Returns:
            Dictionary with benchmark_co2e and confidence
        """
        # Normalize inputs
        transport_mode = transport_mode.lower() if transport_mode else "road"
        route_type = route_type.lower() if route_type else "domestic"
        
        # Get emission factor
        emission_factor = EMISSION_FACTORS.get(transport_mode, EMISSION_FACTORS["road"])
        
        # Get route adjustment
        route_adjustment = ROUTE_ADJUSTMENTS.get(route_type, 1.0)
        
        # Calculate base emissions (convert kg to tons)
        weight_tons = weight_kg / 1000.0
        base_emissions = emission_factor * weight_tons * distance_km
        
        # Apply route adjustment
        adjusted_emissions = base_emissions * route_adjustment
        
        # Add realistic variance (±5%)
        variance = random.uniform(0.95, 1.05)
        final_emissions = adjusted_emissions * variance
        
        # Calculate confidence based on data quality
        confidence = 0.85 if transport_mode in EMISSION_FACTORS else 0.60
        
        return {
            "benchmark_co2e": round(final_emissions, 2),
            "confidence": confidence,
            "emission_factor": emission_factor,
            "transport_mode": transport_mode
        }
    
    @staticmethod
    def validate_route(origin: str, destination: str) -> bool:
        """
        Validate if a route exists (mock implementation).
        In production, this would check against real logistics databases.
        """
        # Simple mock: always return True if both are provided
        return bool(origin and destination)


# Singleton instance
logistics_api = MockLogisticsAPI()
