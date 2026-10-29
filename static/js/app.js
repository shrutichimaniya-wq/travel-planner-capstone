/**
 * WanderPlan AI - Application Controller
 * Manages form interactions, itinerary rendering, budget display, and local storage.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current active itinerary state in memory
    let currentItinerary = null;
    let savedTrips = [];

    // DOM Elements - Navigation & System
    const navMenu = document.getElementById('navMenu');
    const mobileToggle = document.getElementById('mobileToggle');
    const aiStatusPill = document.getElementById('aiStatusPill');
    const systemBanner = document.getElementById('systemBanner');
    const closeBannerBtn = document.getElementById('closeBannerBtn');

    // DOM Elements - Form
    const tripPlannerForm = document.getElementById('tripPlannerForm');
    const destinationInput = document.getElementById('destinationInput');
    const clearDestBtn = document.getElementById('clearDestBtn');
    const destFeedback = document.getElementById('destFeedback');
    const durationDaysSlider = document.getElementById('durationDays');
    const durationDaysDisplay = document.getElementById('durationDaysDisplay');
    const travelerPills = document.querySelectorAll('.traveler-pill');
    const travelersCountInput = document.getElementById('travelersCount');
    const budgetCards = document.querySelectorAll('.budget-card');
    const budgetTierInput = document.getElementById('budgetTier');
    const currencySelect = document.getElementById('currencySelect');
    const pacePills = document.querySelectorAll('.pace-pill');
    const travelPaceInput = document.getElementById('travelPace');
    const interestsGrid = document.getElementById('interestsGrid');
    const interestsFeedback = document.getElementById('interestsFeedback');
    const generateBtn = document.getElementById('generateBtn');

    // DOM Elements - Loading & Results
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const destinationsGrid = document.getElementById('destinationsGrid');

    // DOM Elements - Results Details
    const resultModeBadge = document.getElementById('resultModeBadge');
    const resultModeText = document.getElementById('resultModeText');
    const resultTripTitle = document.getElementById('resultTripTitle');
    const resultTripMeta = document.getElementById('resultTripMeta');
    const modeExplanationBox = document.getElementById('modeExplanationBox');
    const modeExplanationText = document.getElementById('modeExplanationText');
    const overviewText = document.getElementById('overviewText');
    const bestTimeText = document.getElementById('bestTimeText');
    const packingText = document.getElementById('packingText');

    // DOM Elements - Budget Breakdown
    const budgetCurrencySym = document.getElementById('budgetCurrencySym');
    const budgetGrandTotal = document.getElementById('budgetGrandTotal');
    const budgetTierName = document.getElementById('budgetTierName');
    const budgetDailyAvg = document.getElementById('budgetDailyAvg');
    const budgetStayTotal = document.getElementById('budgetStayTotal');
    const budgetFoodTotal = document.getElementById('budgetFoodTotal');
    const budgetActivitiesTotal = document.getElementById('budgetActivitiesTotal');
    const budgetTransportTotal = document.getElementById('budgetTransportTotal');
    const budgetDisclaimerText = document.getElementById('budgetDisclaimerText');

    // DOM Elements - Schedule & Days
    const dayFilterTabs = document.getElementById('dayFilterTabs');
    const daysContainer = document.getElementById('daysContainer');
    const disclaimerList = document.getElementById('disclaimerList');

    // DOM Elements - Actions
    const editPreferencesBtn = document.getElementById('editPreferencesBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const saveTripBtn = document.getElementById('saveTripBtn');
    const printTripBtn = document.getElementById('printTripBtn');

    // DOM Elements - Modals
    const savedTripsModal = document.getElementById('savedTripsModal');
    const openSavedTripsBtn = document.getElementById('openSavedTripsBtn');
    const closeSavedTripsModalBtn = document.getElementById('closeSavedTripsModalBtn');
    const savedTripsList = document.getElementById('savedTripsList');
    const savedTripsCount = document.getElementById('savedTripsCount');

    const capstoneModal = document.getElementById('capstoneModal');
    const openCapstoneModalBtn = document.getElementById('openCapstoneModalBtn');
    const closeCapstoneModalBtn = document.getElementById('closeCapstoneModalBtn');

    // =========================================================================
    // 1. Initialization
    // =========================================================================
    init();

    async function init() {
        setupEventListeners();
        loadSavedTrips();
        await verifyBackendStatus();
        await loadSampleDestinations();
    }

    async function verifyBackendStatus() {
        const health = await window.API.checkHealth();
        if (health && health.api_key_configured) {
            aiStatusPill.className = 'ai-status-pill status-live';
            aiStatusPill.querySelector('.status-label').textContent = 'Live Gemini AI';
            aiStatusPill.title = 'Gemini AI API Key is active on the server.';
            if (systemBanner) systemBanner.classList.remove('banner-visible');
        } else {
            aiStatusPill.className = 'ai-status-pill status-demo';
            aiStatusPill.querySelector('.status-label').textContent = 'Demo Mode';
            aiStatusPill.title = 'Curated Offline Engine active (No Gemini API key set).';
        }
    }

    async function loadSampleDestinations() {
        const samples = await window.API.getSampleDestinations();
        if (!destinationsGrid) return;
        destinationsGrid.innerHTML = '';

        samples.forEach(dest => {
            const card = document.createElement('div');
            card.className = 'dest-card';
            card.innerHTML = `
                <div class="dest-card-top">
                    <h3 class="dest-card-name">${escapeHtml(dest.name)}</h3>
                    <span class="dest-card-country">${escapeHtml(dest.country)}</span>
                    <p class="dest-card-tagline">${escapeHtml(dest.tagline)}</p>
                </div>
                <div class="dest-card-bottom">
                    <span class="dest-card-days">✨ Recommended: ${dest.ideal_days} Days</span>
                    <span class="dest-card-cta">Select & Plan &rarr;</span>
                </div>
            `;
            card.addEventListener('click', () => {
                destinationInput.value = dest.name;
                durationDaysSlider.value = dest.ideal_days;
                updateDurationDisplay(dest.ideal_days);
                clearDestBtn.style.display = 'block';
                document.getElementById('planner-section').scrollIntoView({ behavior: 'smooth' });
                destinationInput.focus();
            });
            destinationsGrid.appendChild(card);
        });
    }

    // =========================================================================
    // 2. Event Listeners & Form Controls
    // =========================================================================
    function setupEventListeners() {
        // Mobile Navigation Toggle
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }

        // System Banner Dismiss
        if (closeBannerBtn && systemBanner) {
            closeBannerBtn.addEventListener('click', () => {
                systemBanner.classList.remove('banner-visible');
            });
        }

        // Destination Input Clear button
        destinationInput.addEventListener('input', () => {
            clearDestBtn.style.display = destinationInput.value ? 'block' : 'none';
            destFeedback.textContent = '';
        });

        clearDestBtn.addEventListener('click', () => {
            destinationInput.value = '';
            clearDestBtn.style.display = 'none';
            destinationInput.focus();
        });

        // Quick select destination chips
        document.querySelectorAll('.chip-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const dest = btn.getAttribute('data-dest');
                const days = btn.getAttribute('data-days');
                destinationInput.value = dest;
                clearDestBtn.style.display = 'block';
                destFeedback.textContent = '';
                if (days) {
                    durationDaysSlider.value = days;
                    updateDurationDisplay(days);
                }
            });
        });

        // Trip Duration Slider
        durationDaysSlider.addEventListener('input', (e) => {
            updateDurationDisplay(e.target.value);
        });

        // Traveler Selector Pills
        travelerPills.forEach(pill => {
            pill.addEventListener('click', () => {
                travelerPills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                travelersCountInput.value = pill.getAttribute('data-count');
            });
        });

        // Budget Selector Cards
        budgetCards.forEach(card => {
            card.addEventListener('click', () => {
                budgetCards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                budgetTierInput.value = card.getAttribute('data-tier');
            });
        });

        // Pace Selector Pills
        pacePills.forEach(pill => {
            pill.addEventListener('click', () => {
                pacePills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                travelPaceInput.value = pill.getAttribute('data-pace');
            });
        });

        // Interest Checkboxes Styling
        document.querySelectorAll('.interest-checkbox').forEach(label => {
            const checkbox = label.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    label.classList.add('checked');
                } else {
                    label.classList.remove('checked');
                }
                interestsFeedback.textContent = '';
            });
        });

        // Form Submission
        tripPlannerForm.addEventListener('submit', handleFormSubmit);

        // Action Buttons in Results
        editPreferencesBtn.addEventListener('click', () => {
            document.getElementById('planner-section').scrollIntoView({ behavior: 'smooth' });
            destinationInput.focus();
        });

        regenerateBtn.addEventListener('click', () => {
            handleFormSubmit(new Event('submit'));
        });

        saveTripBtn.addEventListener('click', saveCurrentTrip);

        printTripBtn.addEventListener('click', () => {
            window.print();
        });

        // Modals
        openSavedTripsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            renderSavedTrips();
            savedTripsModal.style.display = 'flex';
        });

        closeSavedTripsModalBtn.addEventListener('click', () => {
            savedTripsModal.style.display = 'none';
        });

        openCapstoneModalBtn.addEventListener('click', (e) => {
            e.preventDefault();
            capstoneModal.style.display = 'flex';
        });

        closeCapstoneModalBtn.addEventListener('click', () => {
            capstoneModal.style.display = 'none';
        });

        // Close modals on clicking backdrop
        window.addEventListener('click', (e) => {
            if (e.target === savedTripsModal) savedTripsModal.style.display = 'none';
            if (e.target === capstoneModal) capstoneModal.style.display = 'none';
        });
    }

    function updateDurationDisplay(days) {
        durationDaysDisplay.textContent = `${days} Day${days > 1 ? 's' : ''}`;
    }

    // =========================================================================
    // 3. Form Submission & API Request Handling
    // =========================================================================
    async function handleFormSubmit(e) {
        if (e) e.preventDefault();

        // 1. Validation
        const destination = destinationInput.value.trim();
        if (!destination || destination.length < 2) {
            destFeedback.textContent = 'Please enter a destination name (at least 2 characters).';
            destinationInput.focus();
            return;
        }

        const selectedInterests = Array.from(
            document.querySelectorAll('input[name="interests"]:checked')
        ).map(cb => cb.value);

        if (selectedInterests.length === 0) {
            interestsFeedback.textContent = 'Please select at least one travel interest.';
            return;
        }

        const payload = {
            destination: destination,
            duration_days: parseInt(durationDaysSlider.value, 10),
            travelers_count: parseInt(travelersCountInput.value, 10),
            budget_tier: budgetTierInput.value,
            currency: currencySelect.value,
            pace: travelPaceInput.value,
            interests: selectedInterests
        };

        // 2. Set UI Loading State
        setLoadingState(true);

        try {
            const result = await window.API.generateItinerary(payload);
            currentItinerary = result;
            renderItinerary(result);
            setLoadingState(false);

            // Smooth scroll to results
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            setLoadingState(false);
            alert(`Could not generate itinerary: ${error.message || 'Please check your inputs and try again.'}`);
        }
    }

    function setLoadingState(isLoading) {
        if (isLoading) {
            loadingSection.style.display = 'block';
            resultsSection.style.display = 'none';
            generateBtn.disabled = true;
            generateBtn.querySelector('.btn-text').textContent = 'Generating Itinerary...';
            generateBtn.querySelector('.btn-spinner').style.display = 'inline-block';
            loadingSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            loadingSection.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.querySelector('.btn-text').textContent = '✨ Generate Personalized Itinerary';
            generateBtn.querySelector('.btn-spinner').style.display = 'none';
        }
    }

    // =========================================================================
    // 4. Itinerary Rendering
    // =========================================================================
    function renderItinerary(data) {
        // Mode badge & explanation
        resultModeBadge.className = `result-mode-badge ${data.mode_badge_class || (data.is_demo ? 'badge-demo' : 'badge-live-ai')}`;
        resultModeText.textContent = data.mode_badge || (data.is_demo ? 'Curated Demo Mode' : 'Live Gemini AI');
        modeExplanationText.textContent = data.mode_explanation || '';

        // Trip header
        resultTripTitle.textContent = data.trip_title || `${data.duration_days}-Day Trip to ${data.destination}`;
        resultTripMeta.textContent = `📍 ${data.destination} • 🗓️ ${data.duration_days} Days • 👥 ${data.travelers_count} Traveler(s) • 💰 ${data.budget_tier} • ⚡ ${data.pace} Pace`;

        // Overview Cards
        overviewText.textContent = data.trip_overview || 'Comprehensive itinerary curated for your travel preferences.';
        bestTimeText.textContent = data.best_time_to_visit || 'Check local seasonal weather before your trip.';
        packingText.textContent = data.packing_recommendations || 'Comfortable shoes, seasonal clothing, and standard travel gear.';

        // Budget Breakdown
        const budget = data.budget_breakdown || {};
        const sym = budget.currency_symbol || '$';
        budgetCurrencySym.textContent = sym;
        budgetGrandTotal.textContent = (budget.grand_total || 0).toLocaleString();
        budgetTierName.textContent = budget.budget_tier || data.budget_tier;
        budgetDailyAvg.textContent = `${sym}${(budget.daily_average || 0).toLocaleString()}`;

        budgetStayTotal.textContent = `${sym}${(budget.stay_total || 0).toLocaleString()}`;
        budgetFoodTotal.textContent = `${sym}${(budget.food_total || 0).toLocaleString()}`;
        budgetActivitiesTotal.textContent = `${sym}${(budget.activities_total || 0).toLocaleString()}`;
        budgetTransportTotal.textContent = `${sym}${(budget.transport_total || 0).toLocaleString()}`;
        budgetDisclaimerText.textContent = budget.disclaimer || 'Figures are rule-based approximations.';

        // Days Schedule Tabs & Content
        renderDaysSchedule(data.itinerary_days, sym);

        // Disclaimers
        if (disclaimerList && data.disclaimers) {
            disclaimerList.innerHTML = '';
            data.disclaimers.forEach(disc => {
                const li = document.createElement('li');
                li.textContent = disc;
                disclaimerList.appendChild(li);
            });
        }
    }

    function renderDaysSchedule(days, currencySymbol) {
        dayFilterTabs.innerHTML = '';
        daysContainer.innerHTML = '';

        if (!days || days.length === 0) {
            daysContainer.innerHTML = '<p class="text-center">No schedule available.</p>';
            return;
        }

        // "All Days" Tab
        const allTab = document.createElement('button');
        allTab.className = 'day-tab-btn active';
        allTab.textContent = 'All Days';
        allTab.addEventListener('click', () => filterDays('all', allTab));
        dayFilterTabs.appendChild(allTab);

        days.forEach(day => {
            // Day filter tab
            const tabBtn = document.createElement('button');
            tabBtn.className = 'day-tab-btn';
            tabBtn.textContent = `Day ${day.day_number}`;
            tabBtn.addEventListener('click', () => filterDays(day.day_number, tabBtn));
            dayFilterTabs.appendChild(tabBtn);

            // Day Card
            const dayCard = document.createElement('div');
            dayCard.className = 'day-card';
            dayCard.id = `day-card-${day.day_number}`;
            dayCard.setAttribute('data-day', day.day_number);

            let activitiesHtml = '';
            (day.activities || []).forEach(act => {
                const costDisplay = act.estimated_cost_display || `${currencySymbol}${(act.estimated_cost_raw || 0).toLocaleString()}`;
                activitiesHtml += `
                    <div class="activity-item">
                        <div class="activity-time-slot">
                            <span>${escapeHtml(act.time_slot || 'Activity')}</span>
                            <span class="activity-time-range">${escapeHtml(act.time_range || '')}</span>
                        </div>
                        <div class="activity-main">
                            <h4>${escapeHtml(act.activity_name || '')}</h4>
                            <span class="activity-location">📍 ${escapeHtml(act.location || '')}</span>
                            <p class="activity-desc">${escapeHtml(act.description || '')}</p>
                            <span class="activity-unverified-tag">ℹ️ ${escapeHtml(act.unverified_notice || 'Estimated timing & fee; confirm locally')}</span>
                        </div>
                        <div class="activity-meta">
                            <span class="activity-cat-badge">${escapeHtml(act.category || 'Sightseeing')}</span>
                            <span class="activity-cost-tag">${costDisplay}</span>
                            <span class="cost-caption">Estimated cost</span>
                        </div>
                    </div>
                `;
            });

            dayCard.innerHTML = `
                <div class="day-card-header">
                    <div class="day-title-wrap">
                        <span class="day-badge">Day ${day.day_number}</span>
                        <h3 class="day-theme-title">${escapeHtml(day.theme || `Day ${day.day_number} Exploration`)}</h3>
                    </div>
                </div>
                <div class="day-activities-list">
                    ${activitiesHtml}
                </div>
            `;

            daysContainer.appendChild(dayCard);
        });
    }

    function filterDays(dayNumber, activeBtn) {
        document.querySelectorAll('.day-tab-btn').forEach(b => b.classList.remove('active'));
        activeBtn.classList.add('active');

        const cards = document.querySelectorAll('.day-card');
        cards.forEach(card => {
            if (dayNumber === 'all' || card.getAttribute('data-day') == dayNumber) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // =========================================================================
    // 5. Saved Trips (Local Storage)
    // =========================================================================
    function loadSavedTrips() {
        try {
            const raw = localStorage.getItem('wanderplan_saved_trips');
            savedTrips = raw ? JSON.parse(raw) : [];
        } catch (e) {
            savedTrips = [];
        }
        updateSavedTripsCount();
    }

    function updateSavedTripsCount() {
        if (savedTripsCount) {
            savedTripsCount.textContent = savedTrips.length;
        }
    }

    function saveCurrentTrip() {
        if (!currentItinerary) {
            alert('No active itinerary to save.');
            return;
        }

        const tripRecord = {
            id: 'trip_' + Date.now(),
            savedAt: new Date().toLocaleDateString(),
            data: currentItinerary
        };

        savedTrips.unshift(tripRecord);
        // Keep max 10
        if (savedTrips.length > 10) savedTrips.pop();

        try {
            localStorage.setItem('wanderplan_saved_trips', JSON.stringify(savedTrips));
            updateSavedTripsCount();
            alert(`Trip to ${currentItinerary.destination} saved to your browser favorites!`);
        } catch (e) {
            alert('Could not save trip to browser storage.');
        }
    }

    function renderSavedTrips() {
        if (!savedTripsList) return;
        if (savedTrips.length === 0) {
            savedTripsList.innerHTML = '<p class="empty-state">No saved itineraries yet. Plan a trip and click "Save Trip" to keep it here.</p>';
            return;
        }

        savedTripsList.innerHTML = '';
        savedTrips.forEach(item => {
            const trip = item.data;
            const div = document.createElement('div');
            div.className = 'saved-trip-item';
            div.innerHTML = `
                <div class="saved-trip-info">
                    <h4>${escapeHtml(trip.trip_title || trip.destination)}</h4>
                    <span class="saved-trip-meta">📍 ${escapeHtml(trip.destination)} • ${trip.duration_days} Days • Saved on ${item.savedAt}</span>
                </div>
                <div class="saved-trip-actions">
                    <button class="btn btn-outline btn-sm load-trip-btn">View</button>
                    <button class="btn btn-secondary btn-sm delete-trip-btn" title="Delete">&times;</button>
                </div>
            `;

            div.querySelector('.load-trip-btn').addEventListener('click', () => {
                currentItinerary = trip;
                renderItinerary(trip);
                savedTripsModal.style.display = 'none';
                resultsSection.style.display = 'block';
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            });

            div.querySelector('.delete-trip-btn').addEventListener('click', () => {
                savedTrips = savedTrips.filter(t => t.id !== item.id);
                localStorage.setItem('wanderplan_saved_trips', JSON.stringify(savedTrips));
                updateSavedTripsCount();
                renderSavedTrips();
            });

            savedTripsList.appendChild(div);
        });
    }

    // Helper: Escape HTML to prevent XSS
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
