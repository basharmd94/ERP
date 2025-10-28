
processReturn = function() {
    // Validate cart items
    if (!cartItems || cartItems.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'No Items',
            text: 'Please add items to the cart before processing return.',
            customClass: {
                confirmButton: 'btn btn-primary'
            }
        });
        return;
    }

    // Validate form data
    const formData = {
        invoice_date: $('#invoice-date').val(),
        receive_type: $('#receive-type').val(),
        customer: $('#customer').val(),
        supplier_select: $('#supplierSelect').val(),
        warehouse: $('#warehouse').val(),
        project: $('#project').val(),
        notes: $('#notes').val()
    };

    // Check required fields
    const requiredFields = [
        { field: 'invoice_date', name: 'Invoice Date' },
        { field: 'receive_type', name: 'Receive Type' },
        { field: 'customer', name: 'Customer' },
        { field: 'supplier_select', name: 'Supplier' },
        { field: 'warehouse', name: 'Warehouse' },
        { field: 'project', name: 'Project' }
    ];

    for (let required of requiredFields) {
        if (!formData[required.field]) {
            Swal.fire({
                icon: 'warning',
                title: 'Missing Information',
                text: `Please select ${required.name} before processing return.`,
                customClass: {
                    confirmButton: 'btn btn-primary'
                }
            });
            return;
        }
    }

    // Show confirmation dialog
    Swal.fire({
        title: 'Confirm Sales Return',
        text: `Are you sure you want to process this sales return with ${cartItems.length} item(s)?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, Process Return',
        cancelButtonText: 'Cancel',
        customClass: {
            confirmButton: 'btn btn-primary me-3',
            cancelButton: 'btn btn-label-secondary'
        },
        buttonsStyling: false
    }).then(function (result) {
        if (result.isConfirmed) {
            submitSalesReturn(formData);
        }
    });
};

function submitSalesReturn(formData) {
    // Get calculated totals from the UI
    const totalItems = parseFloat($('#cart-total-items').text()) || 0;
    const totalInvValue = parseFloat($('#cart-total-inv-value').text().replace('৳', '').replace(',', '')) || 0;
    const totalMktValue = parseFloat($('#cart-total-mkt-value').text().replace('৳', '').replace(',', '')) || 0;
    
    // Prepare data for submission
    const submitData = {
        formData: formData,
        cartItems: cartItems,
        totals: {
            totalItems: totalItems,
            totalInvValue: totalInvValue,
            totalMktValue: totalMktValue
        }
    };

    // Show loading dialog with SweetAlert2
    Swal.fire({
        title: 'Processing Sales Return',
        html: '<div class="d-flex justify-content-center align-items-center"><div class="spinner-border text-primary me-3" role="status"></div><span>Validating return data...</span></div>',
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    // Submit AJAX request
    $.ajax({
        url: '/sales/sales-return-confirm/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(submitData),
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                // Update loading message for processing
                Swal.update({
                    html: '<div class="d-flex justify-content-center align-items-center"><div class="spinner-border text-success me-3" role="status"></div><span>Processing inventory transactions...</span></div>'
                });

                // Simulate processing time and final success
                setTimeout(function() {
                    Swal.update({
                        html: '<div class="d-flex justify-content-center align-items-center"><div class="text-success me-3" style="font-size: 2rem;">✓</div><span>Sales return processed successfully!</span></div>'
                    });

                    // Clear cart and redirect after final message
                    setTimeout(function() {
                        Swal.close();
                        clearCart();

                        // Show success message
                        toastr.success(`Sales return ${response.sre_voucher} processed successfully!`);

                        // Open sales return detail page in new tab
                        if (response.redirect_url) {
                            window.open(response.redirect_url, '_blank');
                        } else {
                            window.open(`/sales/sales-return-detail/${response.sre_voucher}/`, '_blank');
                        }
                    }, 1000);
                }, 1500);
            } else {
                Swal.close();
                Swal.fire({
                    icon: 'error',
                    title: 'Processing Failed',
                    text: response.error || 'Failed to process sales return',
                    customClass: {
                        confirmButton: 'btn btn-primary'
                    }
                });
            }
        },
        error: function(xhr) {
            Swal.close();

            let errorMessage = 'An error occurred while processing the sales return.';

            if (xhr.responseJSON) {
                errorMessage = xhr.responseJSON.error || xhr.responseJSON.details || errorMessage;
            } else if (xhr.responseText) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.error || response.details || errorMessage;
                } catch (e) {
                    errorMessage = `Server error: ${xhr.status} ${xhr.statusText}`;
                }
            }

            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: errorMessage,
                customClass: {
                    confirmButton: 'btn btn-primary'
                }
            });
        }
    });
}

function clearCart() {
    // Clear cart items
    cartItems = [];
    cartCounter = 0;

    // Update cart display
    updateCartDisplay();

    // Clear localStorage
    if (typeof salesReturnStorage !== 'undefined' && salesReturnStorage.getCurrentZid) {
        const currentZid = salesReturnStorage.getCurrentZid();
        if (currentZid) {
            localStorage.removeItem(`salesReturnCart_${currentZid}`);
        }
    }

    // Reset form if needed
    $('#notes').val('');

    console.log('Cart cleared successfully');
}
