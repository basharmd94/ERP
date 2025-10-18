/**
 * Edit Sales JavaScript Module
 * Handles form interactions, AJAX updates, and validation for sales editing
 */

$(document).ready(function() {
    // Initialize the edit sales functionality
    initializeEditSales();
});

function initializeEditSales() {
    // Setup event handlers
    setupFormHandlers();
    setupItemHandlers();
    setupPaymentHandlers();
    setupValidation();
    
    // Initialize UI components
    initializeSelect2();
    initializeProductSearch();
    initializeDatePicker();
    
    console.log('Edit Sales module initialized');
}

/**
 * Setup form event handlers
 */
function setupFormHandlers() {
    // Save changes button handlers
    $('#save-changes-btn, #save-changes-btn-bottom').on('click', function() {
        saveChanges();
    });
    
    // Delete transaction handler
    $('#delete-transaction-btn').on('click', function() {
        showDeleteConfirmation();
    });
    
    // Confirm delete handler
    $('#confirm-delete-btn').on('click', function() {
        deleteTransaction();
    });
    
    // Form field change handlers
    $('#edit-sales-form input, #edit-sales-form select').on('change', function() {
        markFormAsDirty();
    });
}

/**
 * Setup item management handlers
 */
function setupItemHandlers() {
    // Quantity and rate change handlers for automatic calculation
    $(document).on('input', '.quantity-input, .rate-input', function() {
        calculateItemAmount($(this).closest('tr'));
        calculateTotals();
    });
    
    // Add event listeners for tax changes
    $(document).on('input', 'input[name="item_tax"]', function() {
        calculateTotals();
    });
    
    // Item input change handlers
    $(document).on('change', '.item-input', function() {
        markFormAsDirty();
    });
}

/**
 * Setup payment method handlers with POS-style logic
 */
function setupPaymentHandlers() {
    // Payment method change handler
    $('#payment-method-select').on('change', function() {
        window.selectedPaymentMethod = $(this).val();
        togglePaymentFields();
        updatePaymentCalculations();
    });
    
    // Card amount change handler
    $('#card-amount').on('input', function() {
        updatePaymentCalculations();
        validateCardAmount();
    });
    
    // Pay amount change handler
    $('#pay-amount').on('input', function() {
        updateReturnAmount();
        validatePayAmount();
    });
    
    // Bank name validation
    $('#bank-name').on('change', function() {
        validateBankName();
    });
    
    // Card number validation
    $('#card-number').on('input', function() {
        validateCardNumber();
    });
    
    // Initialize payment method
    window.selectedPaymentMethod = $('#payment-method-select').val() || 'cash';
    togglePaymentFields();
}

/**
 * Setup form validation
 */
function setupValidation() {
    // Real-time validation for required fields
    $('#customer-code, #customer-name').on('blur', function() {
        validateRequiredField($(this));
    });
    
    // Card number validation
    $('#card-number').on('input', function() {
        validateCardNumber($(this));
    });
    
    // Numeric field validation
    $('.item-input[type="number"], #card-amount').on('input', function() {
        validateNumericField($(this));
    });
}

/**
 * Initialize Select2 components
 */
function initializeSelect2() {
    // Initialize select2 with the same approach as ecommerce implementation
    var select2 = $('.select2');
    if (select2.length) {
        select2.each(function () {
            var $this = $(this);
            $this.wrap('<div class="position-relative"></div>').select2({
                dropdownParent: $this.parent(),
                placeholder: $this.data('placeholder') || 'Select an option',
                allowClear: true
            });
        });
    }
}

/**
 * Initialize Bootstrap Datepicker
 */
function initializeDatePicker() {
    // Initialize Bootstrap Datepicker with YYYY-MM-DD format
    $('#transaction-date').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true,
        orientation: 'bottom auto'
    });
}

/**
 * Initialize product search functionality
 */
function initializeProductSearch() {
    // Initialize product search using the POS Products API
    if (typeof window.PosProductsAPI !== 'undefined') {
        window.PosProductsAPI.initializeProductSearch('#product-search', addProductToTable);
        
        // Initialize barcode scanner
        $('#barcode-input').on('keypress', function(e) {
            if (e.which === 13) { // Enter key
                const barcode = $(this).val().trim();
                if (barcode) {
                    window.PosProductsAPI.searchByBarcode(barcode, addProductToTable);
                    $(this).val(''); // Clear input
                }
            }
        });
        
        console.log('Product search initialized for edit sales');
    } else {
        console.error('PosProductsAPI module not loaded');
    }
}

/**
 * Add product to the items table
 */
function addProductToTable(product) {
    if (!product || !product.xitem) {
        toastr.error('Invalid product selected');
        return;
    }
    
    // Check if product has zero stock
    if (product.stock <= 0) {
        toastr.error(`${product.xdesc} is out of stock and cannot be added to cart`);
        return;
    }
    
    // Check if product already exists in the table
    const existingRow = $(`#items-tbody tr`).filter(function() {
        return $(this).find('input[name="item_code"]').val() === product.xitem;
    });
    
    if (existingRow.length > 0) {
        // Update quantity if product already exists
        const qtyInput = existingRow.find('input[name="item_qty"]');
        const currentQty = parseFloat(qtyInput.val()) || 0;
        const newQty = currentQty + 1;
        
        // Check stock availability
        if (newQty > product.stock) {
            toastr.warning(`Cannot add more ${product.xdesc}. Only ${product.stock} items available in stock`);
            return;
        }
        
        qtyInput.val(newQty);
        calculateItemAmount(existingRow);
        calculateTotals();
        toastr.success(`Updated quantity for ${product.xdesc}`);
    } else {
        // Add new row
        addNewItemRow(product);
        toastr.success(`${product.xdesc} added to order`);
    }
    
    // Clear the search
    $('#product-search').val(null).trigger('change');
}

/**
 * Toggle payment fields based on payment method
 */
function togglePaymentFields() {
    const paymentMethod = window.selectedPaymentMethod || 'cash';
    const isCardPayment = paymentMethod === 'card';
    
    // Show/hide card-specific fields
    $('#bank-name-section, #card-number-section').toggle(isCardPayment);
    
    // Update card amount section visibility and label
    if (isCardPayment) {
        $('#card-amount-section').show();
        $('#card-amount-section label').html('Card Amount <span class="text-danger">*</span>');
    } else {
        $('#card-amount-section').show();
        $('#card-amount-section label').text('Total Amount');
        $('#cash-amount').text('0.00');
    }
    
    // Clear card-specific fields when not card payment
    if (!isCardPayment) {
        $('#bank-name').val('');
        $('#card-number').val('');
        $('#card-amount').val('0');
        $('#return-amount-section').hide();
    }
    
    // Update pay amount based on payment method
     updatePaymentCalculations();
}

/**
 * Update payment calculations based on payment method
 */
function updatePaymentCalculations() {
    const total = getCurrentTotal();
    const paymentMethod = window.selectedPaymentMethod || 'cash';
    
    if (paymentMethod === 'card') {
        updateCardAmount(total);
    } else {
        updatePayAmount(total);
    }
}

/**
 * Update card amount and cash portion for card payments
 */
function updateCardAmount(total) {
    const currentCardAmount = parseFloat($('#card-amount').val()) || 0;
    
    if (currentCardAmount === 0 || currentCardAmount > total) {
        $('#card-amount').val(total.toFixed(2));
        $('#cash-amount').text('0.00');
        $('#pay-amount').val('0.00');
    } else {
        const cashAmount = Math.max(0, total - currentCardAmount);
        $('#cash-amount').text(cashAmount.toFixed(2));
        $('#pay-amount').val(cashAmount.toFixed(2));
    }
    updateReturnAmount();
}

/**
 * Update pay amount for cash payments
 */
function updatePayAmount(total) {
    if (window.selectedPaymentMethod === 'cash') {
        $('#pay-amount').val(total.toFixed(2));
        $('#card-amount').val('0');
    }
    updateReturnAmount();
}

/**
 * Calculate and display return amount
 */
function updateReturnAmount() {
    const total = getCurrentTotal();
    const payAmount = parseFloat($('#pay-amount').val()) || 0;
    let returnAmount = 0;
    
    if (window.selectedPaymentMethod === 'card') {
        const cardAmount = parseFloat($('#card-amount').val()) || 0;
        const cashPortionNeeded = Math.max(0, total - cardAmount);
        returnAmount = Math.max(0, payAmount - cashPortionNeeded);
    } else {
        returnAmount = Math.max(0, payAmount - total);
    }
    
    if (returnAmount > 0) {
        $('#return-amount-section').show();
        $('#return-amount').text(`৳${returnAmount.toFixed(2)}`);
    } else {
        $('#return-amount-section').hide();
    }
}

/**
  * Get current total amount from the display
  */
 function getCurrentTotal() {
     const totalText = $('#display-total-amount').text().replace('৳', '').replace(',', '');
     return parseFloat(totalText) || 0;
 }

/**
 * POS-style validation functions
 */

/**
 * Validate card amount
 */
function validateCardAmount() {
    const cardAmount = parseFloat($('#card-amount').val()) || 0;
    const total = getCurrentTotal();
    const $field = $('#card-amount');
    
    // Clear previous validation
    clearFieldValidation($field);
    
    if (window.selectedPaymentMethod === 'card') {
        if (cardAmount < 0) {
            showFieldError($field, 'Card amount cannot be negative');
            return false;
        }
        
        if (cardAmount > total) {
            showFieldError($field, 'Card amount cannot exceed total amount');
            return false;
        }
        
        if (cardAmount === 0) {
            showFieldError($field, 'Card amount is required for card payment');
            return false;
        }
    }
    
    return true;
}

/**
 * Validate pay amount
 */
function validatePayAmount() {
    const payAmount = parseFloat($('#pay-amount').val()) || 0;
    const total = getCurrentTotal();
    const $field = $('#pay-amount');
    
    // Clear previous validation
    clearFieldValidation($field);
    
    if (payAmount < 0) {
        showFieldError($field, 'Pay amount cannot be negative');
        return false;
    }
    
    if (window.selectedPaymentMethod === 'cash' && payAmount < total) {
        showFieldError($field, `Cash payment must be at least ৳${total.toFixed(2)}`);
        return false;
    }
    
    return true;
}

/**
 * Validate bank name for card payments
 */
function validateBankName() {
    const bankName = $('#bank-name').val();
    const $field = $('#bank-name');
    
    // Clear previous validation
    clearFieldValidation($field);
    
    if (window.selectedPaymentMethod === 'card') {
        if (!bankName || bankName.trim() === '' || bankName === '-- Select a bank --') {
            showFieldError($field, 'Please select a bank for card payment');
            return false;
        }
    }
    
    return true;
}

/**
 * Validate card number
 */
function validateCardNumber() {
    const cardNumber = $('#card-number').val();
    const $field = $('#card-number');
    
    // Clear previous validation
    clearFieldValidation($field);
    
    if (window.selectedPaymentMethod === 'card') {
        if (!cardNumber || cardNumber.trim().length === 0) {
            showFieldError($field, 'Card number is required for card payment');
            return false;
        }
        
        // Clean card number (remove spaces, dashes)
        const cleanCard = cardNumber.replace(/[\s\-]/g, '');
        
        if (!/^\d{4}$/.test(cleanCard)) {
            showFieldError($field, 'Card number must be 4 digits');
            return false;
        }
    }
    
    return true;
}

/**
 * Show field validation error
 */
function showFieldError($field, message) {
    $field.addClass('is-invalid');
    
    // Remove existing error message
    $field.siblings('.validation-error').remove();
    
    // Add new error message
    $field.after(`<div class="validation-error text-danger small mt-1">${message}</div>`);
}

/**
 * Clear field validation
 */
function clearFieldValidation($field) {
    $field.removeClass('is-invalid');
    $field.siblings('.validation-error').remove();
}

/**
 * Validate all payment fields
 */
function validatePaymentFields() {
    let isValid = true;
    
    if (window.selectedPaymentMethod === 'card') {
        isValid = validateCardAmount() && isValid;
        isValid = validateCardNumber() && isValid;
        isValid = validateBankName() && isValid;
    }
    
    isValid = validatePayAmount() && isValid;
    
    return isValid;
}

/**
 * Convert payment method to payment type format
 */
function getPaymentTypeFromMethod(method) {
    switch(method) {
        case 'cash': return 'Cash Sale';
        case 'card': return 'Card Sale';
        case 'credit': return 'Credit Sale';
        default: return 'Cash Sale';
    }
}



/**
 * Add new item row with product data
 */
function addNewItemRow(product) {
    const tbody = $('#items-tbody');
    const rowCount = tbody.find('tr').length + 1;
    
    // Calculate VAT (7.5% as per POS config)
    const VAT_PERCENTAGE = 7.5;
    const itemTotal = product.xstdprice;
    const itemVat = (itemTotal * VAT_PERCENTAGE / 100).toFixed(2);
    
    const newRow = `
         <tr data-row="${rowCount}">
             <td>${rowCount}</td>
             <td>
                 <input type="text" class="form-control form-control-sm item-input" name="item_code" 
                        data-field="xitem" value="${product.xitem}" readonly>
             </td>
             <td>
                 <input type="text" class="form-control form-control-sm item-input" name="item_desc" 
                        data-field="xdesc" value="${product.xdesc}" readonly>
             </td>
             <td>
                 <input type="text" class="form-control form-control-sm item-input" name="item_unit" 
                        data-field="xunitsel" value="${product.xunitstk}" readonly>
             </td>
             <td>
                 <input type="number" class="form-control form-control-sm quantity-input item-input" name="item_qty" 
                        data-field="xqtyord" step="0.001" min="0" value="1" max="${product.stock}">
             </td>
             <td>
                 <input type="number" class="form-control form-control-sm rate-input item-input" name="item_rate" 
                        data-field="xrate" step="0.01" min="0" value="${product.xstdprice}">
             </td>
             <td>
                 <input type="number" class="form-control form-control-sm amount-input item-input" name="item_amount" 
                        data-field="xlineamt" step="0.01" readonly value="${itemTotal}">
             </td>
             <td>
                 <input type="number" class="form-control form-control-sm item-input" name="item_tax" 
                        data-field="xdttax" step="0.01" min="0" value="${itemVat}">
             </td>
             <td>
                 <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeItem(this)">
                     <i class="ti ti-trash"></i>
                 </button>
             </td>
         </tr>
     `;
    
    tbody.append(newRow);
    calculateTotals();
    markFormAsDirty();
}

/**
 * Remove item row from table
 */
function removeItem(button) {
    const row = $(button).closest('tr');
    
    if ($('#items-tbody tr').length <= 1) {
        toastr.warning('At least one item is required');
        return;
    }
    
    row.remove();
    renumberRows();
    calculateTotals();
    markFormAsDirty();
}

/**
 * Renumber table rows after deletion
 */
function renumberRows() {
    $('#items-tbody tr').each(function(index) {
        const rowNumber = index + 1;
        $(this).attr('data-row', rowNumber);
        $(this).find('td:first').text(rowNumber);
    });
}

/**
 * Calculate amount for a specific item row
 */
function calculateItemAmount(row) {
    const quantity = parseFloat(row.find('.quantity-input').val()) || 0;
    const rate = parseFloat(row.find('.rate-input').val()) || 0;
    const amount = quantity * rate;
    
    row.find('.amount-input').val(amount.toFixed(2));
}

/**
 * Update summary display
 */
function updateSummaryDisplay(subtotal, totalTax) {
    // This function is kept for compatibility but the main calculation
    // is now handled by the calculateTotals function at the end of the file
}

/**
 * Validate required field
 */
function validateRequiredField(field) {
    const value = field.val().trim();
    
    if (!value) {
        field.addClass('is-invalid');
        showFieldError(field, 'This field is required');
        return false;
    } else {
        field.removeClass('is-invalid');
        hideFieldError(field);
        return true;
    }
}

/**
 * Validate card number
 */
function validateCardNumber(field) {
    const value = field.val().trim();
    
    if ($('#payment-type').val() === 'Card Sale' && !value) {
        field.addClass('is-invalid');
        showFieldError(field, 'Card number is required for card sales');
        return false;
    } else {
        field.removeClass('is-invalid');
        hideFieldError(field);
        return true;
    }
}

/**
 * Validate numeric field
 */
function validateNumericField(field) {
    const value = parseFloat(field.val());
    
    if (isNaN(value) || value < 0) {
        field.addClass('is-invalid');
        showFieldError(field, 'Please enter a valid positive number');
        return false;
    } else {
        field.removeClass('is-invalid');
        hideFieldError(field);
        return true;
    }
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    let errorDiv = field.next('.invalid-feedback');
    if (errorDiv.length === 0) {
        errorDiv = $('<div class="invalid-feedback"></div>');
        field.after(errorDiv);
    }
    errorDiv.text(message);
}

/**
 * Hide field error
 */
function hideFieldError(field) {
    field.next('.invalid-feedback').remove();
}

/**
 * Validate entire form
 */
function validateForm() {
    let isValid = true;
    
    // Validate required fields
    const requiredFields = ['#customer-code', '#customer-name'];
    requiredFields.forEach(selector => {
        if (!validateRequiredField($(selector))) {
            isValid = false;
        }
    });
    
    // Validate payment fields using POS validation
    if (!validatePaymentFields()) {
        isValid = false;
    }
    
    // Validate items
    if ($('#items-tbody tr').length === 0) {
        toastr.error('At least one item is required');
        isValid = false;
    }
    
    // Validate item quantities and rates
    $('#items-tbody tr').each(function() {
        const qty = parseFloat($(this).find('.quantity-input').val());
        const rate = parseFloat($(this).find('.rate-input').val());
        
        if (isNaN(qty) || qty <= 0) {
            $(this).find('.quantity-input').addClass('is-invalid');
            isValid = false;
        }
        
        if (isNaN(rate) || rate < 0) {
            $(this).find('.rate-input').addClass('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Collect form data
 */
function collectFormData() {
    const formData = {
        transaction_id: $('#transaction-id').val(),
        header: {
            xdate: $('#transaction-date').val(),
            xcus: $('#customer-code').val(),
            customer_name: $('#customer-name').val(),
            xwh: $('#warehouse').val(),
            xsp: $('#salesman').val(),
            xmobile: $('#customer-mobile').val(),
            xstatusord: $('#transaction-status').val(),
            xsltype: getPaymentTypeFromMethod($('#payment-method-select').val()),
            xsalescat: $('#bank-name').val(),
            xdocnum: $('#card-number').val(),
            xdtcomm: parseFloat($('#card-amount').val()) || 0
        },
        items: []
    };
    
    // Collect items data
    $('#items-tbody tr').each(function() {
        const row = $(this);
        const item = {
            xrow: row.attr('data-row'),
            xitem: row.find('input[data-field="xitem"]').val(),
            xdesc: row.find('input[data-field="xdesc"]').val(),
            xunitsel: row.find('input[data-field="xunitsel"]').val(),
            xqtyord: parseFloat(row.find('input[data-field="xqtyord"]').val()) || 0,
            xrate: parseFloat(row.find('input[data-field="xrate"]').val()) || 0,
            xlineamt: parseFloat(row.find('input[data-field="xlineamt"]').val()) || 0,
            xdttax: parseFloat(row.find('input[data-field="xdttax"]').val()) || 0
        };
        formData.items.push(item);
    });
    
    return formData;
}

/**
 * Save changes to the transaction
 */
function saveChanges() {
    if (!validateForm()) {
        toastr.error('Please fix the validation errors before saving');
        return;
    }
    
    const formData = collectFormData();
    
    // Show loading state
    const saveBtn = $('#save-changes-btn, #save-changes-btn-bottom');
    const originalText = saveBtn.html();
    saveBtn.prop('disabled', true).html('<i class="ti ti-loader ti-spin me-1"></i> Saving...');
    
    $.ajax({
        url: '/sales/api/update-transaction/',
        type: 'POST',
        data: JSON.stringify(formData),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                toastr.success('Transaction updated successfully');
                markFormAsClean();
                
                // Optionally redirect or refresh data
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                toastr.error(response.message || 'Failed to update transaction');
            }
        },
        error: function(xhr, status, error) {
            console.error('Save error:', error);
            toastr.error('An error occurred while saving. Please try again.');
        },
        complete: function() {
            // Restore button state
            saveBtn.prop('disabled', false).html(originalText);
        }
    });
}

/**
 * Show delete confirmation modal
 */
function showDeleteConfirmation() {
    $('#deleteConfirmModal').modal('show');
}

/**
 * Delete transaction
 */
function deleteTransaction() {
    const transactionId = $('#transaction-id').val();
    
    $.ajax({
        url: '/sales/api/delete-transaction/',
        type: 'POST',
        data: {
            transaction_id: transactionId,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                toastr.success('Transaction deleted successfully');
                $('#deleteConfirmModal').modal('hide');
                
                // Redirect to sales list
                setTimeout(() => {
                    window.location.href = '/sales/sales-list/';
                }, 1500);
            } else {
                toastr.error(response.message || 'Failed to delete transaction');
            }
        },
        error: function(xhr, status, error) {
            console.error('Delete error:', error);
            toastr.error('An error occurred while deleting. Please try again.');
        }
    });
}

/**
 * Mark form as dirty (has unsaved changes)
 */
function markFormAsDirty() {
    window.formIsDirty = true;
}

/**
 * Mark form as clean (no unsaved changes)
 */
function markFormAsClean() {
    window.formIsDirty = false;
}

/**
 * Warn user about unsaved changes
 */
$(window).on('beforeunload', function(e) {
    if (window.formIsDirty) {
        const message = 'You have unsaved changes. Are you sure you want to leave?';
        e.returnValue = message;
        return message;
    }
});

/**
 * Utility function to format currency
 */
function formatCurrency(amount) {
    return '৳' + parseFloat(amount).toFixed(2);
}

/**
 * Utility function to show loading overlay
 */
function showLoading() {
    if ($('#loading-overlay').length === 0) {
        $('body').append(`
            <div id="loading-overlay" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            ">
                <div style="
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <i class="ti ti-loader ti-spin" style="font-size: 24px;"></i>
                    <div style="margin-top: 10px;">Processing...</div>
                </div>
            </div>
        `);
    }
}

/**
 * Utility function to hide loading overlay
 */
function hideLoading() {
    $('#loading-overlay').remove();
}

/**
 * Remove item from table
 */
function removeItem(button) {
    const row = $(button).closest('tr');
    
    if ($('#items-tbody tr').length <= 1) {
        toastr.warning('At least one item is required');
        return;
    }
    
    row.remove();
    renumberRows();
    calculateTotals();
    markFormAsDirty();
    
    toastr.info('Item removed from order');
}

/**
 * Renumber table rows
 */
function renumberRows() {
    $('#items-tbody tr').each(function(index) {
        $(this).find('td:first').text(index + 1);
        $(this).attr('data-row', index + 1);
    });
}

/**
 * Calculate totals for all items
 */
function calculateTotals() {
    let subtotal = 0;
    let totalTax = 0;
    
    $('#items-tbody tr').each(function() {
        const amount = parseFloat($(this).find('.amount-input').val()) || 0;
        const tax = parseFloat($(this).find('input[name="item_tax"]').val()) || 0;
        
        subtotal += amount;
        totalTax += tax;
    });
    
    // Get current discount percentage (default to 0 for now)
    const discountPercent = parseFloat($('#xdiscountper').val()) || 0;
    const discountAmount = (subtotal * discountPercent) / 100;
    const total = subtotal - discountAmount + totalTax;
    
    // Update hidden input fields
    $('#xdiscountamt').val(discountAmount.toFixed(2));
    $('#xtotamt').val(total.toFixed(2));
    $('#xdttax').val(totalTax.toFixed(2));
    
    // Update display elements
    $('#display-discount-percent').text(discountPercent.toFixed(1) + '%');
    $('#display-discount-amount').text('৳' + discountAmount.toFixed(2));
    $('#display-tax-amount').text('৳' + totalTax.toFixed(2));
    $('#display-total-amount').text('৳' + total.toFixed(2));
    
    // Update payment calculations when totals change
    updatePaymentCalculations();
    
    // Mark form as dirty when totals change
    markFormAsDirty();
}