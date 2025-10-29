/**
 * Sales Return Delete Module
 * Provides delete functionality for sales return transactions
 * Can be used across different modules and pages
 */

$(document).ready(function() {
    /**
     * Delete Sales Return Transaction
     * @param {string} transactionId - The transaction ID to delete
     * @param {string} transactionRef - Optional transaction reference for display
     */
    window.deleteSalesReturn = function(transactionId, transactionRef = '') {
        if (!transactionId) {
            toastr.error('Transaction ID is required for deletion');
            return;
        }

        // Show SweetAlert confirmation dialog with transaction details
        const transactionDisplay = transactionRef || transactionId;
        const title = 'Confirm Deletion';

        const text = `Are you sure you want to delete Sales Return Transaction: <strong>${transactionDisplay}</strong>?<br><br>This action cannot be undone and will remove all related records including GL entries if posted.`;

        Swal.fire({
            title: title,
            html: text, // Using html instead of text to allow formatting
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel',
            focusCancel: true // Focus on cancel button by default for safety
        }).then((result) => {
            if (!result.isConfirmed) {
                return;
            }

            // Proceed with deletion if confirmed
            performDelete(transactionId);
        });
    };

    // Separate function to perform the actual deletion
    function performDelete(transactionId) {

        // Show loading state
        const loadingToast = toastr.info('Deleting sales return transaction...', 'Please wait', {
            timeOut: 0,
            extendedTimeOut: 0,
            closeButton: false,
            tapToDismiss: false
        });

        // Perform AJAX delete request
        $.ajax({
            url: `/sales/api/sales-return-delete/${transactionId}/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() || $('meta[name=csrf-token]').attr('content')
            },
            success: function(response) {
                // Clear loading toast
                toastr.clear(loadingToast);

                if (response.success) {
                    toastr.success(response.message || 'Sales return transaction deleted successfully');


                    // Log deletion details if available
                    if (response.deleted_records) {
                        console.log('Deleted records:', response.deleted_records);
                    }

                    // Redirect or refresh based on current page
                    if (window.location.pathname.includes('sales-return-list')) {
                        // If on list page, reload the page to refresh the list
                        window.location.reload();
                    } else if (window.location.pathname.includes('sales-return-detail')) {
                        // If on detail page, redirect to list page
                        window.location.href = '/sales/sales-return-list/';
                    } else {
                        // Default: redirect to list page
                        window.location.href = '/sales/sales-return-list/';
                    }
                } else {
                    toastr.error(response.message || 'Failed to delete sales return transaction');
                }
            },
            error: function(xhr, status, error) {
                // Clear loading toast
                toastr.clear(loadingToast);

                let errorMessage = 'Error deleting sales return transaction';

                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                } else if (xhr.status === 404) {
                    errorMessage = 'Sales return transaction not found';
                } else if (xhr.status === 401) {
                    errorMessage = 'Session expired. Please login again';
                    // Optionally redirect to login
                    setTimeout(() => {
                        window.location.href = '/login/';
                    }, 2000);
                } else if (xhr.status === 500) {
                    errorMessage = 'Server error occurred while deleting transaction';
                }

                toastr.error(errorMessage);
                console.error('Delete error:', {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    responseText: xhr.responseText,
                    error: error
                });
            }
        });
    }
});
