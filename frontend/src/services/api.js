// API Service - Centralized API calls
const API_BASE = '/api';

export const api = {
    // Clothes
    async getClothes(type = null, excludeLaundry = false) {
        const params = new URLSearchParams();
        if (type) params.append('clothing_type', type);
        if (excludeLaundry) params.append('exclude_laundry', 'true');
        const res = await fetch(`${API_BASE}/clothes?${params}`);
        return res.json();
    },

    async addClothing(formData) {
        const res = await fetch(`${API_BASE}/clothes`, {
            method: 'POST',
            body: formData
        });
        return res.json();
    },

    async deleteClothing(id) {
        const res = await fetch(`${API_BASE}/clothes/${id}`, { method: 'DELETE' });
        return res.json();
    },

    async toggleLaundry(id) {
        const res = await fetch(`${API_BASE}/clothes/${id}/laundry`, { method: 'POST' });
        return res.json();
    },

    async toggleFavorite(id) {
        const res = await fetch(`${API_BASE}/clothes/${id}/favorite`, { method: 'POST' });
        return res.json();
    },

    // Classification
    async classifyImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API_BASE}/classify`, {
            method: 'POST',
            body: formData
        });
        return res.json();
    },

    // Outfits
    async getOutfitSuggestions(occasion, weather, num = 4) {
        const params = new URLSearchParams({
            occasion,
            temp: weather.temp,
            condition: weather.condition,
            num
        });
        const res = await fetch(`${API_BASE}/outfits/suggest?${params}`);
        return res.json();
    },

    async logOutfit(outfit) {
        const res = await fetch(`${API_BASE}/outfits/log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(outfit)
        });
        return res.json();
    },

    async getOutfitHistory(limit = 10) {
        const res = await fetch(`${API_BASE}/outfits/history?limit=${limit}`);
        return res.json();
    },

    // Weather
    async getWeather() {
        const res = await fetch(`${API_BASE}/weather`);
        return res.json();
    },

    // Stats
    async getStats() {
        const res = await fetch(`${API_BASE}/stats`);
        return res.json();
    },

    async clearAll() {
        const res = await fetch(`${API_BASE}/clear-all`, { method: 'DELETE' });
        return res.json();
    },

    async deduplicate() {
        const res = await fetch(`${API_BASE}/clothes/deduplicate`, { method: 'POST' });
        return res.json();
    }
};
