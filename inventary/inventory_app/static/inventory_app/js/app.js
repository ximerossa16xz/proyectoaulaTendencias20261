// Shared API utilities for inventory app
const API_BASE = '/api/inventory/';

async function fetchAPI(endpoint, options = {}) {
    try {
        const method = (options.method || 'GET').toUpperCase();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
            headers['X-CSRFToken'] = getCookie('csrftoken');
        }

        const response = await fetch(API_BASE + endpoint, {
            headers,
            ...options
        });
        
        if (!response.ok) {
            const contentType = response.headers.get('content-type') || '';
            let message = `API Error: ${response.status}`;

            if (contentType.includes('application/json')) {
                const errorData = await response.json();
                message = formatAPIError(errorData, response.status);
            }

            throw new Error(message);
        }

        if (response.status === 204) {
            return null;
        }

        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            return await response.json();
        }

        return await response.text();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHtml);
}

function showLoading(element) {
    element.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatAPIError(errorData, fallbackStatus) {
    if (!errorData) {
        return `API Error: ${fallbackStatus}`;
    }

    if (typeof errorData === 'string') {
        return errorData;
    }

    if (errorData.detail) {
        return errorData.detail;
    }

    const fragments = Object.entries(errorData).map(([field, value]) => {
        if (Array.isArray(value)) {
            return `${field}: ${value.join(', ')}`;
        }
        if (typeof value === 'object' && value !== null) {
            return `${field}: ${JSON.stringify(value)}`;
        }
        return `${field}: ${value}`;
    });

    return fragments.join(' | ') || `API Error: ${fallbackStatus}`;
}

function getListData(payload) {
    if (Array.isArray(payload)) {
        return payload;
    }

    if (Array.isArray(payload?.results)) {
        return payload.results;
    }

    return [];
}

// Export for use in templates
window.InventoryApp = {
    fetchAPI,
    formatAPIError,
    getListData,
    showAlert,
    showLoading,
    getCookie
};
