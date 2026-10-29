"""
Personalized Travel Itinerary Planner - Capstone Project.
Flask Application Entry Point.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

from services.ai_generator import generate_itinerary, is_api_key_configured
from services.budget_calculator import CURRENCY_RATES

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "travel_planner_capstone_dev_key")

# Curated popular destination suggestions
SAMPLE_DESTINATIONS = [
    {
        "name": "Tokyo",
        "country": "Japan",
        "tagline": "Neon lights, sacred shrines & legendary cuisine",
        "ideal_days": 5,
        "vibe": "Futuristic & Cultural",
        "image_keyword": "tokyo"
    },
    {
        "name": "Paris",
        "country": "France",
        "tagline": "World-class art, iconic architecture & sidewalk cafes",
        "ideal_days": 4,
        "vibe": "Romantic & Historic",
        "image_keyword": "paris"
    },
    {
        "name": "Bali",
        "country": "Indonesia",
        "tagline": "Emerald rice terraces, spiritual temples & ocean waves",
        "ideal_days": 6,
        "vibe": "Tropical & Relaxing",
        "image_keyword": "bali"
    },
    {
        "name": "Goa",
        "country": "India",
        "tagline": "Golden beaches, Portuguese heritage & coastal seafood",
        "ideal_days": 4,
        "vibe": "Beach & Culture",
        "image_keyword": "goa"
    },
    {
        "name": "Rome",
        "country": "Italy",
        "tagline": "Colosseum, cobblestone lanes & authentic gelato",
        "ideal_days": 4,
        "vibe": "Ancient History & Culinary",
        "image_keyword": "rome"
    },
    {
        "name": "New York City",
        "country": "USA",
        "tagline": "Broadway, Central Park, skyline views & vibrant boroughs",
        "ideal_days": 5,
        "vibe": "Metropolitan & Dynamic",
        "image_keyword": "new-york"
    }
]


@app.route("/")
def home():
    """Renders the main travel planner user interface."""
    return render_template(
        "index.html",
        api_configured=is_api_key_configured(),
        currencies=CURRENCY_RATES
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint returning server status and AI configuration mode.
    Useful for system diagnostic, tests, and frontend status indicators.
    """
    api_ready = is_api_key_configured()
    return jsonify({
        "status": "healthy",
        "mode": "live_ai" if api_ready else "demo_mode",
        "api_key_configured": api_ready,
        "message": (
            "Connected to Gemini AI for live itinerary generation."
            if api_ready
            else "Running in Demo Mode. Add GEMINI_API_KEY in .env for live AI."
        ),
        "supported_currencies": list(CURRENCY_RATES.keys())
    }), 200


@app.route("/api/sample-destinations", methods=["GET"])
def get_sample_destinations():
    """Returns curated destinations to help users quick-fill travel ideas."""
    return jsonify({
        "status": "success",
        "destinations": SAMPLE_DESTINATIONS
    }), 200


@app.route("/api/generate-itinerary", methods=["POST"])
def api_generate_itinerary():
    """
    Main API endpoint for personalized travel itinerary generation.
    Validates input parameters and orchestrates the AI or Demo engine.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "status": "error",
            "error": "Invalid request body. JSON payload is required."
        }), 400

    # 1. Input Validation
    destination = (data.get("destination") or "").strip()
    if not destination or len(destination) < 2:
        return jsonify({
            "status": "error",
            "error": "Please enter a valid destination name (minimum 2 characters)."
        }), 400

    if len(destination) > 80:
        return jsonify({
            "status": "error",
            "error": "Destination name is too long (maximum 80 characters)."
        }), 400

    try:
        duration_days = int(data.get("duration_days", 3))
        if duration_days < 1 or duration_days > 14:
            return jsonify({
                "status": "error",
                "error": "Trip duration must be between 1 and 14 days."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "error": "Trip duration must be a valid integer number of days."
        }), 400

    try:
        travelers_count = int(data.get("travelers_count", 1))
        if travelers_count < 1 or travelers_count > 20:
            return jsonify({
                "status": "error",
                "error": "Number of travelers must be between 1 and 20."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "error": "Number of travelers must be a valid number."
        }), 400

    budget_tier = (data.get("budget_tier") or "moderate").lower()
    if budget_tier not in ["budget", "moderate", "luxury"]:
        budget_tier = "moderate"

    currency = (data.get("currency") or "USD").upper()
    if currency not in CURRENCY_RATES:
        currency = "USD"

    pace = (data.get("pace") or "moderate").lower()
    if pace not in ["relaxed", "moderate", "fast-paced"]:
        pace = "moderate"

    interests = data.get("interests", [])
    if not isinstance(interests, list):
        interests = ["Culture & Heritage", "Food & Dining"]
    elif len(interests) == 0:
        interests = ["Culture & Heritage", "Sightseeing"]

    # 2. Invoke Generation Engine
    try:
        itinerary_result = generate_itinerary(
            destination=destination,
            duration_days=duration_days,
            travelers_count=travelers_count,
            budget_tier=budget_tier,
            currency=currency,
            interests=interests,
            pace=pace
        )
        return jsonify(itinerary_result), 200

    except Exception as exc:
        return jsonify({
            "status": "error",
            "error": f"An unexpected error occurred while generating the itinerary: {str(exc)}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("==================================================")
    print("TravelPlanner Capstone Server Starting...")
    print(f"Local URL: http://127.0.0.1:{port}")
    print(f"Gemini AI Status: {'Configured (Live AI)' if is_api_key_configured() else 'Demo Mode (Offline Fallback)'}")
    print("==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
