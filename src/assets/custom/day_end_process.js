/**
 * Day End Process JavaScript Module
 * Handles date picker initialization, form validation, and AJAX submission
 */

$(document).ready(function() {
    initializeDayEndProcess();
});

/**
 * Initialize Day End Process functionality
 */
function initializeDayEndProcess() {
    initializeDatePicker();
    setupFormHandlers();
    setupValidation();

    console.log('Day End Process module initialized');
}

/**
 * Initialize Bootstrap Date Picker
 */
function initializeDatePicker() {
    $('#process-date').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true,
        orientation: 'bottom auto',
        container: 'body',
        endDate: new Date(), // Prevent future dates
        clearBtn: true
    });

    // Set yesterday as default date
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    $('#process-date').datepicker('setDate', yesterday);
}

/**
 * Setup form event handlers
 */
function setupFormHandlers() {
    $('#day-end-form').on('submit', function(e) {
        e.preventDefault();

        // Check if process button is disabled
        if ($('#process-btn').prop('disabled')) {
            toastr.warning('You do not have permission to start the day-end process');
            return;
        }

        if (validateForm()) {
            showConfirmationDialog();
        }
    });

    // Delete button handler
    $('#delete-btn').on('click', function(e) {
        e.preventDefault();

        // Check if delete button is disabled
        if ($(this).prop('disabled')) {
            toastr.warning('You do not have permission to delete the day-end process');
            return;
        }

        if (validateForm()) {
            showDeleteConfirmationDialog();
        }
    });

    // Date validation on change
    $('#process-date').on('change', function() {
        validateDate($(this));
    });
}

/**
 * Setup real-time validation
 */
function setupValidation() {
    $('#process-date').on('blur', function() {
        validateDate($(this));
    });
}

/**
 * Validate the entire form
 */
function validateForm() {
    let isValid = true;

    // Validate date
    if (!validateDate($('#process-date'))) {
        isValid = false;
    }

    return isValid;
}

/**
 * Validate date field
 */
function validateDate(field) {
    const dateValue = field.val().trim();

    if (!dateValue) {
        showFieldError(field, 'Please select a process date');
        return false;
    }

    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateValue)) {
        showFieldError(field, 'Please enter date in YYYY-MM-DD format');
        return false;
    }

    // Validate date is not in future
    const selectedDate = new Date(dateValue);
    const today = new Date();
    today.setHours(23, 59, 59, 999); // End of today

    if (selectedDate > today) {
        showFieldError(field, 'Cannot process future dates');
        return false;
    }

    // Validate date is not too old (more than 1 year)
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

    if (selectedDate < oneYearAgo) {
        showFieldError(field, 'Cannot process dates older than 1 year');
        return false;
    }

    clearFieldError(field);
    return true;
}

/**
 * Show field error message
 */
function showFieldError(field, message) {
    field.addClass('is-invalid');

    let errorDiv = field.closest('.input-group').next('.invalid-feedback');
    if (errorDiv.length === 0) {
        errorDiv = field.next('.invalid-feedback');
        if (errorDiv.length === 0) {
            errorDiv = $('<div class="invalid-feedback"></div>');
            field.closest('.input-group').after(errorDiv);
        }
    }
    errorDiv.text(message);
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.removeClass('is-invalid');
    field.closest('.input-group').next('.invalid-feedback').remove();
    field.next('.invalid-feedback').remove();
}

/**
 * Show confirmation dialog before processing
 */
function showConfirmationDialog() {
    const processDate = $('#process-date').val();

    Swal.fire({
        title: 'Confirm Day End Process',
        html: `
            <div class="text-start">
                <p><strong>Process Date:</strong> ${processDate}</p>
                <hr>
                <p class="text-warning mb-2">
                    <i class="ti ti-alert-triangle me-2"></i>
                    <strong>Important:</strong>
                </p>
                <ul class="text-start text-muted">
                    <li>This will generate permanent accounting entries</li>
                    <li>The process cannot be undone easily</li>
                    <li>Ensure all sales for this date are completed</li>
                    <li>This process can only be run once per date</li>
                </ul>
            </div>
        `,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '<i class="ti ti-check me-2"></i>Yes, Process Day End',
        cancelButtonText: '<i class="ti ti-x me-2"></i>Cancel',
        reverseButtons: true,
        buttonsStyling: false,
        customClass: {
            popup: 'swal-wide',
            confirmButton: 'btn btn-primary me-3',
            cancelButton: 'btn btn-label-secondary'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            submitDayEndProcess();
        }
    });
}

/**
 * Submit day end process via AJAX
 */
function submitDayEndProcess() {
    const formData = {
        xdate: $('#process-date').val(),
        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
    };

    // Show loading state
    showLoadingState();

    $.ajax({
        url: '/sales/create-day-end-process/', // Use the new API endpoint
        type: 'POST',
        data: formData,
        dataType: 'json',
        timeout: 300000, // 5 minutes timeout for long process
        success: function(response) {
            hideLoadingState();

            if (response.success) {
                showSuccessResult(response);

                // Show success toast
                toastr.success(response.message || 'Day end process completed successfully');
            } else {
                showErrorResult(response);

                // Show error toast
                toastr.error(response.message || 'Day end process failed');
            }
        },
        error: function(xhr, status, error) {
            hideLoadingState();

            let errorMessage = 'An error occurred during the day end process';

            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            } else if (status === 'timeout') {
                errorMessage = 'Process timed out. Please check if the process completed successfully.';
            } else if (xhr.status === 500) {
                errorMessage = 'Server error occurred. Please contact system administrator.';
            }

            showErrorResult({ message: errorMessage, details: error });
            toastr.error(errorMessage);
        }
    });
}

/**
 * Show loading state
 */
function showLoadingState() {
    const btn = $('#process-btn');
    btn.prop('disabled', true);
    btn.find('.btn-text').hide();
    $('#loading-spinner').removeClass('d-none');

    // Disable form
    $('#day-end-form input, #day-end-form button').prop('disabled', true);
    btn.prop('disabled', true); // Keep button disabled
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const btn = $('#process-btn');
    btn.prop('disabled', false);
    btn.find('.btn-text').show();
    $('#loading-spinner').addClass('d-none');

    // Re-enable form
    $('#day-end-form input, #day-end-form button').prop('disabled', false);
}

/**
 * Show success result
 */
function showSuccessResult(response) {
    const resultDiv = $('#process-result');
    const contentDiv = $('#result-content');

    // Update alert to success style
    resultDiv.find('.alert').removeClass('alert-primary').addClass('alert-success');
    resultDiv.find('.alert-heading').html('<i class="ti ti-check-circle me-2"></i>Process Completed Successfully');

    let html = `<p class="mb-0">${response.message}</p>`;

    if (response.details) {
        html += `<div class="row mt-3">`;

        if (response.details.sales_voucher) {
            html += `
                <div class="col-md-6">
                    <strong>Sales Voucher:</strong> ${response.details.sales_voucher}<br>
                    <strong>Total Sales:</strong> ৳${formatCurrency(response.details.total_sales)}<br>
                    <strong>Cash Sales:</strong> ৳${formatCurrency(response.details.cash_sales)}<br>
                    <strong>Card Sales:</strong> ৳${formatCurrency(response.details.card_sales)}
                </div>
            `;
        }

        if (response.details.return_voucher) {
            html += `
                <div class="col-md-6">
                    <strong>Return Voucher:</strong> ${response.details.return_voucher}<br>
                    <strong>Return Amount:</strong> ৳${formatCurrency(response.details.return_amount)}
                </div>
            `;
        }

        html += `</div>`;
    }

    contentDiv.html(html);
    resultDiv.removeClass('d-none');

    // Scroll to result
    $('html, body').animate({
        scrollTop: resultDiv.offset().top - 100
    }, 500);
}

/**
 * Show error result
 */
function showErrorResult(response) {
    const resultDiv = $('#process-result');
    const contentDiv = $('#result-content');

    // Update alert to danger style
    resultDiv.find('.alert').removeClass('alert-primary').addClass('alert-danger');
    resultDiv.find('.alert-heading').html('<i class="ti ti-x-circle me-2"></i>Process Failed');

    let html = `<p class="mb-0">${response.message}</p>`;

    if (response.details) {
        html += `
            <hr class="my-3">
            <div class="details-section">
                <h6 class="mb-2">Error Details:</h6>
                <pre class="small text-muted">${response.details}</pre>
            </div>
        `;
    }

    contentDiv.html(html);
    resultDiv.removeClass('d-none');

    // Scroll to result
    $('html, body').animate({
        scrollTop: resultDiv.offset().top - 100
    }, 500);
}

/**
 * Format currency for display
 */
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '0.00';
    return parseFloat(amount).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Show delete confirmation dialog
 */
function showDeleteConfirmationDialog() {
    const processDate = $('#process-date').val();

    Swal.fire({
        title: 'Delete Day End Process',
        html: `
            <div class="text-start">
                <p><strong>Process Date:</strong> ${processDate}</p>
                <hr>
                <p class="text-danger mb-2">
                    <i class="ti ti-alert-triangle me-2"></i>
                    <strong>Warning:</strong>
                </p>
                <ul class="text-start text-muted">
                    <li>This will permanently delete all accounting entries for this date</li>
                    <li>All GL header and detail records will be removed</li>
                    <li>This action cannot be undone</li>
                    <li>Make sure you have proper backups before proceeding</li>
                </ul>
                <p class="text-danger mt-3">
                    <strong>Are you sure you want to delete the day end process for ${processDate}?</strong>
                </p>
            </div>
        `,
        icon: 'error',
        showCancelButton: true,
        confirmButtonText: '<i class="ti ti-trash me-2"></i>Yes, Delete Process',
        cancelButtonText: '<i class="ti ti-x me-2"></i>Cancel',
        reverseButtons: true,
        buttonsStyling: false,
        customClass: {
            popup: 'swal-wide',
            confirmButton: 'btn btn-danger me-3',
            cancelButton: 'btn btn-label-secondary'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            submitDeleteDayEndProcess();
        }
    });
}

/**
 * Submit delete day end process via AJAX
 */
function submitDeleteDayEndProcess() {
    const processDate = $('#process-date').val();

    // Show loading state
    showLoadingState();

    $.ajax({
        url: `/sales/api/delete-day-end-process/${processDate}/`,
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
             hideLoadingState();

             if (response.success) {
                 // Show success result
                 showSuccessResult(response);

                 // Show success toast
                 toastr.success(response.message || 'Day end process deleted successfully');
             } else {
                 showErrorResult(response);

                 // Show error toast
                 toastr.error(response.message || 'Failed to delete day end process');
             }
         },
        error: function(xhr, status, error) {
            hideLoadingState();

            let errorMessage = 'An error occurred while deleting the day end process';

            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            } else if (xhr.status === 404) {
                errorMessage = 'No day end process found for the selected date';
            } else if (xhr.status === 500) {
                errorMessage = 'Server error occurred. Please try again later';
            }

            // Show error toast
             toastr.error(errorMessage);

            showErrorResult({
                success: false,
                message: errorMessage,
                details: `Status: ${xhr.status}, Error: ${error}`
            });
        }
    });
}

/**
 * Configure toastr notifications
 */
toastr.options = {
    closeButton: true,
    debug: false,
    newestOnTop: true,
    progressBar: true,
    positionClass: 'toast-top-right',
    preventDuplicates: false,
    onclick: null,
    showDuration: '300',
    hideDuration: '1000',
    timeOut: '5000',
    extendedTimeOut: '1000',
    showEasing: 'swing',
    hideEasing: 'linear',
    showMethod: 'fadeIn',
    hideMethod: 'fadeOut'
};
