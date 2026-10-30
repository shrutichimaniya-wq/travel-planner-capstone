/**
 * WanderPlan AI - Application Controller
 * Manages form interactions, itinerary rendering, Leaflet maps,
 * Open-Meteo weather display, destination search, PDF export, and local storage.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current active state in memory
    let currentItinerary = null;
    let savedTrips = [];
    let allDestinations = [];
    let leafletMapInstance = null;
    let mapMarkersLayer = null;

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
    const destSearchInput = document.getElementById('destSearchInput');
    const destTabBtns = document.querySelectorAll('.dest-tab-btn');

    // DOM Elements - Results Header & Mode
    const resultModeBadge = document.getElementById('resultModeBadge');
    const resultModeText = document.getElementById('resultModeText');
    const resultTripTitle = document.getElementById('resultTripTitle');
    const resultTripMeta = document.getElementById('resultTripMeta');
    const modeExplanationBox = document.getElementById('modeExplanationBox');
    const modeExplanationText = document.getElementById('modeExplanationText');

    // DOM Elements - Weather Widget
    const weatherCard = document.getElementById('weatherCard');
    const weatherIcon = document.getElementById('weatherIcon');
    const weatherTemp = document.getElementById('weatherTemp');
    const weatherCondition = document.getElementById('weatherCondition');
    const weatherFeelsLike = document.getElementById('weatherFeelsLike');
    const weatherHumidity = document.getElementById('weatherHumidity');
    const weatherWind = document.getElementById('weatherWind');
    const weatherRain = document.getElementById('weatherRain');
    const forecastStrip = document.getElementById('forecastStrip');

    // DOM Elements - Overview Details
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

    // DOM Elements - Schedule, Map & Disclaimers
    const dayFilterTabs = document.getElementById('dayFilterTabs');
    const daysContainer = document.getElementById('daysContainer');
    const disclaimerList = document.getElementById('disclaimerList');
    const resetMapBtn = document.getElementById('resetMapBtn');

    // DOM Elements - Actions
    const editPreferencesBtn = document.getElementById('editPreferencesBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const saveTripBtn = document.getElementById('saveTripBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const printTripBtn = document.getElementById('printTripBtn');

    // DOM Elements - Modals & Toasts
    const savedTripsModal = document.getElementById('savedTripsModal');
    const openSavedTripsBtn = document.getElementById('openSavedTripsBtn');
    const closeSavedTripsModalBtn = document.getElementById('closeSavedTripsModalBtn');
    const savedTripsList = document.getElementById('savedTripsList');
    const savedTripsCount = document.getElementById('savedTripsCount');

    const capstoneModal = document.getElementById('capstoneModal');
    const openCapstoneModalBtn = document.getElementById('openCapstoneModalBtn');
    const closeCapstoneModalBtn = document.getElementById('closeCapstoneModalBtn');

    const toastNotification = document.getElementById('toastNotification');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');

    // =========================================================================
    // 1. Initialization
    // =========================================================================
    init();

    async function init() {
        setupEventListeners();
        loadSavedTrips();
        await verifyBackendStatus();
        await loadAllDestinations();
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

    // =========================================================================
    // 2. Destination Explorer (Cards, Search & Filter)
    // =========================================================================
    async function loadAllDestinations() {
        allDestinations = await window.API.getSampleDestinations();
        renderDestinationCards(allDestinations);
    }

    function renderDestinationCards(destinations) {
        if (!destinationsGrid) return;
        destinationsGrid.innerHTML = '';

        if (!destinations || destinations.length === 0) {
            destinationsGrid.innerHTML = `
                <div class="empty-dest-search">
                    <span class="empty-icon">🌍</span>
                    <h4>No destinations matched your search</h4>
                    <p>Try searching for another city, country, or vibe like "Beach", "Historic", or "Futuristic".</p>
                </div>
            `;
            return;
        }

        destinations.forEach(dest => {
            const card = document.createElement('div');
            card.className = 'dest-card';
            
            // Build attractions badges
            const attractionsHtml = (dest.popular_attractions || [])
                .map(att => `<span class="attraction-pill">📍 ${escapeHtml(att)}</span>`)
                .join('');

            card.innerHTML = `
                <div class="dest-card-image-wrap">
                    <img 
                        src="${escapeHtml(dest.image_url)}" 
                        alt="${escapeHtml(dest.name)}, ${escapeHtml(dest.country)}"
                        class="dest-card-img"
                        loading="lazy"
                        onerror="this.onerror=null; this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 600 400%22><rect fill=%22%230284c7%22 width=%22600%22 height=%22400%22/><text fill=%22white%22 x=%2250%%22 y=%2250%%22 font-family=%22sans-serif%22 font-size=%2228%22 text-anchor=%22middle%22>${escapeHtml(dest.name)}</text></svg>';"
                    >
                    <span class="dest-badge-continent">${escapeHtml(dest.continent || 'Global')}</span>
                    <span class="dest-badge-vibe">${escapeHtml(dest.vibe || 'Travel')}</span>
                </div>
                <div class="dest-card-body">
                    <div class="dest-card-header-row">
                        <div>
                            <h3 class="dest-card-name">${escapeHtml(dest.name)}</h3>
                            <span class="dest-card-country">${escapeHtml(dest.country)}</span>
                        </div>
                        <span class="dest-ideal-days">🗓️ ${dest.ideal_days} Days</span>
                    </div>
                    <p class="dest-card-tagline">${escapeHtml(dest.tagline)}</p>
                    <p class="dest-card-desc">${escapeHtml(dest.description)}</p>
                    
                    <div class="dest-attractions-wrap">
                        <span class="attractions-label">Top Sights:</span>
                        <div class="attractions-list">${attractionsHtml}</div>
                    </div>
                </div>
                <div class="dest-card-bottom">
                    <span class="dest-season">🌤️ Best: ${escapeHtml(dest.best_time || 'Year-round')}</span>
                    <button type="button" class="btn btn-primary btn-sm select-dest-btn" data-dest="${escapeHtml(dest.name)}" data-days="${dest.ideal_days}">
                        Plan Trip &rarr;
                    </button>
                </div>
            `;

            // Select & Populate Button
            card.querySelector('.select-dest-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                selectDestination(dest.name, dest.ideal_days);
            });

            // Clicking the card body also auto-fills
            card.addEventListener('click', () => {
                selectDestination(dest.name, dest.ideal_days);
            });

            destinationsGrid.appendChild(card);
        });
    }

    function selectDestination(name, days) {
        destinationInput.value = name;
        if (days) {
            durationDaysSlider.value = days;
            updateDurationDisplay(days);
        }
        clearDestBtn.style.display = 'block';
        destFeedback.textContent = '';
        document.getElementById('planner-section').scrollIntoView({ behavior: 'smooth' });
        destinationInput.focus();
        showToast(`Selected ${name} for your journey!`, '✈️');
    }

    // Destination Search Input Filter
    if (destSearchInput) {
        destSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim().toLowerCase();
            filterDestinations(query, getActiveContinentFilter());
        });
    }

    // Continent Filter Tabs
    destTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            destTabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.getAttribute('data-filter');
            const query = destSearchInput ? destSearchInput.value.trim().toLowerCase() : '';
            filterDestinations(query, filter);
        });
    });

    function getActiveContinentFilter() {
        const activeBtn = document.querySelector('.dest-tab-btn.active');
        return activeBtn ? activeBtn.getAttribute('data-filter') : 'all';
    }

    function filterDestinations(query, continent) {
        let filtered = allDestinations;

        if (continent && continent !== 'all') {
            filtered = filtered.filter(d => (d.continent || '').toLowerCase() === continent.toLowerCase());
        }

        if (query) {
            filtered = filtered.filter(d => 
                d.name.toLowerCase().includes(query) ||
                d.country.toLowerCase().includes(query) ||
                (d.vibe && d.vibe.toLowerCase().includes(query)) ||
                (d.tagline && d.tagline.toLowerCase().includes(query)) ||
                (d.popular_attractions && d.popular_attractions.some(a => a.toLowerCase().includes(query)))
            );
        }

        renderDestinationCards(filtered);
    }

    // =========================================================================
    // 3. Form Event Listeners & Controls
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
                selectDestination(dest, days);
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

        downloadPdfBtn.addEventListener('click', downloadItineraryPdf);

        printTripBtn.addEventListener('click', () => {
            window.print();
        });

        if (resetMapBtn) {
            resetMapBtn.addEventListener('click', recenterMap);
        }

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
    // 4. Form Submission & Generation
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

            // Invalidate Leaflet Map layout after section becomes visible
            setTimeout(() => {
                if (leafletMapInstance) {
                    leafletMapInstance.invalidateSize();
                }
            }, 300);

            showToast(`Itinerary for ${result.destination} ready!`, '✨');

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
            generateBtn.querySelector('.btn-text').textContent = 'Synthesizing Itinerary...';
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
    // 5. Itinerary Rendering
    // =========================================================================
    function renderItinerary(data) {
        // Mode badge & explanation
        resultModeBadge.className = `result-mode-badge ${data.mode_badge_class || (data.is_demo ? 'badge-demo' : 'badge-live-ai')}`;
        resultModeText.textContent = data.mode_badge || (data.is_demo ? 'Curated Demo Mode' : 'Live Gemini AI');
        modeExplanationText.textContent = data.mode_explanation || '';

        // Trip header
        resultTripTitle.textContent = data.trip_title || `${data.duration_days}-Day Trip to ${data.destination}`;
        resultTripMeta.textContent = `📍 ${data.destination} • 🗓️ ${data.duration_days} Days • 👥 ${data.travelers_count} Traveler(s) • 💰 ${data.budget_tier} • ⚡ ${data.pace} Pace`;

        // Live Weather Rendering
        renderWeather(data.weather);

        // Overview Cards
        overviewText.textContent = data.trip_overview || 'Comprehensive itinerary curated for your travel preferences.';
        bestTimeText.textContent = data.best_time_to_visit || 'Check seasonal weather prior to travel.';
        packingText.textContent = data.packing_recommendations || 'Comfortable shoes, versatile apparel, and travel essentials.';

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

        // Render Leaflet Interactive Map
        renderInteractiveMap(data);

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

    // =========================================================================
    // 6. Live Weather Widget (Open-Meteo)
    // =========================================================================
    function renderWeather(weather) {
        if (!weather || !weather.is_available) {
            weatherIcon.textContent = '🌤️';
            weatherTemp.textContent = '--';
            weatherCondition.textContent = weather ? (weather.message || 'Forecast unavailable') : 'Forecast unavailable';
            weatherFeelsLike.textContent = 'Check local weather before travel';
            weatherHumidity.textContent = '--%';
            weatherWind.textContent = '-- km/h';
            weatherRain.textContent = '--%';
            forecastStrip.innerHTML = '<span class="forecast-empty">5-day outlook unavailable for this location</span>';
            return;
        }

        const curr = weather.current || {};
        weatherIcon.textContent = curr.icon || '☀️';
        weatherTemp.textContent = curr.temperature_c !== undefined ? curr.temperature_c : '--';
        weatherCondition.textContent = curr.condition || 'Clear';
        weatherFeelsLike.textContent = `Feels like ${curr.feels_like_c !== undefined ? curr.feels_like_c : '--'}°C (${curr.temperature_f || '--'}°F)`;
        weatherHumidity.textContent = `${curr.humidity || 0}%`;
        weatherWind.textContent = `${curr.wind_speed_kmh || 0} km/h`;
        weatherRain.textContent = `${Math.round((curr.precipitation_mm || 0) * 10)}%`;

        // Render 5-day forecast strip
        forecastStrip.innerHTML = '';
        const daily = weather.daily_forecast || [];
        daily.forEach(d => {
            const dayName = new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' });
            const item = document.createElement('div');
            item.className = 'forecast-day-item';
            item.innerHTML = `
                <span class="f-day">${dayName}</span>
                <span class="f-icon">${d.icon}</span>
                <span class="f-temp">${d.max_temp_c !== null ? d.max_temp_c : '--'}° <small>${d.min_temp_c !== null ? d.min_temp_c : '--'}°</small></span>
            `;
            forecastStrip.appendChild(item);
        });
    }

    // =========================================================================
    // 7. Interactive Leaflet Map
    // =========================================================================
    function renderInteractiveMap(data) {
        const mapContainer = document.getElementById('travelMap');
        if (!mapContainer || typeof L === 'undefined') return;

        // Default or resolved coordinates
        const coords = data.destination_coordinates || { lat: 48.8566, lon: 2.3522 };
        const centerLat = coords.lat || 48.8566;
        const centerLon = coords.lon || 2.3522;

        // Initialize map instance if not existing
        if (!leafletMapInstance) {
            leafletMapInstance = L.map('travelMap').setView([centerLat, centerLon], 12);

            // OpenStreetMap tile layer (Clean, standard, fast)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(leafletMapInstance);

            mapMarkersLayer = L.layerGroup().addTo(leafletMapInstance);
        } else {
            leafletMapInstance.setView([centerLat, centerLon], 12);
            if (mapMarkersLayer) {
                mapMarkersLayer.clearLayers();
            }
        }

        // Add markers for all daily activities
        const days = data.itinerary_days || [];
        const markerPoints = [];

        days.forEach(day => {
            (day.activities || []).forEach(act => {
                if (act.latitude && act.longitude) {
                    const lat = act.latitude;
                    const lon = act.longitude;
                    markerPoints.push([lat, lon]);

                    // Category color dot
                    const cat = (act.category || '').toLowerCase();
                    let color = '#0284c7';
                    if (cat.includes('food')) color = '#e11d48';
                    else if (cat.includes('culture') || cat.includes('heritage')) color = '#d97706';
                    else if (cat.includes('nature') || cat.includes('adventure')) color = '#059669';

                    // Custom SVG circle marker
                    const customMarker = L.circleMarker([lat, lon], {
                        radius: 8,
                        fillColor: color,
                        color: '#ffffff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.9
                    });

                    // Popup Content
                    const popupContent = `
                        <div class="map-popup-wrap">
                            <span class="popup-day">Day ${day.day_number} • ${escapeHtml(act.time_slot || '')}</span>
                            <h4 class="popup-title">${escapeHtml(act.activity_name || '')}</h4>
                            <span class="popup-location">📍 ${escapeHtml(act.location || '')}</span>
                            <p class="popup-desc">${escapeHtml(act.description || '')}</p>
                            <div class="popup-meta">
                                <span class="popup-cat">${escapeHtml(act.category || 'Sightseeing')}</span>
                                <strong class="popup-cost">${escapeHtml(act.estimated_cost_display || '')}</strong>
                            </div>
                        </div>
                    `;

                    customMarker.bindPopup(popupContent);
                    mapMarkersLayer.addLayer(customMarker);
                }
            });
        });

        // Fit map bounds to show all markers if multiple
        if (markerPoints.length > 1) {
            try {
                const bounds = L.latLngBounds(markerPoints);
                leafletMapInstance.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
            } catch (err) {
                console.warn('Error adjusting map bounds:', err);
            }
        }
    }

    function recenterMap() {
        if (!leafletMapInstance || !currentItinerary) return;
        const coords = currentItinerary.destination_coordinates || { lat: 48.8566, lon: 2.3522 };
        leafletMapInstance.setView([coords.lat, coords.lon], 12);
        showToast('Map recentered to destination', '📍');
    }

    // =========================================================================
    // 8. Day-by-Day Schedule & Tabs
    // =========================================================================
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
    // 9. PDF Download (html2pdf.js)
    // =========================================================================
    function downloadItineraryPdf() {
        if (!currentItinerary) {
            alert('No active itinerary to download.');
            return;
        }

        const element = document.getElementById('printableItinerary');
        if (!element) return;

        showToast('Preparing your travel itinerary PDF...', '📥');

        // Check if html2pdf is available
        if (typeof html2pdf === 'undefined') {
            window.print();
            return;
        }

        // Temporarily hide actions bar during PDF capture
        const actionsBar = document.getElementById('resultActionsBar');
        const mapSection = document.getElementById('mapSectionCard');
        if (actionsBar) actionsBar.style.display = 'none';

        const opt = {
            margin: [10, 10, 10, 10],
            filename: `WanderPlan_${(currentItinerary.destination || 'Trip').replace(/\s+/g, '_')}_Itinerary.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, logging: false },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        html2pdf().set(opt).from(element).save().then(() => {
            if (actionsBar) actionsBar.style.display = 'flex';
            showToast('PDF downloaded successfully!', '✅');
        }).catch(err => {
            console.error('PDF generation error:', err);
            if (actionsBar) actionsBar.style.display = 'flex';
            window.print();
        });
    }

    // =========================================================================
    // 10. Saved Trips (Local Storage)
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
            savedAt: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            data: currentItinerary
        };

        savedTrips.unshift(tripRecord);
        if (savedTrips.length > 10) savedTrips.pop();

        try {
            localStorage.setItem('wanderplan_saved_trips', JSON.stringify(savedTrips));
            updateSavedTripsCount();
            showToast(`Trip to ${currentItinerary.destination} saved!`, '⭐');
        } catch (e) {
            alert('Could not save trip to browser storage.');
        }
    }

    function renderSavedTrips() {
        if (!savedTripsList) return;
        if (savedTrips.length === 0) {
            savedTripsList.innerHTML = '<p class="empty-state">No saved itineraries yet. Plan a trip and click "Save" to keep it here.</p>';
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
                    <span class="saved-trip-meta">📍 ${escapeHtml(trip.destination)} • ${trip.duration_days} Days • ${trip.budget_tier} • Saved on ${item.savedAt}</span>
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
                setTimeout(() => {
                    if (leafletMapInstance) leafletMapInstance.invalidateSize();
                }, 300);
            });

            div.querySelector('.delete-trip-btn').addEventListener('click', () => {
                savedTrips = savedTrips.filter(t => t.id !== item.id);
                localStorage.setItem('wanderplan_saved_trips', JSON.stringify(savedTrips));
                updateSavedTripsCount();
                renderSavedTrips();
                showToast('Trip removed from favorites', '🗑️');
            });

            savedTripsList.appendChild(div);
        });
    }

    // =========================================================================
    // 11. Toast Notifications
    // =========================================================================
    function showToast(message, icon = 'ℹ️') {
        if (!toastNotification) return;
        toastIcon.textContent = icon;
        toastMessage.textContent = message;
        toastNotification.style.display = 'flex';
        toastNotification.classList.add('toast-visible');

        setTimeout(() => {
            toastNotification.classList.remove('toast-visible');
            setTimeout(() => {
                toastNotification.style.display = 'none';
            }, 300);
        }, 3000);
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
