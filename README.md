# WanderPlan AI: Personalized Travel Itinerary Planner
**Capstone Project for Skill Wallet | B.Tech Computer Science & Engineering**

[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deployment: Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://vercel.com)

---

## 📌 1. Project Overview & Problem Statement

### Problem Statement
Travelers often spend dozens of hours researching travel blogs, comparing hotel rates, calculating transit budgets, and assembling scattered notes across multiple websites to plan a vacation. Existing solutions are either generic static travel guides or commercial booking platforms biased towards affiliate promotions.

### Solution Overview
**WanderPlan AI** is a fully responsive, modern web application that automatically synthesizes realistic, customized day-by-day itineraries tailored directly to a traveler's individual destination, trip length, companion count, budget tier, preferred currency, travel pace, and specific interests. 

The application implements a secure dual-engine architecture:
1. **Live AI Engine:** Powered by Google Gemini AI with structured JSON outputs.
2. **Curated Demo Mode Engine:** A transparent offline engine that activates automatically when no API key is provided, ensuring full functionality during evaluations or offline demos without pretending or fabricating data.
3. **Responsible AI Disclaimers:** Clearly badges estimated costs and unverified opening hours to prevent misleading travelers.

---

## 🎯 2. Objectives & Scope

### Project Objectives
* **AI-Driven Personalization:** Tailor morning, afternoon, evening, and night activities according to travel style (Relaxed, Balanced, Fast-paced) and specific interests (Culture, Food, Adventure, Nature, etc.).
* **Integrated Budget Estimator:** Provide itemized cost approximations for accommodation, dining, activities, and local transport across 7 global currencies (`USD`, `INR`, `EUR`, `GBP`, `JPY`, `AUD`, `CAD`).
* **Ethical & Transparent AI:** Ensure all estimates are labeled as approximations. Never present unverified opening hours or real-time ticket availability as verified facts.
* **Modern Mobile-First UI:** Deliver an intuitive, accessible user interface optimized across mobile devices, tablets, and desktop displays.
* **Zero-Leakage Security:** Keep all AI credentials securely isolated on the backend server; never expose private API keys in client-side code.

### Scope
* **In Scope:** Destination selection, duration configuration (1–14 days), travel party scaling (1–20 people), currency conversion, budget estimation, day-by-day timeline view, interactive day filter tabs, offline demo mode, browser trip saving (`localStorage`), print/PDF export, and automated unit testing.
* **Out of Scope for Current Phase:** Direct airline booking APIs, payment gateway processing, and live GPS turn-by-turn navigation (identified as future enhancements).

---

## 🛠️ 3. Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | **Python (Flask 3.1)** | Lightweight, beginner-friendly REST architecture, minimal boilerplate, clean routing, and simple serverless deployment. |
| **AI Personalization** | **Google Gemini API** (`gemini-2.5-flash` / `gemini-1.5-flash`) | Generous free tier for students, ultra-fast latency, and native support for strict JSON schema output (`responseMimeType: "application/json"`). |
| **Frontend UI** | **HTML5 & Semantic Elements** | Standards-compliant, accessible structure. |
| **Styling & Theme** | **Modern CSS3 (CSS Variables + Grid/Flexbox)** | Travel-themed palette (ocean blues, emerald greens, gold accents), responsive breakpoints, and dedicated print stylesheet (`@media print`). |
| **Client Scripting** | **Vanilla ES6 JavaScript** | Zero build step or complex bundler overhead; modular API client and local storage controller. |
| **Deployment** | **Vercel Serverless Functions** | Native Python runtime support (`api/index.py` + `vercel.json`) with zero configuration servers. |
| **Testing** | **Python `unittest`** | Automated validation of endpoints, inputs, budget math, and fallback behavior. |

---

## 🏛️ 4. System Architecture & Workflow

### Architecture Diagram
```
+-------------------------------------------------------------------------+
|                              Client Browser                             |
|  [Responsive UI] <---> [Form Controller (app.js)] <---> [API Client]   |
+-------------------------------------------------------------------------+
                                     |
                         HTTP JSON REST Requests
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           Flask Backend Server                          |
|                                                                         |
|   +-----------------------+              +--------------------------+   |
|   |   GET / & /api/health |              | POST /api/generate-...   |   |
|   +-----------------------+              +--------------------------+   |
|                                                        |                |
|                                           Server Input Validation       |
|                                                        |                |
|                      +---------------------------------+                |
|                      |                                 |                |
|                      v                                 v                |
|         [GEMINI_API_KEY Available?]             [No API Key / Error]    |
|                      |                                 |                |
|                      v                                 v                |
|         +-------------------------+       +-------------------------+   |
|         | services/ai_generator   |       | services/demo_generator |   |
|         | Google Gemini REST API  |       | Curated Offline Engine  |   |
|         +-------------------------+       +-------------------------+   |
|                      \                                 /                |
|                       +-------------------------------+                 |
|                                       |                                 |
|                                       v                                 |
|                         +---------------------------+                   |
|                         | services/budget_calculator|                   |
|                         | Currency & Tier Multiplier|                   |
|                         +---------------------------+                   |
|                                       |                                 |
|                           Unified JSON Response                         |
+-------------------------------------------------------------------------+
```

---

## 📁 5. Project Directory Structure

```
TravelPlannerCapstone/
├── app.py                      # Flask main entry point (local development server)
├── api/
│   └── index.py                # Vercel Serverless Function entry point
├── services/
│   ├── __init__.py             # Services package definition
│   ├── ai_generator.py         # Google Gemini AI integration & prompt orchestration
│   ├── demo_generator.py       # Curated offline demo engine (transparent fallback)
│   └── budget_calculator.py    # Multi-currency cost estimator and category math
├── static/
│   ├── css/
│   │   └── style.css           # Travel-themed design system, mobile queries & print styles
│   └── js/
│       ├── api.js              # Fetch client communicating with backend endpoints
│       └── app.js              # UI controller, state management, and localStorage saver
├── templates/
│   └── index.html              # Semantic, responsive HTML5 travel planner UI
├── tests/
│   ├── __init__.py             # Test package definition
│   └── test_app.py             # Automated unit tests for routes, validation & math
├── requirements.txt            # Python dependencies (Flask, requests, python-dotenv)
├── .env.example                # Template for environment variables (API keys)
├── .gitignore                  # Git ignore rules (prevents secret leaks)
├── vercel.json                 # Vercel serverless configuration
└── README.md                   # Complete documentation & capstone report guide
```

---

## 🚀 6. Setup & Running Locally on Windows

Follow these steps to run the application on your Windows machine:

### Step 1: Open Terminal in Workspace
Open **PowerShell** or **Command Prompt** and navigate to your project directory:
```powershell
cd c:\Users\LENOVO\Downloads\TravelPlannerCapstone
```

### Step 2: Install Python Dependencies
Install the required packages using Python's package manager:
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables (Optional for Live AI)
1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in any text editor (such as Notepad or VS Code).
3. If you have a Google Gemini API Key:
   * Obtain a free key from: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   * Paste it into `.env`:
     ```env
     GEMINI_API_KEY=AIzaSyYourActualKeyHere
     ```
4. If you do not have an API key right now, leave it empty. The application will smoothly and automatically run in **Curated Demo Mode**.

### Step 4: Start the Local Flask Server
Run the Flask server:
```powershell
python app.py
```
You will see output in the console:
```
==================================================
✈️  TravelPlanner Capstone Server Starting...
🌐 Local URL: http://127.0.0.1:5000
🔑 Gemini AI Status: Demo Mode (Offline Fallback)
==================================================
```

### Step 5: Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 7. Running Automated Tests

A dedicated test suite is included to verify that API routing, server-side validation, demo generation, and budget math function properly.

Run the tests using Python's built-in `unittest` runner:
```powershell
python -m unittest tests/test_app.py
```

### Verified Test Results
```
Ran 8 tests in 0.151s
OK
```
* `test_health_check_endpoint`: Verifies `/api/health` returns HTTP 200 with diagnostics.
* `test_sample_destinations_endpoint`: Verifies sample destinations load correctly.
* `test_home_page_renders`: Confirms the HTML interface is rendered at `/`.
* `test_validation_missing_destination`: Validates that empty destination submissions return HTTP 400.
* `test_validation_invalid_duration`: Validates that duration > 14 days returns HTTP 400.
* `test_itinerary_generation_demo_mode`: Verifies the offline fallback returns complete daily schedules and disclaimers.
* `test_budget_calculator_multi_currency`: Verifies accurate math across USD, INR, and EUR.
* `test_budget_calculator_tier_scaling`: Verifies that Luxury tier costs scale higher than Budget tier.

---

## ☁️ 8. Deployment Guide (Vercel & GitHub)

### Preparing GitHub Repository
Before pushing to GitHub, ensure Git is available on your machine:
1. If Git is not installed, install it using Windows Package Manager:
   ```powershell
   winget install --id Git.Git -e --source winget
   ```
2. Initialize repository and commit files:
   ```powershell
   git init
   git add .
   git commit -m "feat: complete Personalized Travel Itinerary Planner capstone"
   ```
3. Create a new repository on your GitHub account (e.g., `travel-planner-capstone`).
4. Link and push your repository:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/travel-planner-capstone.git
   git push -u origin main
   ```

### Deploying to Vercel
1. Sign in to your [Vercel Dashboard](https://vercel.com).
2. Click **Add New** &rarr; **Project**.
3. Import your GitHub repository `travel-planner-capstone`.
4. Under **Environment Variables**:
   * Add Key: `GEMINI_API_KEY`
   * Add Value: *(Your Google Gemini API Key from Google AI Studio)*
5. Click **Deploy**. Vercel will detect `vercel.json` and deploy your serverless Python application automatically.

---

## 📸 9. Capstone Submission Screenshots Checklist

When preparing your final submission for Skill Wallet, capture the following screenshots:
- [ ] **Screenshot 1: Landing Page & Hero Section:** Shows title, AI status badge, and call-to-action buttons.
- [ ] **Screenshot 2: Interactive Travel Form:** Destination search, duration slider, traveler selector, currency dropdown, and interest tags.
- [ ] **Screenshot 3: Loading State:** Pulse animation and loading indicator while generating.
- [ ] **Screenshot 4: Generated Itinerary:** Result header, trip overview, best time to visit, and packing tips.
- [ ] **Screenshot 5: Budget Breakdown Card:** Grand total, daily average, and itemized category breakdown.
- [ ] **Screenshot 6: Day-by-Day Timeline & Filter Tabs:** Morning, afternoon, and evening activity cards with unverified estimate badges.
- [ ] **Screenshot 7: Demo Mode vs Live AI Mode:** Shows the transparent mode badge and explanation banner.
- [ ] **Screenshot 8: Saved Trips Modal:** Demonstrates browser storage persistence.
- [ ] **Screenshot 9: Mobile View:** Responsive layout rendered on a smartphone or browser developer tools device emulator.
- [ ] **Screenshot 10: Terminal Test Run:** Terminal output showing `8 tests OK` in `tests/test_app.py`.

---

## 🎬 10. Demo Video Script (3-Minute Capstone Viva)

| Timestamp | Screen / Visual | Narration / Script |
| :--- | :--- | :--- |
| **0:00 - 0:30** | Landing Page | *"Hello everyone. Today I am presenting my B.Tech Capstone Project: WanderPlan AI, an intelligent, personalized travel itinerary planner. In this project, we solve the challenge of fragmented travel planning by creating tailored day-by-day itineraries with integrated multi-currency budget estimations."* |
| **0:30 - 1:00** | Interactive Planner Form | *"Here on the planning interface, users can input any global destination, select trip duration up to 14 days, choose companion party size, set their budget tier, pick from 7 global currencies, and select specific interests such as Culture, Food, and Adventure."* |
| **1:00 - 1:45** | Generation & Results View | *"When we click 'Generate Itinerary', our backend processes the preferences. Notice the transparent Status Badge: if an API key is present, it connects live to Google Gemini. If not, it activates our transparent Curated Demo Engine so users and evaluators always have a functional experience."* |
| **1:45 - 2:15** | Budget & Disclaimers | *"Notice the estimated budget breakdown divided into Accommodation, Dining, Activities, and Local Transport. Following Responsible AI principles, we explicitly badge these figures and timings as unverified approximations, advising travelers to verify local opening hours."* |
| **2:15 - 2:45** | Interactive Features | *"The interface allows users to filter by specific days, edit preferences, regenerate plans, save trips to browser storage, and export clean print/PDF versions."* |
| **2:45 - 3:00** | Conclusion & Tech Stack | *"The system is built using Python Flask, semantic HTML5, responsive CSS3, and Vanilla JavaScript, thoroughly verified with automated unit tests. Thank you."* |

---

## 🔮 11. Limitations & Future Enhancements

* **Live Weather Integration:** Incorporating real-time weather forecasts via OpenWeatherMap API for departures within 7 days.
* **Interactive Map Visualization:** Plotting daily activity routes on an interactive Leaflet or Google Maps layer.
* **Flight & Hotel Affiliates:** Optional integration with Skyscanner or Booking.com APIs for real-time live availability.
* **Multi-Language Support:** Localizing itineraries into Spanish, French, Japanese, and Hindi.

---

## 📜 12. References & Acknowledgments
1. Google Gemini API Documentation: [https://ai.google.dev/docs](https://ai.google.dev/docs)
2. Flask Web Framework Documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
3. MDN Web Docs: CSS Grid & Flexbox Responsive Design: [https://developer.mozilla.org/](https://developer.mozilla.org/)
4. Skill Wallet Capstone Curriculum Guidelines.
