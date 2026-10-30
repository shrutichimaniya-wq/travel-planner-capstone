# WanderPlan AI – Personalized AI Travel Itinerary Planner
**Skill Wallet Generative AI with Google Cloud Virtual Internship Capstone**

[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deployment: Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://travel-planner-capstone-zeta.vercel.app/)

* **Live Demo:** [https://travel-planner-capstone-zeta.vercel.app/](https://travel-planner-capstone-zeta.vercel.app/)
* **GitHub Repository:** [https://github.com/shrutichimaniya-wq/travel-planner-capstone](https://github.com/shrutichimaniya-wq/travel-planner-capstone)

---

## 📌 1. Project Overview & Problem Statement

### Problem Statement
Modern travelers spend hours reading fragmented travel blogs, cross-referencing weather forecasts, calculating multi-currency budgets, and planning daily sightseeing routes. Generic static travel guides lack personalization, and commercial booking engines are often biased by commission fees.

### Solution Overview
**WanderPlan AI** is an intelligent, full-stack travel planning platform designed to synthesize authentic, day-wise itineraries tailored specifically to a traveler's destination, budget tier, party size, travel pace, and interests.

The upgraded platform integrates:
1. **Google Gemini Generative AI:** Real-time personalized itinerary generation with structured JSON schema.
2. **Open-Meteo Real-Time Weather:** Live destination weather, temperature, humidity, wind, and 5-day forecasts.
3. **Interactive Travel Map:** Embedded Leaflet.js and OpenStreetMap engine plotting verified destination attractions.
4. **Destination Explorer:** High-resolution destination cards with real-time search and continent filters.
5. **Smart Multi-Currency Budget Planner:** Categorized breakdown across Accommodation, Dining, Sightseeing, and Local Transport.
6. **1-Click PDF Download & Print:** Instant client-side PDF generation via `html2pdf.js` and dedicated print CSS.
7. **Curated Demo Mode Fallback:** Transparent offline engine ensuring complete reliability during evaluations or offline demos.
8. **Responsible AI Disclaimers:** Explicitly badging estimates and advising travelers to confirm local operating hours.

---

## 🎯 2. Features Breakdown

| Feature | Description | Integration / Tech |
| :--- | :--- | :--- |
| **Destination Explorer** | Interactive catalog of 12+ iconic global destinations with Unsplash photography, top attractions, best visiting seasons, and real-time search. | REST API + Client Filter |
| **AI Travel Itinerary** | Day-wise schedule with Morning, Afternoon, Evening, and Night segments, personalized by budget, party size, pace, and interests. | Google Gemini API (`v1beta`) |
| **Live Weather Widget** | Real-time temperature (°C/°F), weather condition icons, humidity, wind, rain probability, and 5-day forecast. | Open-Meteo API |
| **Interactive Map** | Geospatial map centered on the destination, plotting activity markers with interactive popups. | Leaflet.js & OpenStreetMap |
| **Smart Budget Planner** | Rule-based multi-currency estimations across 7 global currencies (`USD`, `INR`, `EUR`, `GBP`, `JPY`, `AUD`, `CAD`). | `budget_calculator.py` |
| **Save Favourite Trips** | Store, revisit, and manage generated itineraries in the browser. | Browser `localStorage` |
| **1-Click PDF Download** | Download complete travel itineraries as clean, multi-page PDF documents. | `html2pdf.js` & `@media print` |
| **Demo Mode Fallback** | Automatic fallback to curated offline travel database when API key is unconfigured or unavailable. | `demo_generator.py` |

---

## 🛠️ 3. Technology Stack & APIs

* **Backend:** Python 3.14 & Flask 3.1
* **AI Engine:** Google Gemini API (`gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`)
* **Weather & Geocoding:** Open-Meteo API (Open-source, no key required)
* **Maps:** Leaflet.js 1.9.4 & OpenStreetMap
* **Frontend:** Semantic HTML5, Modern Responsive CSS3 (CSS Variables, Flexbox, Grid), Vanilla ES6 JavaScript
* **PDF Engine:** `html2pdf.js` (Client-side HTML5 canvas to PDF)
* **Deployment:** Vercel Serverless Functions (`@vercel/python`)
* **Testing:** Python `unittest` (11 automated test cases)

---

## 🏛️ 4. System Architecture

```
+---------------------------------------------------------------------------------+
|                                 Client Browser                                  |
|   [Responsive UI] <---> [app.js Controller] <---> [Leaflet Map + html2pdf]      |
+---------------------------------------------------------------------------------+
                                        |
                            HTTP JSON REST Requests
                                        |
                                        v
+---------------------------------------------------------------------------------+
|                              Flask Backend Server                               |
|                                                                                 |
|   +-----------------------+   +-----------------------+   +-----------------+   |
|   |  GET / & /api/health  |   | GET /api/destinations |   | GET /api/weather|   |
|   +-----------------------+   +-----------------------+   +-----------------+   |
|                                                                     |           |
|                                                              Open-Meteo REST    |
|                                                                                 |
|                      POST /api/generate-itinerary                               |
|                                   |                                             |
|                        Server Input Validation                                  |
|                                   |                                             |
|                 +-----------------+-----------------+                           |
|                 |                                   |                           |
|                 v                                   v                           |
|      [GEMINI_API_KEY Present?]             [No Key / API Error]                 |
|                 |                                   |                           |
|                 v                                   v                           |
|    +-------------------------+         +-------------------------+              |
|    |  services/ai_generator  |         | services/demo_generator |              |
|    | Google Gemini REST API  |         |  Curated Offline Engine |              |
|    +-------------------------+         +-------------------------+              |
|                 \                                   /                           |
|                  +----------------+----------------+                            |
|                                   |                                             |
|                                   v                                             |
|                     +---------------------------+                               |
|                     | services/budget_calculator|                               |
|                     | Multi-Currency Estimator  |                               |
|                     +---------------------------+                               |
|                                   |                                             |
|                                   v                                             |
|                     +---------------------------+                               |
|                     | services/weather_service  |                               |
|                     | Open-Meteo Live Forecast  |                               |
|                     +---------------------------+                               |
|                                   |                                             |
|                        Unified JSON Response                                    |
+---------------------------------------------------------------------------------+
```

---

## 📁 5. Directory Structure

```
TravelPlannerCapstone/
├── app.py                      # Flask main entry point & REST API routes
├── api/
│   └── index.py                # Vercel Serverless Function entry point
├── services/
│   ├── __init__.py             # Package definition
│   ├── ai_generator.py         # Google Gemini AI integration & structured prompt orchestration
│   ├── demo_generator.py       # Curated offline demo engine with coordinates
│   ├── budget_calculator.py    # Multi-currency cost estimator and category math
│   └── weather_service.py      # Open-Meteo real-time weather & geocoding integration
├── static/
│   ├── css/
│   │   └── style.css           # Travel-themed design system, mobile queries & print styles
│   └── js/
│       ├── api.js              # Fetch client communicating with backend endpoints
│       └── app.js              # UI controller, Leaflet map renderer & local storage saver
├── templates/
│   └── index.html              # Semantic HTML5 UI with Leaflet maps & weather widget
├── tests/
│   ├── __init__.py             # Test package definition
│   └── test_app.py             # Automated unit tests (11 passing tests)
├── requirements.txt            # Python dependencies (Flask, requests, python-dotenv)
├── .env.example                # Safe environment variable template
├── .gitignore                  # Prevents committing secrets (.env) or cached binaries
├── vercel.json                 # Vercel serverless configuration
└── README.md                   # Complete documentation & capstone report
```

---

## 🚀 6. Setup & Running Locally on Windows

### Step 1: Open Terminal in Workspace
```powershell
cd c:\Users\LENOVO\Downloads\TravelPlannerCapstone
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` and paste your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_key_here
   ```
   *(If left empty, the application automatically runs in the clearly labeled Curated Demo Mode).*

### Step 4: Start the Flask Application
```powershell
python app.py
```
Terminal output:
```text
==================================================
TravelPlanner Capstone Server Starting...
Local URL: http://127.0.0.1:5000
Gemini AI Status: Configured (Live AI) / Demo Mode
==================================================
```

### Step 5: Open in Browser
Navigate to **`http://127.0.0.1:5000`** in Google Chrome.

---

## 🧪 7. Running Automated Tests

Run the test suite using Python's built-in `unittest` runner:
```powershell
python -m unittest tests/test_app.py
```

### Verified Test Results
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.144s

OK
```
* `test_health_check_endpoint`: Verifies `/api/health` diagnostics.
* `test_sample_destinations_endpoint`: Verifies 12+ destinations load properly.
* `test_sample_destinations_search_filter`: Verifies keyword filtering for destinations.
* `test_weather_endpoint_valid_destination`: Verifies weather service response structure.
* `test_weather_endpoint_missing_param`: Verifies 400 error on missing destination.
* `test_home_page_renders`: Confirms main HTML interface is served.
* `test_validation_missing_destination`: Verifies rejection of empty destination submissions.
* `test_validation_invalid_duration`: Verifies rejection of duration > 14 days.
* `test_itinerary_generation_demo_mode_structure`: Confirms presence of Leaflet coordinates, weather, and budget breakdown.
* `test_budget_calculator_multi_currency`: Verifies accurate math across USD, INR, and EUR.
* `test_geocoding_helper`: Verifies destination coordinate resolution.

---

## ☁️ 8. Deployment Guide (Vercel & GitHub)

### Pushing Upgrades to GitHub
```powershell
git add .
git commit -m "feat: upgrade WanderPlan AI with Open-Meteo weather, Leaflet map, Destination Explorer, and PDF download"
git push origin main
```

### Redeploying on Vercel
1. If your Vercel project is linked to GitHub (`shrutichimaniya-wq/travel-planner-capstone`), pushing to `main` will automatically trigger a new deployment.
2. In the [Vercel Dashboard](https://vercel.com):
   * Navigate to **Settings &rarr; Environment Variables**.
   * Ensure `GEMINI_API_KEY` is added under Production and Preview environments.
3. Your live application will update automatically at:  
   **[https://travel-planner-capstone-zeta.vercel.app/](https://travel-planner-capstone-zeta.vercel.app/)**

---

## 📜 9. References & Acknowledgments
1. Google Cloud Generative AI & Gemini API Documentation: [https://ai.google.dev/docs](https://ai.google.dev/docs)
2. Open-Meteo Free Weather API: [https://open-meteo.com/](https://open-meteo.com/)
3. Leaflet.js Open-Source Interactive Maps: [https://leafletjs.com/](https://leafletjs.com/)
4. OpenStreetMap: [https://www.openstreetmap.org/](https://www.openstreetmap.org/)
5. Skill Wallet Generative AI with Google Cloud Virtual Internship Guidelines.
