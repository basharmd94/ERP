/**
 * Sales Item List DataTable (AJAX)
 */

'use strict';

$(function () {
    let salesItemTable;

    // Initialize DataTable
    function initializeDataTable() {
        if ($.fn.DataTable.isDataTable('#sales-item-list-table')) {
            $('#sales-item-list-table').DataTable().destroy();
        }

        salesItemTable = $('#sales-item-list-table').DataTable({
            processing: true,
            serverSide: true,
            ajax: {
                url: '/sales/api/sales-item-list/',
                type: 'GET',
                error: function(xhr, error, code) {
                    console.error('DataTable AJAX error:', error);
                    showError('Failed to load sales orders. Please try again.');
                }
            },
            columns: [
                {
                    data: 0,
                    title: 'Date',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<span class="badge bg-light text-dark">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 1,
                    title: 'Order Number',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<strong class="text-primary">${data}</strong>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 2,
                    title: 'Status',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            let badgeClass = 'bg-secondary';
                            switch(data.toLowerCase()) {
                                case 'open':
                                    badgeClass = 'bg-warning';
                                    break;
                                case 'closed':
                                    badgeClass = 'bg-success';
                                    break;
                                case 'cancelled':
                                    badgeClass = 'bg-danger';
                                    break;
                                case 'pending':
                                    badgeClass = 'bg-info';
                                    break;
                            }
                            return `<span class="badge ${badgeClass}">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 3,
                    title: 'Warehouse',
                    orderable: true,
                    searchable: true
                },
                {
                    data: 4,
                    title: 'Payment Type',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            const paymentType = data.toLowerCase();
                            let badgeClass = '';

                            if (paymentType === 'cash') {
                                badgeClass = 'bg-success text-white';  // Green for Cash
                            } else if (paymentType === 'card') {
                                badgeClass = 'bg-primary text-white';  // Blue for Card
                            } else {
                                badgeClass = 'bg-secondary text-white'; // Gray for others
                            }

                            return `<span class="badge ${badgeClass}">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 5,
                    title: 'Bank Name',
                    orderable: true,
                    searchable: true
                },
                {
                    data: 6,
                    title: 'Card Amount',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data !== null && data !== undefined) {
                            // Get payment type from the same row (index 4)
                            const paymentType = row[4] ? row[4].toLowerCase() : '';

                            // Format number with commas and 2 decimal places
                            const amount = parseFloat(data);
                            const formattedAmount = amount.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });

                            // Apply conditional colors based on payment type
                            let colorClass = '';
                            if (paymentType === 'cash') {
                                colorClass = 'text-success fw-bold';  // Green for Cash
                            } else if (paymentType === 'card') {
                                colorClass = 'text-primary fw-bold';  // Blue for Card
                            } else {
                                colorClass = 'text-secondary fw-bold'; // Gray for others
                            }

                            return `<span class="${colorClass}">${formattedAmount}</span>`;
                        }
                        return '<span class="text-muted">0.00</span>';
                    }
                },
                {
                    data: 7,
                    title: 'Total Amount',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data !== null && data !== undefined) {
                            // Format number with commas and 2 decimal places
                            const amount = parseFloat(data);
                            const formattedAmount = amount.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                            return `<span class="text-success fw-bold">${formattedAmount}</span>`;
                        }
                        return '<span class="text-muted">0.00</span>';
                    }
                },
                {
                    data: 8,
                    title: 'Actions',
                    orderable: false,
                    searchable: false,
                    className: 'text-center'
                }
            ],
            order: [[0, 'desc']], // Order by date descending
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>' +
                 '<"table-responsive"t>' +
                 '<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
            language: {
                processing: '<div class="d-flex justify-content-center align-items-center">' +
                           '<div class="spinner-border text-primary me-2" role="status">' +
                           '<span class="visually-hidden">Loading...</span></div>' +
                           'Loading sales orders...</div>',
                emptyTable: '<div class="text-center py-4">' +
                           '<i class="tf-icons ti ti-shopping-cart-off ti-lg text-muted mb-2 d-block"></i>' +
                           '<div class="text-muted">No sales orders found</div>' +
                           '<small class="text-muted">Try adjusting your search criteria</small></div>',
                zeroRecords: '<div class="text-center py-4">' +
                            '<i class="tf-icons ti ti-search-off ti-lg text-muted mb-2 d-block"></i>' +
                            '<div class="text-muted">No matching records found</div>' +
                            '<small class="text-muted">Try different search terms</small></div>',
                search: '<i class="tf-icons ti ti-search me-1"></i>',
                searchPlaceholder: 'Search orders...',
                lengthMenu: 'Show _MENU_ entries',
                info: 'Showing _START_ to _END_ of _TOTAL_ entries',
                infoEmpty: 'No entries available',
                infoFiltered: '(filtered from _MAX_ total entries)',
                paginate: {
                    first: '<i class="tf-icons ti ti-chevrons-left"></i>',
                    previous: '<i class="tf-icons ti ti-chevron-left"></i>',
                    next: '<i class="tf-icons ti ti-chevron-right"></i>',
                    last: '<i class="tf-icons ti ti-chevrons-right"></i>'
                }
            },
            responsive: true,
            autoWidth: false,
            drawCallback: function(settings) {
                // Initialize tooltips for action buttons
                $('[data-bs-toggle="tooltip"]').tooltip();
            }
        });
    }

    // Initialize when the sales list tab is shown
    $('button[data-bs-target="#sales-list-tab"]').on('shown.bs.tab', function (e) {
        if (!salesItemTable) {
            initializeDataTable();
        } else {
            salesItemTable.ajax.reload();
        }
    });

    // Initialize DataTable on page load
    $(document).ready(function() {
        initializeDataTable();
    });

    // Refresh button functionality
    $(document).on('click', '#refresh-sales-table', function() {
        if (salesItemTable) {
            salesItemTable.ajax.reload();
            showSuccess('Table refreshed successfully');
        }
    });

    // Show error message
    function showError(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: message,
                confirmButtonText: 'OK'
            });
        } else {
            alert(message);
        }
    }

    // Show success message
    function showSuccess(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: 'Success',
                text: message,
                timer: 2000,
                showConfirmButton: false
            });
        }
    }
});

// Action functions for the dropdown buttons
function viewSalesOrder(orderNumber) {
    console.log('View sales order:', orderNumber);
    // TODO: Implement view functionality
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'info',
            title: 'View Sales Order',
            text: `View functionality for ${orderNumber} will be implemented later.`,
            confirmButtonText: 'OK'
        });
    }
}

function editSalesOrder(orderNumber) {
    console.log('Edit sales order:', orderNumber);
    // TODO: Implement edit functionality
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'info',
            title: 'Edit Sales Order',
            text: `Edit functionality for ${orderNumber} will be implemented later.`,
            confirmButtonText: 'OK'
        });
    }
}

function printSalesOrder(orderNumber) {
    console.log('Print sales order:', orderNumber);

    try {
        // Construct the print URL for sales invoice
        const printUrl = `/sales/print-invoice/${orderNumber}/`;

        console.log('Opening print URL:', printUrl);

        // Open in a new window/tab optimized for printing
        const printWindow = window.open(
            printUrl,
            'sales-invoice-' + orderNumber,
            'width=800,height=600,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no'
        );

        if (printWindow) {
            // Focus on the new window
            printWindow.focus();

            // Show success message
            if (typeof toastr !== 'undefined') {
                toastr.info('Invoice PDF opened in new window. You can print or download it.', 'Print Ready');
            }
        } else {
            // Handle popup blocker
            if (typeof toastr !== 'undefined') {
                toastr.warning('Popup blocked. Please allow popups and try again, or manually navigate to: ' + printUrl, 'Print Blocked');
            }
            // Fallback: try to open in same tab
            // window.open(printUrl, '_blank');
        }
    } catch (error) {
        console.error('Error opening print window:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Failed to open print window. Please try printing manually.', 'Print Error');
        }
    }
}

function deleteSalesOrder(orderNumber) {
    console.log('Delete sales order:', orderNumber);
    // TODO: Implement delete functionality with confirmation
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Are you sure?',
            text: `Do you want to delete order ${orderNumber}? This action cannot be undone!`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                // TODO: Implement actual delete API call
                Swal.fire({
                    icon: 'info',
                    title: 'Delete Sales Order',
                    text: `Delete functionality for ${orderNumber} will be implemented later.`,
                    confirmButtonText: 'OK'
                });
            }
        });
    }
}
