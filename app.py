"""
Personalized Travel Itinerary Planner - Capstone Project.
Flask Application Entry Point.
Provides REST APIs for itinerary generation, destination exploration, and live weather.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

from services.ai_generator import generate_itinerary, is_api_key_configured
from services.budget_calculator import CURRENCY_RATES
from services.weather_service import get_destination_weather

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "travel_planner_capstone_dev_key")

# Comprehensive Curated Destination Explorer Database
SAMPLE_DESTINATIONS = [
    {
        "id": "tokyo",
        "name": "Tokyo",
        "country": "Japan",
        "continent": "Asia",
        "tagline": "Neon lights, sacred shrines & legendary culinary culture",
        "description": "A dazzling metropolis blending ancient temples like Senso-ji with hyper-modern districts like Shibuya and Akihabara.",
        "popular_attractions": ["Senso-ji Temple", "Shibuya Crossing", "Meiji Shrine", "Tsukiji Outer Market"],
        "ideal_days": 5,
        "best_time": "March - May & Oct - Nov",
        "vibe": "Futuristic & Cultural",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "paris",
        "name": "Paris",
        "country": "France",
        "continent": "Europe",
        "tagline": "World-class art, iconic architecture & boulevard cafes",
        "description": "The City of Light captivates with the Eiffel Tower, the Louvre museum masterpieces, and romantic walks along the Seine River.",
        "popular_attractions": ["Eiffel Tower", "Louvre Museum", "Montmartre", "Seine River Cruise"],
        "ideal_days": 4,
        "best_time": "April - June & Sept - Oct",
        "vibe": "Romantic & Historic",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "bali",
        "name": "Bali",
        "country": "Indonesia",
        "continent": "Asia",
        "tagline": "Emerald rice terraces, spiritual temples & ocean waves",
        "description": "An island paradise boasting cliffside temples at Uluwatu, lush Ubud jungle walks, surfing breaks, and peaceful yoga retreats.",
        "popular_attractions": ["Tegallalang Terraces", "Uluwatu Temple", "Ubud Monkey Forest", "Canggu Beach"],
        "ideal_days": 6,
        "best_time": "May - September",
        "vibe": "Tropical & Relaxing",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "goa",
        "name": "Goa",
        "country": "India",
        "continent": "Asia",
        "tagline": "Golden beaches, Portuguese heritage & coastal seafood",
        "description": "India's beach haven offering colorful Latin quarter villas in Fontainhas, historic cathedrals, water sports, and sunset beach shacks.",
        "popular_attractions": ["Fontainhas Latin Quarter", "Basilica of Bom Jesus", "Calangute Beach", "Dudhsagar Falls"],
        "ideal_days": 4,
        "best_time": "November - February",
        "vibe": "Beach & Culture",
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "rome",
        "name": "Rome",
        "country": "Italy",
        "continent": "Europe",
        "tagline": "Colosseum, cobblestone lanes & authentic gelato",
        "description": "An open-air museum where ancient history comes alive at the Roman Colosseum, Trevi Fountain, and Pantheon.",
        "popular_attractions": ["Colosseum & Forum", "Trevi Fountain", "Pantheon", "Trastevere Piazzas"],
        "ideal_days": 4,
        "best_time": "April - May & Sept - Oct",
        "vibe": "Ancient History & Culinary",
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "new-york",
        "name": "New York City",
        "country": "USA",
        "continent": "North America",
        "tagline": "Broadway, Central Park, skyline views & vibrant boroughs",
        "description": "The city that never sleeps offers towering skyscrapers, world-renowned Broadway theaters, Central Park trails, and diverse food neighborhoods.",
        "popular_attractions": ["Central Park", "Times Square", "Brooklyn Bridge", "High Line Elevated Park"],
        "ideal_days": 5,
        "best_time": "Sept - Nov & May - June",
        "vibe": "Metropolitan & Dynamic",
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "london",
        "name": "London",
        "country": "United Kingdom",
        "continent": "Europe",
        "tagline": "Historic royalty, British museums & Thames riverside walks",
        "description": "Experience centuries of heritage at Big Ben and Tower Bridge, explore free national museums, and stroll lively Covent Garden.",
        "popular_attractions": ["Big Ben & Parliament", "British Museum", "Tower Bridge", "Covent Garden"],
        "ideal_days": 5,
        "best_time": "May - September",
        "vibe": "Royal & Cosmopolitan",
        "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "dubai",
        "name": "Dubai",
        "country": "United Arab Emirates",
        "continent": "Middle East",
        "tagline": "Futuristic skyline, luxury shopping & desert safaris",
        "description": "A dazzling desert city featuring the world's tallest tower (Burj Khalifa), vast artificial islands, and golden sand dunes.",
        "popular_attractions": ["Burj Khalifa", "Dubai Mall & Fountain", "Dubai Marina", "Desert Safari"],
        "ideal_days": 4,
        "best_time": "November - March",
        "vibe": "Luxury & Innovation",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "jaipur",
        "name": "Jaipur",
        "country": "India",
        "continent": "Asia",
        "tagline": "Pink City palaces, grand forts & royal Rajasthani heritage",
        "description": "The capital of Rajasthan, famous for the intricately carved Hawa Mahal, hilltop Amber Fort, and bustling gemstone bazaars.",
        "popular_attractions": ["Hawa Mahal", "Amber Fort", "City Palace", "Johari Bazaar"],
        "ideal_days": 3,
        "best_time": "October - March",
        "vibe": "Royal & Heritage",
        "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "barcelona",
        "name": "Barcelona",
        "country": "Spain",
        "continent": "Europe",
        "tagline": "Gaudí architecture, Mediterranean beaches & tapas bars",
        "description": "Catalonia's coastal crown jewel, celebrated for the Sagrada Família, whimsical Park Güell, and vibrant nightlife along Las Ramblas.",
        "popular_attractions": ["Sagrada Família", "Park Güell", "Gothic Quarter", "Barceloneta Beach"],
        "ideal_days": 4,
        "best_time": "May - June & Sept - Oct",
        "vibe": "Artistic & Coastal",
        "image_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "singapore",
        "name": "Singapore",
        "country": "Singapore",
        "continent": "Asia",
        "tagline": "Garden city wonders, hawker street food & skyline infinity pools",
        "description": "A green global hub renowned for the futuristic Supertree Grove at Gardens by the Bay, Marina Bay Sands, and Chinatown food stalls.",
        "popular_attractions": ["Gardens by the Bay", "Marina Bay Sands", "Sentosa Island", "Chinatown Hawkers"],
        "ideal_days": 4,
        "best_time": "Year-round",
        "vibe": "Green & Futuristic",
        "image_url": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "sydney",
        "name": "Sydney",
        "country": "Australia",
        "continent": "Oceania",
        "tagline": "Harbour bridge climbs, iconic Opera House & Bondi surf",
        "description": "Australia's picturesque coastal gem famous for its world-renowned Opera House, sparkling blue harbor, and scenic coastal walks.",
        "popular_attractions": ["Sydney Opera House", "Harbour Bridge", "Bondi to Coogee Walk", "The Rocks"],
        "ideal_days": 5,
        "best_time": "September - November & March - May",
        "vibe": "Coastal & Active",
        "image_url": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=800&q=80"
    }
]


@app.route("/")
def home():
    """Renders the main travel planner user interface."""
    return render_template(
        "index.html",
        api_configured=is_api_key_configured(),
        currencies=CURRENCY_RATES,
        destinations=SAMPLE_DESTINATIONS
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
    """
    Returns curated destinations with support for search keyword filtering.
    Usage: /api/sample-destinations or /api/sample-destinations?q=beach
    """
    query = (request.args.get("q") or "").strip().lower()
    if not query:
        return jsonify({
            "status": "success",
            "count": len(SAMPLE_DESTINATIONS),
            "destinations": SAMPLE_DESTINATIONS
        }), 200

    filtered = [
        d for d in SAMPLE_DESTINATIONS
        if query in d["name"].lower()
        or query in d["country"].lower()
        or query in d["vibe"].lower()
        or query in d["tagline"].lower()
    ]
    return jsonify({
        "status": "success",
        "count": len(filtered),
        "destinations": filtered
    }), 200


@app.route("/api/weather", methods=["GET"])
def api_destination_weather():
    """
    Dedicated endpoint for live Open-Meteo weather data.
    Usage: /api/weather?destination=Tokyo
    """
    dest = (request.args.get("destination") or "").strip()
    if not dest:
        return jsonify({
            "status": "error",
            "error": "Destination parameter is required."
        }), 400

    weather_data = get_destination_weather(dest)
    return jsonify(weather_data), 200


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
