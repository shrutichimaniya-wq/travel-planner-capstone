"""
AI Generator Service for TravelPlanner Capstone.
Connects securely to Google Gemini API using server-side environment variables.
Provides structured prompt engineering, JSON response formatting, and graceful
fallback to Demo Mode when no API key is provided or when API errors occur.
"""

import os
import json
import logging
import requests
from services.budget_calculator import calculate_budget_breakdown, CURRENCY_RATES
from services.demo_generator import build_fallback_itinerary

logger = logging.getLogger(__name__)

# Primary and fallback Gemini models
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash"
]

def is_api_key_configured() -> bool:
    """Checks whether a valid, non-placeholder GEMINI_API_KEY is present in the environment."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    placeholder_values = ["", "your_gemini_api_key_here", "your_api_key", "none"]
    return bool(api_key and api_key.lower() not in placeholder_values)


def generate_itinerary(
    destination: str,
    duration_days: int,
    travelers_count: int,
    budget_tier: str = "moderate",
    currency: str = "USD",
    interests: list = None,
    pace: str = "moderate"
) -> dict:
    """
    Main entry point for generating travel itineraries.
    Attempts live AI personalization via Gemini API; gracefully falls back to Demo Mode.
    """
    interests = interests or ["Culture & Heritage", "Food & Dining"]
    curr = currency.upper() if currency.upper() in CURRENCY_RATES else "USD"
    curr_info = CURRENCY_RATES[curr]
    curr_rate = curr_info["rate"]
    curr_sym = curr_info["symbol"]

    # 1. Check if Gemini API key is configured
    if not is_api_key_configured():
        logger.info("GEMINI_API_KEY not configured. Falling back to curated Demo Mode.")
        return build_fallback_itinerary(
            destination=destination,
            duration_days=duration_days,
            travelers_count=travelers_count,
            budget_tier=budget_tier,
            currency=curr,
            interests=interests,
            pace=pace
        )

    api_key = os.environ.get("GEMINI_API_KEY").strip()

    # 2. Build structured prompt for Gemini
    system_instruction = (
        "You are an expert travel consultant. Generate an authentic, realistic day-by-day travel itinerary. "
        "Adhere strictly to the requested pace, budget tier, and user interests. "
        "CRITICAL: Do not fabricate verified opening hours or guaranteed live prices. Label all costs as approximations. "
        "Output ONLY raw valid JSON conforming to the requested schema, without markdown formatting or code blocks."
    )

    user_prompt = f"""
Create a detailed {duration_days}-day travel itinerary for {destination} with the following preferences:
- Travelers: {travelers_count} person(s)
- Budget Tier: {budget_tier}
- Currency: {curr} ({curr_sym})
- Selected Interests: {', '.join(interests)}
- Travel Pace: {pace}

Return a valid JSON object matching this exact structure:
{{
  "trip_title": "Inspiring trip title",
  "trip_overview": "3-4 sentence comprehensive overview of the destination and trip vibe",
  "best_time_to_visit": "Best seasons or months with brief weather rationale",
  "packing_recommendations": "4-5 essential packing tips tailored to this trip and climate",
  "itinerary_days": [
    {{
      "day_number": 1,
      "theme": "Theme of Day 1",
      "activities": [
        {{
          "time_slot": "Morning",
          "time_range": "09:00 AM - 12:00 PM",
          "activity_name": "Specific landmark or activity name",
          "description": "2-3 sentences explaining what makes this memorable and practical tips",
          "location": "District or specific neighborhood",
          "category": "Culture, Food, Adventure, Nature, Sightseeing, or Relaxation",
          "estimated_cost_local": 25
        }}
      ]
    }}
  ]
}}

Provide activities for each day: Morning, Afternoon, Evening, and Night (if fast-paced, include Night; if relaxed, keep it to 3 activities per day).
All activity costs in 'estimated_cost_local' must be realistic integer approximations in {curr}.
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.95,
            "responseMimeType": "application/json"
        }
    }

    # 3. Call Gemini REST API
    last_error_msg = None
    for model_name in GEMINI_MODELS:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            response = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=25
            )

            if response.status_code == 200:
                result_data = response.json()
                raw_text = (
                    result_data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                
                # Parse JSON
                parsed_itinerary = json.loads(raw_text)

                # Format activities with formatted currency display
                for day in parsed_itinerary.get("itinerary_days", []):
                    for act in day.get("activities", []):
                        cost_num = act.get("estimated_cost_local", 0)
                        act["estimated_cost_raw"] = cost_num
                        act["estimated_cost_display"] = f"{curr_sym}{cost_num:,}"
                        act["unverified_notice"] = "Estimated activity cost; verify local opening hours and ticket availability before visiting."

                # Calculate itemized budget
                budget_breakdown = calculate_budget_breakdown(
                    destination=destination,
                    duration_days=duration_days,
                    travelers_count=travelers_count,
                    budget_tier=budget_tier,
                    currency=curr,
                    pace=pace
                )

                return {
                    "status": "success",
                    "is_demo": False,
                    "generation_source": f"Google Gemini ({model_name})",
                    "mode_badge": "Live Gemini AI Generated",
                    "mode_badge_class": "badge-live-ai",
                    "mode_explanation": "This personalized itinerary was dynamically synthesized in real-time by Google Gemini AI according to your custom preferences.",
                    "trip_title": parsed_itinerary.get("trip_title", f"{duration_days}-Day Journey to {destination.title()}"),
                    "destination": destination.title(),
                    "duration_days": duration_days,
                    "travelers_count": travelers_count,
                    "budget_tier": budget_tier.capitalize(),
                    "pace": pace.capitalize(),
                    "trip_overview": parsed_itinerary.get("trip_overview", ""),
                    "best_time_to_visit": parsed_itinerary.get("best_time_to_visit", ""),
                    "packing_recommendations": parsed_itinerary.get("packing_recommendations", ""),
                    "itinerary_days": parsed_itinerary.get("itinerary_days", []),
                    "budget_breakdown": budget_breakdown,
                    "disclaimers": [
                        "All pricing, entrance fees, and meal costs are approximations for planning purposes only.",
                        "Opening hours, availability, and public transit schedules change seasonally; always confirm directly with local providers.",
                        "Live weather, bookings, and ticket availability are not guaranteed in this itinerary estimate."
                    ]
                }
            else:
                last_error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(f"Gemini API returned error with model {model_name}: {last_error_msg}")

        except Exception as e:
            last_error_msg = str(e)
            logger.warning(f"Gemini API request failed for {model_name}: {e}")

    # If all API attempts fail, fall back to Demo Mode with transparent notice
    fallback_result = build_fallback_itinerary(
        destination=destination,
        duration_days=duration_days,
        travelers_count=travelers_count,
        budget_tier=budget_tier,
        currency=curr,
        interests=interests,
        pace=pace
    )
    fallback_result["mode_badge"] = "Demo Mode (API Fallback)"
    fallback_result["mode_explanation"] = (
        f"Real AI request could not be completed ({last_error_msg or 'API unreachable'}). "
        "The application safely fell back to our curated offline travel database so your experience was uninterrupted."
    )
    return fallback_result
