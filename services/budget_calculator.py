"""
Budget Calculator Service for TravelPlanner Capstone.
Provides rule-based estimation of accommodation, food, activities, and local transport
across multiple global currencies and traveler tiers.
"""

# Base currency conversion rates relative to USD (1 USD = X Currency)
CURRENCY_RATES = {
    "USD": {"symbol": "$", "rate": 1.0, "name": "US Dollar"},
    "INR": {"symbol": "₹", "rate": 83.5, "name": "Indian Rupee"},
    "EUR": {"symbol": "€", "rate": 0.92, "name": "Euro"},
    "GBP": {"symbol": "£", "rate": 0.79, "name": "British Pound"},
    "JPY": {"symbol": "¥", "rate": 155.0, "name": "Japanese Yen"},
    "AUD": {"symbol": "A$", "rate": 1.52, "name": "Australian Dollar"},
    "CAD": {"symbol": "C$", "rate": 1.36, "name": "Canadian Dollar"},
}

# Base daily cost per person in USD by tier
BASE_DAILY_USD = {
    "budget": {
        "stay": 35.0,        # Hostels, budget guesthouses
        "food": 20.0,        # Street food, markets, budget cafes
        "activities": 15.0,  # Free walking tours, public parks, historic sites
        "transport": 8.0,    # Subways, buses, shared rides
    },
    "moderate": {
        "stay": 95.0,        # 3-star hotels, private rentals
        "food": 50.0,        # Mid-range restaurants, local eateries
        "activities": 35.0,  # Museum passes, guided tours, attractions
        "transport": 22.0,   # Metro, occasional taxis, ride-hailing
    },
    "luxury": {
        "stay": 260.0,       # 4/5-star boutique hotels, resorts
        "food": 130.0,       # Fine dining, wine pairings, curated dining
        "activities": 90.0,  # Private guided tours, VIP access, special excursions
        "transport": 60.0,   # Private drivers, premium taxis, express transfers
    }
}

# Regional destination cost multipliers
DESTINATION_WEIGHTS = {
    # High-cost destinations
    "tokyo": 1.25,
    "paris": 1.35,
    "new york": 1.45,
    "london": 1.40,
    "zurich": 1.60,
    "singapore": 1.30,
    "dubai": 1.25,
    "sydney": 1.25,
    
    # Moderate-cost destinations
    "rome": 1.10,
    "barcelona": 1.05,
    "berlin": 1.05,
    "seoul": 1.00,
    "bangkok": 0.65,
    "bali": 0.60,
    "phuket": 0.65,
    "istanbul": 0.70,

    # Budget-friendly destinations
    "goa": 0.50,
    "delhi": 0.45,
    "jaipur": 0.45,
    "mumbai": 0.60,
    "hanoi": 0.50,
    "cairo": 0.55,
    "kathmandu": 0.40,
}

def get_destination_weight(destination_name: str) -> float:
    """Finds regional cost multiplier based on destination keyword match."""
    if not destination_name:
        return 1.0
    dest_lower = destination_name.lower().strip()
    for key, weight in DESTINATION_WEIGHTS.items():
        if key in dest_lower:
            return weight
    return 1.0  # Default baseline


def calculate_budget_breakdown(
    destination: str,
    duration_days: int,
    travelers_count: int,
    budget_tier: str = "moderate",
    currency: str = "USD",
    pace: str = "moderate"
) -> dict:
    """
    Computes an itemized trip budget breakdown.
    
    Returns structured cost data and explicit unverified estimation labels.
    """
    tier = budget_tier.lower() if budget_tier.lower() in BASE_DAILY_USD else "moderate"
    curr = currency.upper() if currency.upper() in CURRENCY_RATES else "USD"
    curr_info = CURRENCY_RATES[curr]
    rate = curr_info["rate"]
    symbol = curr_info["symbol"]

    # Clamp days and travelers to realistic bounds
    days = max(1, min(int(duration_days or 1), 30))
    travelers = max(1, min(int(travelers_count or 1), 20))

    dest_weight = get_destination_weight(destination)

    # Pace modifiers: fast pace increases activity/transport costs; relaxed decreases
    pace_lower = (pace or "moderate").lower()
    activity_pace_mod = 1.25 if pace_lower == "fast-paced" else (0.85 if pace_lower == "relaxed" else 1.0)
    transport_pace_mod = 1.20 if pace_lower == "fast-paced" else (0.90 if pace_lower == "relaxed" else 1.0)

    base = BASE_DAILY_USD[tier]

    # Calculate USD totals
    # Room sharing: 2 travelers share 1 room; 3-4 share 2 rooms
    rooms_needed = max(1, (travelers + 1) // 2)
    stay_usd = (base["stay"] * 1.5) * rooms_needed * days * dest_weight
    food_usd = base["food"] * travelers * days * dest_weight
    activities_usd = base["activities"] * travelers * days * dest_weight * activity_pace_mod
    transport_usd = base["transport"] * travelers * days * dest_weight * transport_pace_mod

    # Apply currency conversion
    stay_local = round(stay_usd * rate)
    food_local = round(food_usd * rate)
    activities_local = round(activities_usd * rate)
    transport_local = round(transport_usd * rate)
    grand_total_local = stay_local + food_local + activities_local + transport_local
    daily_avg_local = round(grand_total_local / days) if days > 0 else grand_total_local

    return {
        "currency_code": curr,
        "currency_symbol": symbol,
        "currency_name": curr_info["name"],
        "budget_tier": tier.capitalize(),
        "travelers_count": travelers,
        "duration_days": days,
        "stay_total": stay_local,
        "food_total": food_local,
        "activities_total": activities_local,
        "transport_total": transport_local,
        "grand_total": grand_total_local,
        "daily_average": daily_avg_local,
        "is_estimate": True,
        "disclaimer": "Budget figures are estimated approximations based on typical local costs and travel style. Flights, visa fees, and personal shopping are not included. Local prices fluctuate by season."
    }
