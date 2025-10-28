/**
 * Sales Return Item List DataTable (AJAX)
 */


$(function () {
    let salesReturnTable;

    // Initialize DataTable
    function initializeDataTable() {
        if ($.fn.DataTable.isDataTable('#sales-return-item-list-table')) {
            $('#sales-return-item-list-table').DataTable().destroy();
        }

        salesReturnTable = $('#sales-return-item-list-table').DataTable({
            processing: true,
            serverSide: true,
            ajax: {
                url: '/sales/api/sales-return-item-list/',
                type: 'GET',
                error: function(xhr, error, code) {
                    console.error('DataTable AJAX error:', error);
                    showError('Failed to load sales returns. Please try again.');
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
                            return `<span class="badge rounded-pill bg-label-dark">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 1,
                    title: 'SRE Number',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<strong class="text-danger">${data}</strong>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 2,
                    title: 'Warehouse',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<span class="badge rounded-pill bg-label-primary">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 3,
                    title: 'GL Ref No',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<span class="text-muted">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 4,
                    title: 'Status',
                    orderable: true,
                    searchable: true,
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            let badgeClass = 'bg-secondary';
                            switch(data) {
                                case '1-Open':
                                    badgeClass = 'bg-warning';
                                    break;
                                case '5-Confirmed':
                                    badgeClass = 'badge rounded-pill bg-label-success';
                                    break;
                                case 'cancelled':
                                    badgeClass = 'bg-danger';
                                    break;
                                case 'pending':
                                    badgeClass = 'bg-info';
                                    break;
                                case 'returned':
                                    badgeClass = 'bg-danger';
                                    break;
                                case 'processed':
                                    badgeClass = 'bg-success';
                                    break;
                            }
                            return `<span class="badge ${badgeClass}">${data}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    data: 5,
                    title: 'Quick Act',
                    orderable: false,
                    searchable: false,
                    className: 'text-center',
                    width: '120px',
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            const sreNumber = data;
                            return `
                                <div class="btn-group" role="group" aria-label="Quick Actions">
                                    <a href="/sales/sales-return-detail/${sreNumber}/"
                                       target="_blank"
                                       class="btn btn-sm btn-outline-primary"
                                       title="View Details">
                                        <i class="tf-icons ti ti-eye"></i>
                                    </a>
                                    <a href="/sales/sales-return-print/${sreNumber}/"
                                       target="_blank"
                                       class="btn btn-sm btn-outline-info"
                                       title="Print">
                                        <i class="tf-icons ti ti-printer"></i>
                                    </a>
                                    <a href="/sales/sales-return-export-excel/${sreNumber}/"
                                       class="btn btn-sm btn-outline-success"
                                       title="Export Excel">
                                        <i class="tf-icons ti ti-file-spreadsheet"></i>
                                    </a>
                                </div>
                            `;
                        }
                        return '';
                    }
                },
                {
                    data: 6,
                    title: 'Actions',
                    orderable: false,
                    searchable: false,
                    className: 'text-center',
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            const sreNumber = data;
                            return `
                                <div class="dropdown">
                                    <button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle"
                                            data-bs-toggle="dropdown" aria-expanded="false">
                                        <i class="tf-icons ti ti-dots-vertical"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="/sales/sales-return-detail/${sreNumber}/">
                                            <i class="tf-icons ti ti-eye me-1"></i>View</a></li>
                                        <li><a class="dropdown-item" href="/sales/sales-return-print/${sreNumber}/" target="_blank">
                                            <i class="tf-icons ti ti-printer me-1"></i>Print</a></li>
                                        <li><a class="dropdown-item" href="/sales/sales-return-export-excel/${sreNumber}/">
                                            <i class="tf-icons ti ti-file-spreadsheet me-1"></i>Export Excel</a></li>
                                        <li><hr class="dropdown-divider"></li>
                                        <li><a class="dropdown-item text-danger" href="#" onclick="deleteSalesReturn('${sreNumber}')">
                                            <i class="tf-icons ti ti-trash me-1"></i>Delete</a></li>
                                    </ul>
                                </div>
                            `;
                        }
                        return '';
                    }
                }
            ],
            order: [[0, 'desc']], // Order by date descending
            pageLength: 10,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>' +
                 '<"table-responsive"t>' +
                 '<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
            language: {
                processing: '<div class="d-flex justify-content-center align-items-center">' +
                           '<div class="spinner-border text-primary me-2" role="status">' +
                           '<span class="visually-hidden">Loading...</span></div>' +
                           'Loading sales returns...</div>',
                emptyTable: '<div class="text-center py-4">' +
                           '<i class="tf-icons ti ti-arrow-back-up ti-lg text-muted mb-2 d-block"></i>' +
                           '<div class="text-muted">No sales returns found</div>' +
                           '<small class="text-muted">Try adjusting your search criteria</small></div>',
                zeroRecords: '<div class="text-center py-4">' +
                            '<i class="tf-icons ti ti-search-off ti-lg text-muted mb-2 d-block"></i>' +
                            '<div class="text-muted">No matching records found</div>' +
                            '<small class="text-muted">Try different search terms</small></div>',
                search: '<i class="tf-icons ti ti-search me-1"></i>',
                searchPlaceholder: 'Search returns...',
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

    // Initialize when the sales return list tab is shown
    $('button[data-bs-target="#sales-return-list-tab"]').on('shown.bs.tab', function (e) {
        if (!salesReturnTable) {
            initializeDataTable();
        } else {
            salesReturnTable.ajax.reload();
        }
    });

    // Initialize DataTable on page load
    $(document).ready(function() {
        initializeDataTable();
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
function viewSalesReturn(sreNumber) {
    console.log('View sales return:', sreNumber);
    // Open sales return detail page in new tab
    window.open(`/sales/sales-return-detail/${sreNumber}/`, '_blank');
}

function printSalesReturn(sreNumber) {
    console.log('Print sales return:', sreNumber);

    try {
        // Construct the print URL for sales return
        const printUrl = `/sales/sales-return-print/${sreNumber}/`;

        console.log('Opening sales return print URL:', printUrl);

        // Open in a new window/tab optimized for printing
        const printWindow = window.open(
            printUrl,
            'sales-return-' + sreNumber,
            'width=800,height=600,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no'
        );

        if (printWindow) {
            // Focus on the new window
            printWindow.focus();

            // Show success message
            if (typeof toastr !== 'undefined') {
                toastr.info('Sales Return document opened in new window. You can print or download it.', 'Print Ready');
            }
        } else {
            // Handle popup blocker
            if (typeof toastr !== 'undefined') {
                toastr.warning('Popup blocked. Please allow popups and try again, or manually navigate to: ' + printUrl, 'Print Blocked');
            }
        }
    } catch (error) {
        console.error('Error opening sales return print window:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Failed to open print window. Please try printing manually.', 'Print Error');
        }
    }
}

function exportSalesReturnExcel(sreNumber) {
    console.log('Export sales return to Excel:', sreNumber);

    try {
        // Construct the Excel export URL
        const exportUrl = `/sales/sales-return-export-excel/${sreNumber}/`;

        console.log('Opening Excel export URL:', exportUrl);

        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `sales_return_${sreNumber}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Show success message
        if (typeof toastr !== 'undefined') {
            toastr.success('Excel export started. The file will download shortly.', 'Export Started');
        }
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Failed to export to Excel. Please try again.', 'Export Error');
        }
    }
}

function deleteSalesReturn(sreNumber) {
    console.log('Delete sales return:', sreNumber);
    // TODO: Implement delete functionality with confirmation
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Are you sure?',
            text: `Do you want to delete sales return ${sreNumber}? This action cannot be undone!`,
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
                    title: 'Delete Sales Return',
                    text: `Delete functionality for ${sreNumber} will be implemented later.`,
                    confirmButtonText: 'OK'
                });
            }
        });
    }
}
