"""
Automated Unit and Integration Tests for TravelPlanner Capstone.
Tests Flask endpoints, input validation, offline demo generation,
Leaflet map coordinates, Open-Meteo weather service, and budget calculations.
"""

import unittest
import json
from app import app
from services.budget_calculator import calculate_budget_breakdown, CURRENCY_RATES
from services.demo_generator import build_fallback_itinerary
from services.weather_service import geocode_destination, get_destination_weather


class TravelPlannerTestCase(unittest.TestCase):

    def setUp(self):
        """Set up Flask test client before each test."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_check_endpoint(self):
        """Verify /api/health returns HTTP 200 with required diagnostic keys."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("mode", data)
        self.assertIn("api_key_configured", data)
        self.assertIn("supported_currencies", data)

    def test_sample_destinations_endpoint(self):
        """Verify /api/sample-destinations returns non-empty destination list."""
        response = self.client.get("/api/sample-destinations")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIsInstance(data["destinations"], list)
        self.assertGreaterEqual(len(data["destinations"]), 10)

    def test_sample_destinations_search_filter(self):
        """Verify /api/sample-destinations?q=tokyo filters properly."""
        response = self.client.get("/api/sample-destinations?q=tokyo")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["count"], 0)
        self.assertEqual(data["destinations"][0]["name"], "Tokyo")

    def test_weather_endpoint_valid_destination(self):
        """Verify /api/weather returns weather or structured fallback for a destination."""
        response = self.client.get("/api/weather?destination=Tokyo")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("status", data)
        self.assertIn("destination", data)

    def test_weather_endpoint_missing_param(self):
        """Verify /api/weather returns 400 when destination is omitted."""
        response = self.client.get("/api/weather")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["status"], "error")

    def test_home_page_renders(self):
        """Verify GET / renders the main HTML interface."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"WanderPlan", response.data)
        self.assertIn(b"Destination Explorer", response.data)

    def test_validation_missing_destination(self):
        """Verify /api/generate-itinerary rejects empty destination."""
        payload = {
            "destination": "",
            "duration_days": 4,
            "travelers_count": 2,
            "budget_tier": "moderate",
            "currency": "USD"
        }
        response = self.client.post(
            "/api/generate-itinerary",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["status"], "error")
        self.assertIn("destination", data["error"].lower())

    def test_validation_invalid_duration(self):
        """Verify /api/generate-itinerary rejects out-of-range duration (> 14 days)."""
        payload = {
            "destination": "Paris",
            "duration_days": 25,
            "travelers_count": 2,
            "budget_tier": "moderate",
            "currency": "USD"
        }
        response = self.client.post(
            "/api/generate-itinerary",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("duration", data["error"].lower())

    def test_itinerary_generation_demo_mode_structure(self):
        """Verify demo generator returns complete structure with map coords, weather, and budget."""
        payload = {
            "destination": "Tokyo",
            "duration_days": 3,
            "travelers_count": 2,
            "budget_tier": "moderate",
            "currency": "USD",
            "pace": "moderate",
            "interests": ["Culture & Heritage", "Food & Dining"]
        }
        response = self.client.post(
            "/api/generate-itinerary",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(data["duration_days"], 3)
        self.assertEqual(len(data["itinerary_days"]), 3)
        
        # Verify map coordinates
        self.assertIn("destination_coordinates", data)
        self.assertIn("lat", data["destination_coordinates"])
        self.assertIn("lon", data["destination_coordinates"])
        
        # Verify weather data structure
        self.assertIn("weather", data)
        
        # Verify activity level coordinates
        first_act = data["itinerary_days"][0]["activities"][0]
        self.assertIn("latitude", first_act)
        self.assertIn("longitude", first_act)

        # Verify budget and disclaimers
        self.assertIn("budget_breakdown", data)
        self.assertGreater(data["budget_breakdown"]["grand_total"], 0)
        self.assertIn("disclaimers", data)

    def test_budget_calculator_multi_currency(self):
        """Verify budget calculator math across USD, INR, and EUR."""
        for curr in ["USD", "INR", "EUR"]:
            budget = calculate_budget_breakdown(
                destination="Paris",
                duration_days=5,
                travelers_count=2,
                budget_tier="moderate",
                currency=curr,
                pace="moderate"
            )
            self.assertEqual(budget["currency_code"], curr)
            self.assertGreater(budget["grand_total"], 0)
            self.assertEqual(
                budget["grand_total"],
                budget["stay_total"] + budget["food_total"] + budget["activities_total"] + budget["transport_total"]
            )
            self.assertTrue(budget["is_estimate"])

    def test_geocoding_helper(self):
        """Verify geocode_destination resolves coordinates for known destinations."""
        geo = geocode_destination("Paris")
        self.assertIsNotNone(geo)
        self.assertAlmostEqual(geo["latitude"], 48.8566, places=1)
        self.assertAlmostEqual(geo["longitude"], 2.3522, places=1)


if __name__ == "__main__":
    unittest.main()
