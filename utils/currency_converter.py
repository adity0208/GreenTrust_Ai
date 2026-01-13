"""
Currency and unit conversion utilities for edge cases.
"""

# Static exchange rates for demo (as of Jan 2026)
EXCHANGE_RATES = {
    "EUR": 89.50,  # EUR to INR
    "USD": 83.25,  # USD to INR
    "GBP": 105.30,  # GBP to INR
    "INR": 1.0
}

# Weight conversion factors
WEIGHT_CONVERSIONS = {
    "kg": 1.0,
    "tons": 1000.0,
    "metric_tons": 1000.0,
    "lbs": 0.453592,
    "pounds": 0.453592
}

# Distance conversion factors
DISTANCE_CONVERSIONS = {
    "km": 1.0,
    "kilometers": 1.0,
    "miles": 1.60934,
    "nautical_miles": 1.852
}


def convert_currency(amount: float, from_currency: str, to_currency: str = "INR") -> float:
    """
    Convert currency amount.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (EUR, USD, GBP, INR)
        to_currency: Target currency code (default: INR)
        
    Returns:
        Converted amount
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {from_currency}")
    
    if to_currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {to_currency}")
    
    # Convert to INR first, then to target currency
    inr_amount = amount * EXCHANGE_RATES[from_currency]
    result = inr_amount / EXCHANGE_RATES[to_currency]
    
    return round(result, 2)


def convert_weight(amount: float, from_unit: str, to_unit: str = "kg") -> float:
    """
    Convert weight units.
    
    Args:
        amount: Weight amount
        from_unit: Source unit (kg, tons, lbs, etc.)
        to_unit: Target unit (default: kg)
        
    Returns:
        Converted weight
    """
    from_unit = from_unit.lower().replace(" ", "_")
    to_unit = to_unit.lower().replace(" ", "_")
    
    if from_unit not in WEIGHT_CONVERSIONS:
        raise ValueError(f"Unsupported weight unit: {from_unit}")
    
    if to_unit not in WEIGHT_CONVERSIONS:
        raise ValueError(f"Unsupported weight unit: {to_unit}")
    
    # Convert to kg first, then to target unit
    kg_amount = amount * WEIGHT_CONVERSIONS[from_unit]
    result = kg_amount / WEIGHT_CONVERSIONS[to_unit]
    
    return round(result, 2)


def convert_distance(amount: float, from_unit: str, to_unit: str = "km") -> float:
    """
    Convert distance units.
    
    Args:
        amount: Distance amount
        from_unit: Source unit (km, miles, etc.)
        to_unit: Target unit (default: km)
        
    Returns:
        Converted distance
    """
    from_unit = from_unit.lower().replace(" ", "_")
    to_unit = to_unit.lower().replace(" ", "_")
    
    if from_unit not in DISTANCE_CONVERSIONS:
        raise ValueError(f"Unsupported distance unit: {from_unit}")
    
    if to_unit not in DISTANCE_CONVERSIONS:
        raise ValueError(f"Unsupported distance unit: {to_unit}")
    
    # Convert to km first, then to target unit
    km_amount = amount * DISTANCE_CONVERSIONS[from_unit]
    result = km_amount / DISTANCE_CONVERSIONS[to_unit]
    
    return round(result, 2)


if __name__ == "__main__":
    # Test conversions
    print("Currency Conversions:")
    print(f"  100 EUR = {convert_currency(100, 'EUR', 'INR')} INR")
    print(f"  100 USD = {convert_currency(100, 'USD', 'INR')} INR")
    
    print("\nWeight Conversions:")
    print(f"  5 tons = {convert_weight(5, 'tons', 'kg')} kg")
    print(f"  1000 lbs = {convert_weight(1000, 'lbs', 'kg')} kg")
    
    print("\nDistance Conversions:")
    print(f"  100 miles = {convert_distance(100, 'miles', 'km')} km")
    print(f"  50 nautical_miles = {convert_distance(50, 'nautical_miles', 'km')} km")
