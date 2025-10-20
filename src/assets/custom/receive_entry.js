/**
 * Receive Entry Form JavaScript
 */

// Global variables for line items management
let searchTimeout;
let lineItems = [];
let serialCounter = 1;

// Update total value function (global scope)
function updateTotalValue() {
    const total = lineItems.reduce((sum, item) => sum + item.value, 0);
    $('#total-value').text(`৳${total.toFixed(2)}`);
}

// Helper function to get cookie value
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

$(function () {
    'use strict';

    console.log("=== RECEIVE ENTRY INITIALIZATION ===");
    console.log("Receive Entry Form loaded");
    console.log("jQuery version:", $.fn.jquery);
    console.log("Document ready state:", document.readyState);
    console.log("Select2 available:", typeof $.fn.select2 !== 'undefined');
    
    // Setup AJAX defaults to include credentials
    $.ajaxSetup({
        xhrFields: {
            withCredentials: true
        },
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", $('[name=csrfmiddlewaretoken]').val() || getCookie('csrftoken'));
            }
        }
    });

    // Initialize Select2 dropdowns
    $('.select2').select2({
        placeholder: 'Select an option',
        allowClear: true
    });

    // Initialize Bootstrap Date Pickers following item_ledger.js pattern
    $('#transaction-date, #invoice-date').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true,
        clearBtn: true,
        orientation: 'bottom auto',
        container: 'body'
    });

    // Set today's date as default for both date pickers
    var today = new Date();
    var todayFormatted = today.getFullYear() + '-' + 
                        (today.getMonth() + 1).toString().padStart(2, '0') + '-' + 
                        today.getDate().toString().padStart(2, '0');
    
    $('#transaction-date, #invoice-date').datepicker('setDate', today);

    // Form submission handler
    $('#receive-entry-form').on('submit', function(e) {
        e.preventDefault();

        // Validate required fields
        var receiveType = $('#receive-type').val();
        var warehouse = $('#warehouse').val();

        if (!receiveType) {
            alert('Please select a Receive Type');
            return false;
        }

        if (!warehouse) {
            alert('Please select a Warehouse');
            return false;
        }

        // Here you can add AJAX call to submit the form
        console.log('Form submitted successfully');
        
        // Clear localStorage after successful submission
        localStorage.removeItem(STORAGE_KEY);
        
        alert('Receive Entry saved successfully!');
    });

    // Reset form handler
    $('#receive-entry-form').on('reset', function() {
        setTimeout(function() {
            $('.select2').trigger('change');
            $('#transaction-date, #invoice-date').datepicker('setDate', today);
            // Clear line items
            clearLineItems();
        }, 100);
    });

    // Smart Item Selector functionality

    // LocalStorage key for persisting line items
    const STORAGE_KEY = 'receive_entry_line_items';

    // Load line items from localStorage
    function loadLineItemsFromStorage() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                const data = JSON.parse(stored);
                lineItems = data.items || [];
                serialCounter = data.serialCounter || 1;
                
                // Restore table from stored data
                if (lineItems.length > 0) {
                    restoreLineItemsTable();
                }
            }
        } catch (error) {
            console.error('Error loading line items from storage:', error);
            lineItems = [];
            serialCounter = 1;
        }
    }

    // Save line items to localStorage
    function saveLineItemsToStorage() {
        try {
            const data = {
                items: lineItems,
                serialCounter: serialCounter
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving line items to storage:', error);
        }
    }

    // Restore line items table from stored data
    function restoreLineItemsTable() {
        $('#no-items-row').remove();
        $('#line-items-tbody').empty();
        
        lineItems.forEach((item, index) => {
            addLineItemRow(item, index);
        });
        
        updateTotalValue();
    }

    // Initialize line items from storage on page load
    loadLineItemsFromStorage();

    // Product search functionality will be implemented here

    // Product selection functionality will be implemented here



    // Add item to line items table
    function addItemToTable(item) {
        // Check if item already exists
        const existingIndex = lineItems.findIndex(lineItem => lineItem.xitem === item.xitem);
        
        if (existingIndex !== -1) {
            // Increment quantity if item exists
            lineItems[existingIndex].qty += 1;
            updateLineItemRow(existingIndex);
            
            // Save to localStorage
            saveLineItemsToStorage();
            
            // Show feedback for existing item
            showItemFeedback(`Updated quantity for ${item.xitem}`, 'info');
            
            // Highlight the updated row
            const row = $(`tr[data-index="${existingIndex}"]`);
            row.addClass('table-warning');
            setTimeout(() => row.removeClass('table-warning'), 1500);
        } else {
            // Add new item
            const newItem = {
                sl: serialCounter++,
                xitem: item.xitem,
                xdesc: item.xdesc,
                rate: parseFloat(item.xstdprice || item.price || 0),
                qty: 1,
                value: parseFloat(item.xstdprice || item.price || 0) * 1
            };
            lineItems.push(newItem);
            addLineItemRow(newItem, lineItems.length - 1);
            
            // Save to localStorage
            saveLineItemsToStorage();
            
            // Show feedback for new item
            showItemFeedback(`Added ${item.xitem} to cart`, 'success');
        }

        updateTotalValue();
    }

    // Show item feedback
    function showItemFeedback(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'info' ? 'alert-info' : 'alert-primary';
        
        const feedback = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <i class="tf-icons ti ti-check me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(feedback);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            feedback.alert('close');
        }, 3000);
    }

    // Add line item row to table
    function addLineItemRow(item, index) {
        // Remove "no items" row if it exists
        $('#no-items-row').remove();

        const row = $(`
            <tr data-index="${index}">
                <td class="text-center">${item.sl}</td>
                <td><strong>${item.xitem}</strong></td>
                <td>${item.xdesc}</td>
                <td>
                    <input type="number" class="form-control form-control-sm rate-input" 
                           value="${item.rate}" min="0" step="0.01" data-index="${index}" readonly>
                </td>
                <td>
                    <input type="number" class="form-control form-control-sm qty-input" 
                           value="${item.qty}" min="1" step="1" data-index="${index}">
                </td>
                <td class="text-end value-cell">৳${item.value.toFixed(2)}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger delete-item" data-index="${index}">
                        <i class="tf-icons ti ti-trash"></i>
                    </button>
                </td>
            </tr>
        `);

        $('#line-items-tbody').append(row);
    }

    // Update existing line item row
    function updateLineItemRow(index) {
        const item = lineItems[index];
        const row = $(`tr[data-index="${index}"]`);
        
        row.find('.qty-input').val(item.qty);
        row.find('.value-cell').text(`৳${item.value.toFixed(2)}`);
    }





    // Clear all line items
    function clearLineItems() {
        lineItems = [];
        serialCounter = 1;
        $('#line-items-tbody').html(`
            <tr id="no-items-row">
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="tf-icons ti ti-package-off ti-lg mb-2 d-block"></i>
                    No items added yet. Use the item selector above to add items.
                </td>
            </tr>
        `);
        updateTotalValue();
        
        // Clear localStorage
        localStorage.removeItem(STORAGE_KEY);
    }



    // Handle quantity changes
    $(document).on('input', '.qty-input', function() {
        const index = $(this).data('index');
        const item = lineItems[index];
        
        item.qty = parseFloat($(this).val()) || 1;
        item.value = item.qty * item.rate;
        updateLineItemRow(index);
        updateTotalValue();
        
        // Save to localStorage
        saveLineItemsToStorage();
    });

    // Handle item deletion
    $(document).on('click', '.delete-item', function() {
        const index = $(this).data('index');
        
        // Remove from array
        lineItems.splice(index, 1);
        
        // Remove row
        $(this).closest('tr').remove();
        
        // Update indices and serial numbers
        $('#line-items-tbody tr').each(function(i) {
            if (!$(this).attr('id')) { // Skip "no-items-row"
                $(this).attr('data-index', i);
                $(this).find('.qty-input, .rate-input, .delete-item').attr('data-index', i);
                $(this).find('td:first').text(i + 1);
                if (lineItems[i]) {
                    lineItems[i].sl = i + 1;
                }
            }
        });
        
        // Show "no items" row if table is empty
        if (lineItems.length === 0) {
            $('#line-items-tbody').html(`
                <tr id="no-items-row">
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="tf-icons ti ti-package-off ti-lg mb-2 d-block"></i>
                        No items added yet. Use the item selector above to add items.
                    </td>
                </tr>
            `);
            serialCounter = 1;
        }
        
        updateTotalValue();
        
        // Save to localStorage
        saveLineItemsToStorage();
    });

    // Handle form submission
    $('#receive-entry-form').on('submit', function(e) {
        e.preventDefault();
        saveReceiveEntry();
    });
});

/**
 * Save receive entry data via AJAX
 */
function saveReceiveEntry() {
    // Validate line items
    if (lineItems.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'No Items',
            text: 'Please add at least one item before saving.',
            confirmButtonText: 'OK'
        });
        return;
    }

    // Show loading state
    const saveBtn = $('button[type="submit"]');
    const originalBtnText = saveBtn.html();
    saveBtn.prop('disabled', true).html('<i class="tf-icons ti ti-loader-2 me-1 spin"></i>Saving...');

    // Add CSS for spinner animation if not already present
    if (!$('#spinner-style').length) {
        $('<style id="spinner-style">.spin { animation: spin 1s linear infinite; }</style>').appendTo('head');
    }

    // Collect form data
    const formData = new FormData();
    
    // Add CSRF token
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    
    // Add form fields
    formData.append('xdate', $('#transaction-date').val());
    formData.append('xinvdate', $('#invoice-date').val());
    formData.append('xtype', $('#receive-type option:selected').text()); // Send display text
    formData.append('xref', $('#reference').val());
    formData.append('xsupplier', $('#supplier-number').val());
    formData.append('xwh', $('#warehouse option:selected').text()); // Send display text
    formData.append('xnote', $('#notes').val());
    formData.append('xprefix', $('#transaction-prefix').val());
    formData.append('xenteredby', $('#entered-by').val());
    
    // Add line items as JSON
    formData.append('line_items', JSON.stringify(lineItems));
    
    // Add total value
    formData.append('total_value', $('#total-value').text().replace('৳', '').replace(',', ''));

    // Make AJAX request
    $.ajax({
        url: '/inventory/api/save_receive_entry/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log('Save response:', response);
            
            if (response.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: `Receive entry saved successfully. Voucher Number: ${response.voucher_number}`,
                    confirmButtonText: 'OK'
                }).then(() => {
                    // Clear form and line items
                    clearForm();
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: response.error || 'Failed to save receive entry',
                    confirmButtonText: 'OK'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Save error:', xhr.responseText);
            
            let errorMessage = 'Failed to save receive entry';
            try {
                const response = JSON.parse(xhr.responseText);
                errorMessage = response.error || errorMessage;
            } catch (e) {
                errorMessage = `Server error: ${xhr.status} ${xhr.statusText}`;
            }
            
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: errorMessage,
                confirmButtonText: 'OK'
            });
        },
        complete: function() {
            // Restore button state
            saveBtn.prop('disabled', false).html(originalBtnText);
        }
    });
}

/**
 * Clear form and reset to initial state
 */
function clearForm() {
    // Clear form fields
    $('#receive-entry-form')[0].reset();
    
    // Clear line items
    lineItems = [];
    serialCounter = 1;
    
    // Reset table
    $('#line-items-tbody').html(`
        <tr id="no-items-row">
            <td colspan="7" class="text-center text-muted py-4">
                <i class="tf-icons ti ti-package-off ti-lg mb-2 d-block"></i>
                No items added yet. Use the item selector above to add items.
            </td>
        </tr>
    `);
    
    // Reset total
    updateTotalValue();
    
    // Clear localStorage
    localStorage.removeItem('receiveEntryLineItems');
    
    // Clear search
    $('#item-search').val('');
    $('#search-results').hide();
}