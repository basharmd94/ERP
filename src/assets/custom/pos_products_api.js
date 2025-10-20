/**
 * POS Products API JavaScript Module
 * Handles product search functionality for POS system
 */

// Product Search Configuration
const PRODUCT_SEARCH_CONFIG = {
    API_URL: '/api/pos/products/',
    MIN_INPUT_LENGTH: 1,
    DELAY: 250,
    PLACEHOLDER: 'Search products by name, code, or barcode...'
};

/**
 * Initialize product search functionality with Select2
 * @param {string} selector - CSS selector for the search input
 * @param {function} onProductSelect - Callback function when product is selected
 */
function initializeProductSearch(selector = '#product-search', onProductSelect = null) {

    $(selector).select2({
        placeholder: PRODUCT_SEARCH_CONFIG.PLACEHOLDER,
        allowClear: true,
        minimumInputLength: PRODUCT_SEARCH_CONFIG.MIN_INPUT_LENGTH,
        ajax: {
            url: PRODUCT_SEARCH_CONFIG.API_URL,
            dataType: 'json',
            delay: PRODUCT_SEARCH_CONFIG.DELAY,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                
                return {
                    results: data.results || [],
                    pagination: data.pagination || { more: false }
                };
            },
            cache: true
        },
        templateResult: function(item) {
            if (item.loading) return item.text;

            const price = item.xstdprice || item.price || 0;
            const stock = item.stock || 0;

            return $(`
                <div class="product-result">
                    <div class="fw-bold">${item.text}</div>
                    <div class="small text-muted">
                        Price: ৳${parseFloat(price).toFixed(2)} | Stock: ${parseFloat(stock).toFixed(2)} | Barcode: ${item.xbarcode || 'N/A'}
                    </div>
                </div>
            `);
        },
        templateSelection: function(item) {
            return item.text || item.id;
        }
    });

    // Handle product selection
    $(selector).on('select2:select', function (e) {
        const product = e.params.data;

        // Call the provided callback or default behavior
        if (onProductSelect && typeof onProductSelect === 'function') {
            onProductSelect(product);
        } else if (typeof addToCart === 'function') {
            // Fallback to global addToCart function if available
            addToCart(product);
        } else {
            console.warn('No product selection handler provided');
        }

        // Clear the selection
        $(this).val(null).trigger('change');
    });
}

/**
 * Search for a product by barcode
 * @param {string} barcode - The barcode to search for
 * @param {function} onSuccess - Callback function when product is found
 * @param {function} onError - Callback function when product is not found or error occurs
 */
function searchProductByBarcode(barcode, onSuccess = null, onError = null) {
    if (!barcode || barcode.trim() === '') {
        console.warn('Barcode is required for search');
        return;
    }

    $.ajax({
        url: PRODUCT_SEARCH_CONFIG.API_URL,
        data: { search: barcode.trim() },
        success: function(data) {
            if (data.results && data.results.length > 0) {
                const product = data.results[0];

                // Call the provided success callback or default behavior
                if (onSuccess && typeof onSuccess === 'function') {
                    onSuccess(product);
                } else if (typeof addToCart === 'function') {
                    // Fallback to global addToCart function if available
                    addToCart(product);
                } else {
                    console.warn('No success handler provided for barcode search');
                }
            } else {
                // Product not found
                if (onError && typeof onError === 'function') {
                    onError('Product not found');
                } else if (typeof toastr !== 'undefined') {
                    toastr.error('Product not found');
                } else {
                    console.error('Product not found');
                }
            }
        },
        error: function(xhr, status, error) {
            const errorMessage = 'Error searching product';

            if (onError && typeof onError === 'function') {
                onError(errorMessage);
            } else if (typeof toastr !== 'undefined') {
                toastr.error(errorMessage);
            } else {
                console.error(errorMessage, error);
            }
        }
    });
}

/**
 * Search for products with custom parameters
 * @param {object} searchParams - Search parameters
 * @param {function} onSuccess - Success callback
 * @param {function} onError - Error callback
 */
function searchProducts(searchParams, onSuccess, onError) {
    $.ajax({
        url: PRODUCT_SEARCH_CONFIG.API_URL,
        data: searchParams,
        success: function(data) {
            if (onSuccess && typeof onSuccess === 'function') {
                onSuccess(data);
            }
        },
        error: function(xhr, status, error) {
            if (onError && typeof onError === 'function') {
                onError(error);
            }
        }
    });
}

/**
 * Update the API URL configuration
 * @param {string} newUrl - New API URL
 */
function setProductSearchApiUrl(newUrl) {
    PRODUCT_SEARCH_CONFIG.API_URL = newUrl;
}

// Export functions for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeProductSearch,
        searchProductByBarcode,
        searchProducts,
        setProductSearchApiUrl,
        PRODUCT_SEARCH_CONFIG
    };
}

// Make functions globally available
window.PosProductsAPI = {
    initializeProductSearch,
    searchProductByBarcode,
    searchProducts,
    setProductSearchApiUrl,
    PRODUCT_SEARCH_CONFIG
};
