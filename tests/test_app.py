"""
Automated Unit and Integration Tests for TravelPlanner Capstone.
Tests Flask endpoints, input validation, offline demo generation, and budget calculations.
"""

import unittest
import json
from app import app
from services.budget_calculator import calculate_budget_breakdown, CURRENCY_RATES
from services.demo_generator import build_fallback_itinerary


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
        self.assertGreater(len(data["destinations"]), 0)

    def test_home_page_renders(self):
        """Verify GET / renders the main HTML interface."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"WanderPlan", response.data)
        self.assertIn(b"Trip Planner", response.data)

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

    def test_itinerary_generation_demo_mode(self):
        """Verify demo generator returns complete structure with disclaimers and budget."""
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
        self.assertIn("budget_breakdown", data)
        self.assertGreater(data["budget_breakdown"]["grand_total"], 0)
        self.assertIn("disclaimers", data)
        self.assertGreater(len(data["disclaimers"]), 0)

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

    def test_budget_calculator_tier_scaling(self):
        """Verify luxury budget is greater than budget tier for same trip."""
        b_budget = calculate_budget_breakdown("Rome", 3, 1, "budget", "USD")
        b_luxury = calculate_budget_breakdown("Rome", 3, 1, "luxury", "USD")
        self.assertGreater(b_luxury["grand_total"], b_budget["grand_total"])


if __name__ == "__main__":
    unittest.main()
