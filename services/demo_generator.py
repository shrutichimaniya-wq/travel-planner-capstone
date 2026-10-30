"""
Demo Generator Service for TravelPlanner Capstone.
Provides rich, realistic, curated offline itineraries when no Gemini API key is configured.
Strictly labelled as demo mode to adhere to capstone integrity guidelines.
Now includes geographic coordinates for Leaflet Interactive Maps and Open-Meteo weather integration.
"""

import random
from services.budget_calculator import calculate_budget_breakdown, CURRENCY_RATES
from services.weather_service import get_destination_weather, geocode_destination

# Curated destination database with authentic sights, coordinates, culinary spots, and experiences
CURATED_DESTINATIONS = {
    "tokyo": {
        "title": "Vibrant Tokyo: Neon Lights, Ancient Shrines & Culinary Wonders",
        "best_time": "March to May (Cherry Blossoms) or October to November (Autumn Foliage)",
        "packing_tips": "Comfortable walking shoes, universal power adapter, IC transit card, light jacket.",
        "coordinates": {"lat": 35.6762, "lon": 139.6503},
        "highlights": ["Senso-ji Temple", "Shibuya Crossing", "Shinjuku Gyoen", "Akihabara", "Tsukiji Outer Market", "Meiji Shrine", "TeamLab Planets"],
        "pool": [
            {
                "title": "Visit Historic Senso-ji Temple & Nakamise Shopping Street",
                "desc": "Tokyo's oldest Buddhist temple. Stroll traditional stalls selling freshly baked melonpan and handcrafted souvenirs.",
                "location": "Asakusa, Taito City",
                "category": "Culture & Heritage",
                "base_cost_usd": 10,
                "lat": 35.7148,
                "lon": 139.7967
            },
            {
                "title": "Tsukiji Outer Market Food & Street Tasting Tour",
                "desc": "Sample freshly grilled seafood skewers, tamagoyaki rolled omelet, and premium tuna sashimi from heritage stalls.",
                "location": "Tsukiji, Chuo City",
                "category": "Food & Dining",
                "base_cost_usd": 28,
                "lat": 35.6655,
                "lon": 139.7708
            },
            {
                "title": "Meiji Jingu Shrine & Harajuku Takeshita Street",
                "desc": "Experience the peaceful cedar forest surrounding Emperor Meiji's shrine, then contrast with Harajuku's vibrant youth culture.",
                "location": "Shibuya City",
                "category": "Culture & Shopping",
                "base_cost_usd": 12,
                "lat": 35.6764,
                "lon": 139.6993
            },
            {
                "title": "Shibuya Sky Observation Deck & Famous Scramble Crossing",
                "desc": "Catch a 360-degree sunset over the Tokyo metropolis from Shibuya Sky rooftop, then walk the iconic pedestrian crossing.",
                "location": "Shibuya, Tokyo",
                "category": "Sightseeing",
                "base_cost_usd": 22,
                "lat": 35.6595,
                "lon": 139.7005
            },
            {
                "title": "TeamLab Planets Digital Art Immersion",
                "desc": "Walk barefoot through sensory water pools and infinite crystal gardens in this interactive digital art museum.",
                "location": "Toyosu, Koto City",
                "category": "Adventure & Art",
                "base_cost_usd": 32,
                "lat": 35.6491,
                "lon": 139.7898
            },
            {
                "title": "Shinjuku Omoide Yokocho & Golden Gai Izakaya Walk",
                "desc": "Discover tiny heritage alleyway taverns serving charcoal-grilled yakitori and craft Japanese beer under warm paper lanterns.",
                "location": "Shinjuku, Tokyo",
                "category": "Food & Nightlife",
                "base_cost_usd": 35,
                "lat": 35.6928,
                "lon": 139.7001
            },
            {
                "title": "Akihabara Electric Town & Retro Gaming Arcade",
                "desc": "Browse multi-story anime, retro electronics, and vintage gaming arcades in Tokyo's world-famous subculture capital.",
                "location": "Chiyoda City",
                "category": "Shopping & Pop Culture",
                "base_cost_usd": 15,
                "lat": 35.6983,
                "lon": 139.7731
            },
            {
                "title": "Relaxing Walk in Shinjuku Gyoen National Garden",
                "desc": "Wander through landscaped Japanese traditional, French Formal, and English Landscape gardens.",
                "location": "Shinjuku / Shibuya",
                "category": "Nature & Relaxation",
                "base_cost_usd": 5,
                "lat": 35.6852,
                "lon": 139.7101
            }
        ]
    },
    "paris": {
        "title": "Romantic Paris: Architectural Marvels, Art & Boulevard Cafes",
        "best_time": "April to June or September to October (Mild weather, fewer crowds)",
        "packing_tips": "Chic comfortable footwear, compact umbrella, daypack, offline Metro map.",
        "coordinates": {"lat": 48.8566, "lon": 2.3522},
        "highlights": ["Eiffel Tower", "Louvre Museum", "Montmartre", "Seine River Cruise", "Le Marais", "Sainte-Chapelle"],
        "pool": [
            {
                "title": "Morning Coffee & Fresh Croissant in the Latin Quarter",
                "desc": "Start with espresso and warm pain au chocolat at a pavement terrace overlooking historic university squares.",
                "location": "5th Arrondissement, Paris",
                "category": "Food & Dining",
                "base_cost_usd": 12,
                "lat": 48.8499,
                "lon": 2.3444
            },
            {
                "title": "Louvre Museum Masterpieces & Tuileries Garden",
                "desc": "Marvel at the Mona Lisa and Venus de Milo before strolling through the royal marble sculptures of Tuileries.",
                "location": "Rue de Rivoli",
                "category": "Culture & Heritage",
                "base_cost_usd": 24,
                "lat": 48.8606,
                "lon": 2.3376
            },
            {
                "title": "Sunset Cruise on the Seine River",
                "desc": "Glide past illuminated bridges, Notre-Dame Cathedral, and the Musée d'Orsay aboard a scenic river cruiser.",
                "location": "Pont de l'Alma Dock",
                "category": "Sightseeing",
                "base_cost_usd": 20,
                "lat": 48.8635,
                "lon": 2.3015
            },
            {
                "title": "Montmartre Bohemian Walk & Sacré-Cœur Basilica",
                "desc": "Climb cobblestone alleys where artists once painted and enjoy panoramic sunset views overlooking Paris.",
                "location": "18th Arrondissement",
                "category": "Culture & Sightseeing",
                "base_cost_usd": 8,
                "lat": 48.8867,
                "lon": 2.3431
            },
            {
                "title": "Eiffel Tower Summit & Trocadéro Gardens",
                "desc": "Ascend to the summit level for panoramic vistas across the Champ de Mars and surrounding Parisian boulevards.",
                "location": "Champ de Mars",
                "category": "Sightseeing",
                "base_cost_usd": 35,
                "lat": 48.8584,
                "lon": 2.2945
            },
            {
                "title": "Vintage Boutiques & Pastry Crawl in Le Marais",
                "desc": "Explore 17th-century aristocratic mansions, independent art galleries, and famous Parisian falafel and bakeries.",
                "location": "4th Arrondissement",
                "category": "Shopping & Food",
                "base_cost_usd": 25,
                "lat": 48.8575,
                "lon": 2.3622
            }
        ]
    },
    "bali": {
        "title": "Enchanting Bali: Lush Rice Terraces, Ancient Temples & Coastline Sunsets",
        "best_time": "May to September (Dry season with low humidity and optimal surf)",
        "packing_tips": "Breathable linen clothing, temple sarong, mosquito repellent, reef-safe sunscreen.",
        "coordinates": {"lat": -8.4095, "lon": 115.1889},
        "highlights": ["Tegallalang Rice Terraces", "Uluwatu Temple", "Ubud Monkey Forest", "Canggu Beach", "Tirta Empul"],
        "pool": [
            {
                "title": "Sunrise Walk at Tegallalang Rice Terraces",
                "desc": "Hike the UNESCO-listed emerald subak irrigation terraces amidst morning mist and coconut palms.",
                "location": "Ubud, Gianyar",
                "category": "Nature & Adventure",
                "base_cost_usd": 15,
                "lat": -8.4310,
                "lon": 115.2780
            },
            {
                "title": "Sacred Monkey Forest Sanctuary & Ubud Market",
                "desc": "Walk shaded mossy paths surrounded by playful macaques and browse handmade rattan bags and batik silks.",
                "location": "Padangtegal, Ubud",
                "category": "Nature & Culture",
                "base_cost_usd": 12,
                "lat": -8.5188,
                "lon": 115.2588
            },
            {
                "title": "Balinese Cooking Class & Organic Farm Lunch",
                "desc": "Grind fresh galangal, lemongrass, and turmeric to prepare authentic chicken satay lilit and sambal matah.",
                "location": "Central Ubud",
                "category": "Food & Dining",
                "base_cost_usd": 30,
                "lat": -8.5069,
                "lon": 115.2625
            },
            {
                "title": "Cliffside Uluwatu Temple & Kecak Fire Dance",
                "desc": "Perched 70 meters above crashing waves, watch hypnotic choir chanting as the sun sinks into the Indian Ocean.",
                "location": "Pecatu, South Kuta",
                "category": "Culture & Sightseeing",
                "base_cost_usd": 18,
                "lat": -8.8291,
                "lon": 115.0849
            },
            {
                "title": "Canggu Beach Sunset Lounge & Surfing",
                "desc": "Watch surfers catch evening waves from a relaxed beachfront lounge with fresh chilled coconut water.",
                "location": "Echo Beach, Canggu",
                "category": "Relaxation & Nightlife",
                "base_cost_usd": 20,
                "lat": -8.6500,
                "lon": 115.1333
            }
        ]
    },
    "goa": {
        "title": "Sunny Goa: Golden Beaches, Portuguese Heritage & Spice Plantations",
        "best_time": "November to February (Pleasant coastal breezes and lively beach shacks)",
        "packing_tips": "Swimwear, sunglasses, flip flops, light cottons, sunscreen.",
        "coordinates": {"lat": 15.2993, "lon": 74.1240},
        "highlights": ["Fontainhas Latin Quarter", "Anjuna Flea Market", "Old Goa Churches", "Dudhsagar Waterfalls", "Palolem Beach"],
        "pool": [
            {
                "title": "Heritage Walk through Fontainhas Latin Quarter",
                "desc": "Stroll brightly painted Portuguese-colonial villas with terracotta roofs and sample warm Goan bebinca pastries.",
                "location": "Panaji, North Goa",
                "category": "Culture & History",
                "base_cost_usd": 8,
                "lat": 15.4989,
                "lon": 73.8278
            },
            {
                "title": "Basilica of Bom Jesus & Se Cathedral Exploration",
                "desc": "Explore 16th-century UNESCO World Heritage architecture holding the sacred relics of St. Francis Xavier.",
                "location": "Old Goa",
                "category": "Culture & Heritage",
                "base_cost_usd": 5,
                "lat": 15.5009,
                "lon": 73.9116
            },
            {
                "title": "Authentic Coastal Goan Fish Curry Thali Lunch",
                "desc": "Indulge in kingfish curry cooked with coconut milk, kokum, fried prawns, and warm poi bread.",
                "location": "Rua 31 de Janeiro, Panjim",
                "category": "Food & Dining",
                "base_cost_usd": 12,
                "lat": 15.4950,
                "lon": 73.8310
            },
            {
                "title": "Watersports & Sunset Shack at Calangute / Baga",
                "desc": "Try parasailing or jet skiing, followed by chilled coconut water and tandoori seafood under candlelit beach tables.",
                "location": "North Goa Coast",
                "category": "Adventure & Relaxation",
                "base_cost_usd": 25,
                "lat": 15.5439,
                "lon": 73.7553
            },
            {
                "title": "Sahakari Spice Plantation Guided Tour & Feast",
                "desc": "Walk amidst cardamom, cinnamon, and vanilla trees, greeted with herbal tea and an authentic buffet lunch on banana leaves.",
                "location": "Ponda, South Goa",
                "category": "Nature & Food",
                "base_cost_usd": 15,
                "lat": 15.4026,
                "lon": 74.0150
            }
        ]
    },
    "rome": {
        "title": "Eternal Rome: Gladiators, Vatican Wonders & Italian Gastronomy",
        "best_time": "April to May or September to October (Warm sunny days, moderate crowds)",
        "packing_tips": "Comfortable sneakers for cobblestones, shoulder cover for churches, reusable water bottle.",
        "coordinates": {"lat": 41.9028, "lon": 12.4964},
        "highlights": ["Colosseum", "Vatican Museums", "Trevi Fountain", "Pantheon", "Trastevere"],
        "pool": [
            {
                "title": "Colosseum & Roman Forum Ancient Walk",
                "desc": "Step back 2,000 years into gladiatorial arena chambers and temples of the ancient Roman Republic.",
                "location": "Piazza del Colosseo",
                "category": "Culture & Heritage",
                "base_cost_usd": 28,
                "lat": 41.8902,
                "lon": 12.4922
            },
            {
                "title": "Trevi Fountain & Spanish Steps Stroll",
                "desc": "Toss a coin into the baroque Trevi Fountain to ensure your return to Rome and enjoy artisanal pistachio gelato.",
                "location": "Piazza di Trevi",
                "category": "Sightseeing",
                "base_cost_usd": 10,
                "lat": 41.9009,
                "lon": 12.4833
            },
            {
                "title": "Pantheon Architectural Marvel & Piazza Navona",
                "desc": "Stand beneath the world's largest unreinforced concrete dome with its celestial oculus.",
                "location": "Piazza della Rotonda",
                "category": "Culture & Heritage",
                "base_cost_usd": 12,
                "lat": 41.8986,
                "lon": 12.4769
            },
            {
                "title": "Trastevere Evening Dinner & Pasta Experience",
                "desc": "Dine on handmade cacio e pepe and carbonara in ivy-draped piazzas with live street musicians.",
                "location": "Trastevere, Rome",
                "category": "Food & Dining",
                "base_cost_usd": 32,
                "lat": 41.8887,
                "lon": 12.4697
            }
        ]
    },
    "new york city": {
        "title": "Dynamic New York: Skyline Vistas, Central Park & Broadway Lights",
        "best_time": "September to November (Crisp autumn air) or May to June (Mild spring)",
        "packing_tips": "Comfortable sneakers for 15,000+ daily steps, MetroCard/OMNY tap card, layered attire.",
        "coordinates": {"lat": 40.7128, "lon": -74.0060},
        "highlights": ["Central Park", "Times Square", "Brooklyn Bridge", "High Line", "Empire State"],
        "pool": [
            {
                "title": "Central Park Morning Walk & Bethesda Terrace",
                "desc": "Stroll beneath American elms at the Mall, view Bethesda Fountain, and watch rowboats on the Lake.",
                "location": "Manhattan, NYC",
                "category": "Nature & Relaxation",
                "base_cost_usd": 10,
                "lat": 40.7829,
                "lon": -73.9654
            },
            {
                "title": "High Line Elevated Park & Chelsea Market Food Hall",
                "desc": "Walk on a repurposed historic freight rail line above city streets, tasting artisanal tacos and lobster rolls.",
                "location": "Meatpacking / Chelsea",
                "category": "Food & Sightseeing",
                "base_cost_usd": 25,
                "lat": 40.7480,
                "lon": -74.0048
            },
            {
                "title": "Brooklyn Bridge Walk & DUMBO Waterfront Sunset",
                "desc": "Walk across the gothic stone arches with sweeping views of the Manhattan skyline.",
                "location": "Lower Manhattan / Brooklyn",
                "category": "Sightseeing",
                "base_cost_usd": 8,
                "lat": 40.7061,
                "lon": -73.9969
            },
            {
                "title": "Times Square Lights & Broadway Theater District",
                "desc": "Immerse in the electric neon glow of Duffy Square and experience world-renowned Broadway entertainment.",
                "location": "Midtown Manhattan",
                "category": "Nightlife & Culture",
                "base_cost_usd": 40,
                "lat": 40.7580,
                "lon": -73.9855
            }
        ]
    }
}

# Generic fallback templates for arbitrary global destinations
GENERIC_POOLS = {
    "Culture & History": [
        ("Discover the Historic Old Town & Heritage Monuments", "Take a walking tour through the oldest district, exploring centuries-old architecture and heritage.", 10),
        ("Visit the Premier City Museum & Art Exhibition", "Explore curated historical exhibits and archaeological discoveries showcasing the region's story.", 18),
        ("Guided Tour of Famous Cathedral / Sacred Landmark", "Admire intricate architectural details and learn about local religious traditions.", 12)
    ],
    "Food & Dining": [
        ("Morning Cafe Breakfast & Local Specialty Pastries", "Savor roasted coffee paired with traditional regional breakfast delicacies at a beloved bakery.", 12),
        ("Authentic Street Food Market Tasting Walk", "Sample freshly prepared street snacks, skewers, and traditional drinks from bustling market stalls.", 20),
        ("Evening Dining Experience with Regional Specialties", "Enjoy dinner featuring seasonal ingredients, authentic recipes, and a relaxed ambiance.", 35)
    ],
    "Sightseeing & Nature": [
        ("Panoramic City Viewpoint & Scenic Observation Deck", "Gain high-altitude perspective over the city skyline, surrounding waterways, or mountain peaks.", 20),
        ("Stroll through the Botanical Gardens or Waterfront Promenade", "Recharge in lush green spaces, quiet trails, and peaceful fountains away from traffic.", 6),
        ("Sunset River Cruise or Scenic Coastline Excursion", "Enjoy golden hour views from the water, passing landmarks bathed in late afternoon sunlight.", 25)
    ],
    "Adventure & Outdoors": [
        ("Guided Nature Hike & Scenic Lookout Trail", "Trek along scenic countryside paths or coastal bluffs with panoramic photo opportunities.", 15),
        ("Outdoor Thrills: Kayaking, Cycling, or Excursion", "Engage in an exhilarating outdoor excursion tailored to the region's topography.", 35)
    ],
    "Relaxation & Leisure": [
        ("Afternoon Leisure, Artisan Tea House & Bookshops", "Spend a quiet afternoon browsing craft shops and enjoying artisanal brews.", 14),
        ("Sunset Beach or Rooftop Lounge Relaxation", "Unwind with refreshing beverages and relaxing music as the sun sets over the horizon.", 22)
    ]
}


def build_fallback_itinerary(
    destination: str,
    duration_days: int,
    travelers_count: int,
    budget_tier: str = "moderate",
    currency: str = "USD",
    interests: list = None,
    pace: str = "moderate"
) -> dict:
    """
    Builds a high-quality, realistic multi-day itinerary.
    Includes geographic coordinates for the Leaflet interactive map and Open-Meteo live weather.
    """
    interests = interests or ["Culture & Heritage", "Food & Dining", "Sightseeing"]
    curr_rate = CURRENCY_RATES.get(currency.upper(), CURRENCY_RATES["USD"])["rate"]
    curr_sym = CURRENCY_RATES.get(currency.upper(), CURRENCY_RATES["USD"])["symbol"]

    dest_key = destination.lower().strip()
    matched_key = None
    for k in CURATED_DESTINATIONS:
        if k in dest_key or dest_key in k:
            matched_key = k
            break

    # Determine coordinates
    center_coords = {"lat": 20.0, "lon": 0.0}
    if matched_key:
        curated = CURATED_DESTINATIONS[matched_key]
        title = f"{duration_days}-Day Curated Journey: {destination.title()}"
        overview = curated["title"]
        best_time = curated["best_time"]
        packing = curated["packing_tips"]
        center_coords = curated.get("coordinates", {"lat": 48.8566, "lon": 2.3522})
        activity_pool = list(curated["pool"])
    else:
        # Resolve real coordinates using geocoding
        geo = geocode_destination(destination)
        if geo:
            center_coords = {"lat": geo["latitude"], "lon": geo["longitude"]}
        else:
            center_coords = {"lat": 48.8566, "lon": 2.3522}

        title = f"{duration_days}-Day Personalized Discovery: {destination.title()}"
        overview = f"A customized {duration_days}-day itinerary for {destination.title()}, balancing top cultural landmarks, authentic regional cuisine, and scenic strolls."
        best_time = "Spring and Autumn months typically offer mild temperatures and fewer crowds. Check local seasonal weather ahead of departure."
        packing = "Versatile layered clothing, comfortable walking sneakers, portable power bank, and compact umbrella."
        
        activity_pool = []
        for cat, items in GENERIC_POOLS.items():
            for item_title, desc, cost in items:
                # Add gentle offsets around city center
                offset_lat = round(center_coords["lat"] + (random.uniform(-0.02, 0.02)), 4)
                offset_lon = round(center_coords["lon"] + (random.uniform(-0.02, 0.02)), 4)
                activity_pool.append({
                    "title": item_title,
                    "desc": desc,
                    "location": f"Central {destination.title()}",
                    "category": cat,
                    "base_cost_usd": cost,
                    "lat": offset_lat,
                    "lon": offset_lon
                })

    # Generate daily schedule
    days_data = []
    pool_copy = list(activity_pool)
    random.seed(len(destination) + duration_days)

    time_slots = [
        {"name": "Morning", "time": "09:00 AM - 12:00 PM"},
        {"name": "Afternoon", "time": "01:00 PM - 04:30 PM"},
        {"name": "Evening", "time": "05:30 PM - 08:00 PM"},
        {"name": "Night", "time": "08:30 PM - 10:30 PM"}
    ]

    pace_lower = (pace or "moderate").lower()
    if pace_lower == "relaxed":
        active_slots = [time_slots[0], time_slots[1], time_slots[2]]
    elif pace_lower == "fast-paced":
        active_slots = time_slots
    else:
        active_slots = [time_slots[0], time_slots[1], time_slots[2]]

    for day_num in range(1, duration_days + 1):
        day_activities = []
        
        for slot in active_slots:
            if not pool_copy:
                pool_copy = list(activity_pool)
            
            chosen = pool_copy.pop(0) if pool_copy else {
                "title": f"Explore {destination.title()} Local Neighborhoods",
                "desc": "Wander through charming pedestrian lanes, artisan shops, and scenic public squares at your own pace.",
                "location": f"{destination.title()}",
                "category": "Sightseeing",
                "base_cost_usd": 15,
                "lat": center_coords["lat"],
                "lon": center_coords["lon"]
            }

            cost_local = round(chosen["base_cost_usd"] * curr_rate)

            day_activities.append({
                "time_slot": slot["name"],
                "time_range": slot["time"],
                "activity_name": chosen["title"],
                "description": chosen["desc"],
                "location": chosen["location"],
                "category": chosen["category"],
                "latitude": chosen.get("lat", center_coords["lat"]),
                "longitude": chosen.get("lon", center_coords["lon"]),
                "estimated_cost_raw": cost_local,
                "estimated_cost_display": f"{curr_sym}{cost_local:,}",
                "unverified_notice": "Estimated activity cost; verify local opening hours and ticket availability before visiting."
            })

        days_data.append({
            "day_number": day_num,
            "theme": f"Day {day_num}: {destination.title()} Highlights & Discovery",
            "activities": day_activities
        })

    # Compute financial budget breakdown
    budget_breakdown = calculate_budget_breakdown(
        destination=destination,
        duration_days=duration_days,
        travelers_count=travelers_count,
        budget_tier=budget_tier,
        currency=currency,
        pace=pace
    )

    # Fetch live weather (or fallback)
    weather_data = get_destination_weather(destination)

    return {
        "status": "success",
        "is_demo": True,
        "generation_source": "Offline Curated Engine (Demo Mode)",
        "mode_badge": "Demo Mode (Offline Data)",
        "mode_badge_class": "badge-demo",
        "mode_explanation": "You are viewing an itinerary generated by our curated offline travel database. To enable live AI-generated itineraries using Google Gemini, provide your free GEMINI_API_KEY in the server .env file.",
        "trip_title": title,
        "destination": destination.title(),
        "destination_coordinates": center_coords,
        "duration_days": duration_days,
        "travelers_count": travelers_count,
        "budget_tier": budget_tier.capitalize(),
        "pace": pace.capitalize(),
        "trip_overview": overview,
        "best_time_to_visit": best_time,
        "packing_recommendations": packing,
        "itinerary_days": days_data,
        "budget_breakdown": budget_breakdown,
        "weather": weather_data,
        "disclaimers": [
            "All pricing, entrance fees, and meal costs are approximations for planning purposes only.",
            "Opening hours, availability, and public transit schedules change seasonally; always confirm directly with local providers.",
            "Live weather is powered by Open-Meteo. Actual meteorological conditions may vary."
        ]
    }
