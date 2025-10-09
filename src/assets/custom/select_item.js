/**
 * Reusable Select2 AJAX function for item selection
 * This function initializes Select2 with AJAX for selecting items from the caitem table
 */

// Helper function to get CSRF token
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
 * Initialize Select2 with AJAX for item selection
 * @param {string} selector - CSS selector for the element to initialize
 * @param {object} options - Additional options to override defaults
 */
window.initItemSelect = function(selector, options = {}) {
    // Default configuration
    const defaultConfig = {
        placeholder: 'Search for an item...',
        allowClear: true,
        minimumInputLength: 1,
        ajax: {
            url: '/crossapp/api/items/',
            dataType: 'json',
            delay: 250,
            beforeSend: function(xhr, settings) {
                console.log("AJAX beforeSend called for item selection");
                // Get CSRF token
                var csrftoken = getCookie('csrftoken') || $('[name=csrfmiddlewaretoken]').val();
                if (csrftoken) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    console.log("CSRF token set:", csrftoken);
                } else {
                    console.error("CSRF token not found");
                }
            },
            data: function (params) {
                var query = {
                    search: params.term,
                    page: params.page || 1
                };
                // Add CSRF token to data as well
                var csrftoken = getCookie('csrftoken') || $('[name=csrfmiddlewaretoken]').val();
                if (csrftoken) {
                    query.csrfmiddlewaretoken = csrftoken;
                }
                console.log("AJAX data for item selection:", query);
                return query;
            },
            processResults: function (data, params) {
                console.log("AJAX response received for item selection:", data);
                params.page = params.page || 1;

                var results = [];
                if (data.items && Array.isArray(data.items)) {
                    results = data.items.map(function(item) {
                        return {
                            id: item.xitem,
                            text: item.xitem + ' - ' + (item.xdesc || 'No Description'),
                            data: item // Store full item data for potential use
                        };
                    });
                } else {
                    console.warn('No items found in response or items is not an array:', data);
                }

                return {
                    results: results,
                    pagination: {
                        more: data.pagination ? data.pagination.more : false
                    }
                };
            },
            error: function(xhr, status, error) {
                console.error("AJAX error in item selection:", status, error);
                console.error("Response:", xhr.responseText);
            }
        },
        templateResult: function(item) {
            if (item.loading) {
                return item.text;
            }
            // Custom template for displaying results
            var $result = $(
                '<div class="select2-result-item">' +
                    '<div class="select2-result-item__title">' + (item.text || '') + '</div>' +
                '</div>'
            );
            return $result;
        },
        templateSelection: function(item) {
            // Custom template for selected item
            return item.text || item.id;
        }
    };

    // Merge user options with defaults
    const config = $.extend(true, {}, defaultConfig, options);

    try {
        console.log("Initializing Select2 for item selection on:", selector);
        $(selector).select2(config);
        console.log("Select2 item selection initialized successfully for:", selector);
    } catch (error) {
        console.error("Error initializing Select2 for item selection:", error);
    }
};

// Make the function available globally
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initItemSelect: window.initItemSelect };
}
