/**
 * Receive Entry List DataTable (AJAX)
 */

'use strict';

$(function () {
    let receiveEntryTable;

    // Initialize DataTable
    function initializeDataTable() {
        if ($.fn.DataTable.isDataTable('#receive-entry-list-table')) {
            $('#receive-entry-list-table').DataTable().destroy();
        }

        receiveEntryTable = $('#receive-entry-list-table').DataTable({
            processing: true,
            serverSide: true,
            ajax: {
                url: '/inventory/api/receive_entry_list/',
                type: 'GET',
                error: function(xhr, error, code) {
                    console.error('DataTable AJAX error:', error);
                    showError('Failed to load receive entries. Please try again.');
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
                    title: 'Voucher Number',
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
                            }
                            return `<span class="badge ${badgeClass}">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 3,
                    title: 'Project',
                    orderable: true,
                    searchable: true
                },
                {
                    data: 4,
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
                           'Loading receive entries...</div>',
                emptyTable: '<div class="text-center py-4">' +
                           '<i class="tf-icons ti ti-package-off ti-lg text-muted mb-2 d-block"></i>' +
                           '<div class="text-muted">No receive entries found</div>' +
                           '<small class="text-muted">Try adjusting your search criteria</small></div>',
                zeroRecords: '<div class="text-center py-4">' +
                            '<i class="tf-icons ti ti-search-off ti-lg text-muted mb-2 d-block"></i>' +
                            '<div class="text-muted">No matching records found</div>' +
                            '<small class="text-muted">Try different search terms</small></div>',
                search: '<i class="tf-icons ti ti-search me-1"></i>',
                searchPlaceholder: 'Search entries...',
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

    // Initialize when the receipt list tab is shown
    $('button[data-bs-target="#receipt-list-tab"]').on('shown.bs.tab', function (e) {
        if (!receiveEntryTable) {
            initializeDataTable();
        } else {
            receiveEntryTable.ajax.reload();
        }
    });

    // Refresh button functionality
    $(document).on('click', '#refresh-table', function() {
        if (receiveEntryTable) {
            receiveEntryTable.ajax.reload();
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
function viewEntry(voucherNumber) {
    console.log('View entry:', voucherNumber);
    // TODO: Implement view functionality
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'info',
            title: 'View Entry',
            text: `View functionality for ${voucherNumber} will be implemented later.`,
            confirmButtonText: 'OK'
        });
    }
}

function editEntry(voucherNumber) {
    console.log('Edit entry:', voucherNumber);
    // TODO: Implement edit functionality
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'info',
            title: 'Edit Entry',
            text: `Edit functionality for ${voucherNumber} will be implemented later.`,
            confirmButtonText: 'OK'
        });
    }
}

function printEntry(voucherNumber) {
    console.log('Print entry:', voucherNumber);
    // TODO: Implement print functionality
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'info',
            title: 'Print Entry',
            text: `Print functionality for ${voucherNumber} will be implemented later.`,
            confirmButtonText: 'OK'
        });
    }
}

function deleteEntry(voucherNumber) {
    console.log('Delete entry:', voucherNumber);
    // TODO: Implement delete functionality with confirmation
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Are you sure?',
            text: `Do you want to delete voucher ${voucherNumber}? This action cannot be undone!`,
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
                    title: 'Delete Entry',
                    text: `Delete functionality for ${voucherNumber} will be implemented later.`,
                    confirmButtonText: 'OK'
                });
            }
        });
    }
}
