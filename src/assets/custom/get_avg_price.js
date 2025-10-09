/**
 * Reusable AJAX function for getting average item prices
 * This function can be used across multiple modules that need item price data
 */

/**
 * Get average price for items based on search query
 * @param {string} query - Search query for items
 * @param {function} onSuccess - Callback function for successful response
 * @param {function} onError - Callback function for error handling
 * @param {function} onLoading - Optional callback function for loading state
 */
function getAvgPrice(query, onSuccess, onError, onLoading) {
    // Validate inputs
    if (!query || typeof query !== 'string') {
        if (onError) onError('Invalid search query');
        return;
    }

    if (query.length < 2) {
        if (onError) onError('Search query must be at least 2 characters');
        return;
    }

    // Show loading state if callback provided
    if (onLoading && typeof onLoading === 'function') {
        onLoading();
    }

    // Make AJAX request
    $.ajax({
        url: '/inventory/api/get_avg_item_price/',
        method: 'GET',
        data: { q: query },
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(response) {
            if (response.success) {
                if (onSuccess && typeof onSuccess === 'function') {
                    onSuccess(response.data, query);
                }
            } else {
                if (onError && typeof onError === 'function') {
                    onError(response.error || 'Search failed');
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Get average price error:', error);
            if (onError && typeof onError === 'function') {
                onError('Failed to get item prices. Please try again.');
            }
        }
    });
}

/**
 * Get CSRF token from cookies
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null if not found
 */
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

/**
 * Debounce function to limit API calls
 * @param {function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {function} Debounced function
 */
function debounce(func, delay) {
    let searchTimeout;
    return function(args) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getAvgPrice,
        getCookie,
        debounce
    };
}