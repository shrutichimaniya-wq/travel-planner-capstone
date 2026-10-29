/**
 * WanderPlan AI - API Client Module
 * Communicates with backend Flask endpoints.
 */

const API = {
    /**
     * Checks backend system health and Gemini API key status.
     */
    async checkHealth() {
        try {
            const res = await fetch('/api/health');
            if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error('API health check error:', err);
            return {
                status: 'error',
                mode: 'demo_mode',
                api_key_configured: false,
                message: 'Unable to reach backend health endpoint.'
            };
        }
    },

    /**
     * Fetches curated popular sample destinations.
     */
    async getSampleDestinations() {
        try {
            const res = await fetch('/api/sample-destinations');
            if (!res.ok) throw new Error(`Failed to fetch samples: HTTP ${res.status}`);
            const data = await res.json();
            return data.destinations || [];
        } catch (err) {
            console.error('Failed to load sample destinations:', err);
            return [];
        }
    },

    /**
     * Sends user travel preferences to generate personalized itinerary.
     */
    async generateItinerary(payload) {
        try {
            const res = await fetch('/api/generate-itinerary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || `Generation failed with status ${res.status}`);
            }
            return data;
        } catch (err) {
            console.error('Error generating itinerary:', err);
            throw err;
        }
    }
};

window.API = API;
