/**
 * SGLM API Client
 * Gestion des appels API et de l'authentification
 */

const API_BASE_URL = '/api/v1';

// Gestion du token
const TokenManager = {
    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    },

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    isAuthenticated() {
        return !!this.getAccessToken();
    }
};

// Client API
class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = TokenManager.getAccessToken();

        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };

        if (token && !options.skipAuth) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);

            if (response.status === 401 && !options.skipAuth) {
                // Token expiré, essayer de refresh
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry la requête
                    return this.request(endpoint, options);
                } else {
                    // Redirect to login
                    window.location.href = '/login';
                    throw new Error('Session expirée');
                }
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erreur API');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async refreshToken() {
        const refreshToken = TokenManager.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${refreshToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                TokenManager.setTokens(data.access_token);
                return true;
            }
        } catch (error) {
            console.error('Refresh token error:', error);
        }

        return false;
    }

    // Auth endpoints
    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
            skipAuth: true
        });

        TokenManager.setTokens(data.access_token, data.refresh_token);
        TokenManager.setUser(data.user);
        return data;
    }

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } finally {
            TokenManager.clearTokens();
            window.location.href = '/login';
        }
    }

    // Users endpoints
    async getUsers(page = 1, perPage = 20) {
        return this.request(`/users?page=${page}&per_page=${perPage}`);
    }

    async getUser(userId) {
        return this.request(`/users/${userId}`);
    }

    async createUser(userData) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async updateUser(userId, userData) {
        return this.request(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return this.request(`/users/${userId}`, { method: 'DELETE' });
    }

    async getGroups() {
        return this.request('/users/groups');
    }

    // Assets endpoints
    async getAssetTypes() {
        return this.request('/assets/types');
    }

    async getAssets(assetType, page = 1, filters = {}) {
        const params = new URLSearchParams({ page, per_page: 20, ...filters });
        return this.request(`/assets/${assetType}?${params}`);
    }

    async getAsset(assetType, assetId) {
        return this.request(`/assets/${assetType}/${assetId}`);
    }

    async createAsset(assetType, assetData) {
        return this.request(`/assets/${assetType}`, {
            method: 'POST',
            body: JSON.stringify(assetData)
        });
    }

    async updateAsset(assetType, assetId, assetData) {
        return this.request(`/assets/${assetType}/${assetId}`, {
            method: 'PUT',
            body: JSON.stringify(assetData)
        });
    }

    async deleteAsset(assetType, assetId) {
        return this.request(`/assets/${assetType}/${assetId}`, {
            method: 'DELETE'
        });
    }

    // Missions endpoints
    async getMissions(page = 1, filters = {}) {
        const params = new URLSearchParams({ page, per_page: 20, ...filters });
        return this.request(`/missions?${params}`);
    }

    async getMission(missionId) {
        return this.request(`/missions/${missionId}`);
    }

    async createMission(missionData) {
        return this.request('/missions', {
            method: 'POST',
            body: JSON.stringify(missionData)
        });
    }

    async updateMission(missionId, missionData) {
        return this.request(`/missions/${missionId}`, {
            method: 'PUT',
            body: JSON.stringify(missionData)
        });
    }

    async assignAssets(missionId, assetIds) {
        return this.request(`/missions/${missionId}/assign`, {
            method: 'POST',
            body: JSON.stringify({ asset_ids: assetIds })
        });
    }

    async unassignAssets(missionId, assetIds) {
        return this.request(`/missions/${missionId}/unassign`, {
            method: 'POST',
            body: JSON.stringify({ asset_ids: assetIds })
        });
    }

    // Reports endpoints
    async getDashboard() {
        return this.request('/reports/dashboard');
    }

    async getAssetsReport(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/reports/assets?${params}`);
    }

    async getMissionsReport(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/reports/missions?${params}`);
    }

    async getActivityReport(days = 30) {
        return this.request(`/reports/activity?days=${days}`);
    }

    // Logs endpoints
    async getAssetLogs(filters = {}) {
        const params = new URLSearchParams({ page: 1, per_page: 50, ...filters });
        return this.request(`/logs/assets?${params}`);
    }

    async getAdminLogs(filters = {}) {
        const params = new URLSearchParams({ page: 1, per_page: 50, ...filters });
        return this.request(`/logs/admin?${params}`);
    }

    async getMissionLogs(missionId) {
        return this.request(`/logs/missions/${missionId}`);
    }
}

// Export une instance unique
const api = new APIClient();

// Fonction utilitaire pour afficher les erreurs
function showError(message, containerId = 'error-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${message}
            </div>
        `;
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }
}

// Fonction utilitaire pour afficher les succès
function showSuccess(message, containerId = 'success-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-success">
                ${message}
            </div>
        `;
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }
}

// Fonction utilitaire pour formater les dates
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Fonction utilitaire pour formater les dates courtes
function formatShortDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}
