/**
 * XCode API Utilities
 * Centralized JavaScript utilities for handling xcode API calls
 * Supports Select2 integration and AJAX requests
 */

class XCodeAPI {
    constructor() {
        this.baseUrl = '/api/xcodes/';
    }

    /**
     * Get the API URL for a specific xtype
     * @param {string} xtype - The xcode type (brands, units, etc.)
     * @returns {string} The API URL
     */
    getApiUrl(xtype) {
        return `${this.baseUrl}${xtype}/`;
    }

    /**
     * Initialize Select2 for xcode dropdown
     * @param {string} selector - jQuery selector for the element
     * @param {string} xtype - The xcode type
     * @param {object} options - Additional Select2 options
     */
    initSelect2(selector, xtype, options = {}) {
        const defaultOptions = {
            ajax: {
                url: this.getApiUrl(xtype),
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term,
                        page: params.page
                    };
                },
                processResults: function (data, params) {
                    return {
                        results: data.results,
                        pagination: data.pagination
                    };
                },
                cache: true
            },
            placeholder: `Select ${xtype.replace('-', ' ')}...`,
            allowClear: true,
            minimumInputLength: 0
        };

        // Merge with custom options
        const finalOptions = $.extend(true, {}, defaultOptions, options);
        
        $(selector).select2(finalOptions);
    }

    /**
     * Fetch xcode data via AJAX
     * @param {string} xtype - The xcode type
     * @param {string} searchTerm - Optional search term
     * @returns {Promise} jQuery AJAX promise
     */
    fetchData(xtype, searchTerm = '') {
        return $.ajax({
            url: this.getApiUrl(xtype),
            type: 'GET',
            data: {
                q: searchTerm
            },
            dataType: 'json'
        });
    }

    /**
     * Populate a regular select element with xcode data
     * @param {string} selector - jQuery selector for the select element
     * @param {string} xtype - The xcode type
     * @param {string} selectedValue - Optional pre-selected value
     */
    populateSelect(selector, xtype, selectedValue = '') {
        const $select = $(selector);
        
        // Show loading state
        $select.html('<option>Loading...</option>').prop('disabled', true);
        
        this.fetchData(xtype)
            .done(function(data) {
                $select.empty();
                
                // Add default option
                $select.append('<option value="">Select ' + xtype.replace('-', ' ') + '...</option>');
                
                // Add data options
                $.each(data.results, function(index, item) {
                    const isSelected = item.id === selectedValue ? 'selected' : '';
                    $select.append(`<option value="${item.id}" ${isSelected}>${item.text}</option>`);
                });
                
                $select.prop('disabled', false);
            })
            .fail(function(xhr, status, error) {
                console.error(`Error loading ${xtype} data:`, error);
                $select.html('<option>Error loading data</option>');
            });
    }

    /**
     * Initialize multiple Select2 dropdowns at once
     * @param {Array} configs - Array of configuration objects
     * Each config should have: {selector, xtype, options}
     */
    initMultipleSelect2(configs) {
        configs.forEach(config => {
            this.initSelect2(config.selector, config.xtype, config.options || {});
        });
    }
}

// Create global instance
window.xcodeAPI = new XCodeAPI();

// jQuery plugin for easy initialization
$.fn.xcodeSelect2 = function(xtype, options = {}) {
    return this.each(function() {
        window.xcodeAPI.initSelect2(this, xtype, options);
    });
};

// Usage Examples:
/*
// Initialize Select2 for brands
$('#brand-select').xcodeSelect2('brands');

// Initialize Select2 with custom options
$('#unit-select').xcodeSelect2('units', {
    placeholder: 'Choose a unit...',
    allowClear: false
});

// Initialize multiple dropdowns
xcodeAPI.initMultipleSelect2([
    {selector: '#brand-select', xtype: 'brands'},
    {selector: '#color-select', xtype: 'color'},
    {selector: '#material-select', xtype: 'material'}
]);

// Populate regular select
xcodeAPI.populateSelect('#country-select', 'country', 'USA');

// Fetch data programmatically
xcodeAPI.fetchData('brands', 'nike').done(function(data) {
    console.log('Brand data:', data.results);
});
*/