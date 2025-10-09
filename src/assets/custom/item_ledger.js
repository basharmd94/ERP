/**
 * Item Ledger DataTable
 */

$(function () {
    'use strict';

    console.log("Item Ledger DataTable loaded");

    // Function to get cookie value by name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var dt_item_ledger_table = $('#item-ledger-table'),
        dt_item_ledger;



    // Function to get filter parameters
    function getFilterParams() {
        return {
            warehouse: $('#warehouse').val() || '',
            from_date: $('#from_date').val() || '',
            to_date: $('#to_date').val() || '',
            select_item: $('#select_item').val() || ''
        };
    }

    // Item Ledger DataTable with Ajax
    // ---------------------------------------------------------------------

    if (dt_item_ledger_table.length) {
        dt_item_ledger = dt_item_ledger_table.DataTable({
            processing: true,
            serverSide: false,
            autoWidth: false,
            responsive: true,
            deferRender: true,
            ajax: {
                url: '/inventory/reports/item-ledger/get-item-ledger/',
                type: 'GET',
                data: function(d) {
                    // Add filter parameters to the request
                    var filters = getFilterParams();
                    return $.extend({}, d, filters);
                },
                dataSrc: function(json) {
                    if (json.success) {
                        return json.data;
                    } else {
                        console.error('Error loading item ledger data:', json.error);
                        return [];
                    }
                },
                error: function (xhr, error, thrown) {
                    console.error('AJAX Error loading item ledger:', error);
                    console.error('Response:', xhr.responseText);
                }
            },
            columns: [
                {
                    data: 'xdate',
                    title: 'Date',
                    render: function(data) {
                        if (data) {
                            // Format date as DD/MM/YYYY
                            var date = new Date(data);
                            return date.toLocaleDateString('en-GB');
                        }
                        return '-';
                    }
                },
                {
                    data: 'xdocnum',
                    title: 'Document',
                    render: function(data) {
                        return data || '-';
                    }
                },
                {
                    data: 'ximtrnnum',
                    title: 'Transaction #',
                    render: function(data) {
                        return data || '-';
                    }
                },
                {
                    data: 'xitem',
                    title: 'Item',
                    render: function(data) {
                        return data || '-';
                    }
                },
                {
                    data: 'transaction_type',
                    title: 'Type',
                    render: function(data) {
                        var badgeClass = '';
                        if (data === 'Receipt') {
                            badgeClass = 'bg-success';
                        } else if (data === 'Issue') {
                            badgeClass = 'bg-danger';
                        } else {
                            badgeClass = 'bg-secondary';
                        }
                        return '<span class="badge ' + badgeClass + '">' + (data || 'Unknown') + '</span>';
                    }
                },
                {
                    data: 'transaction_qty',
                    title: 'Txn Qty',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            return parseFloat(data).toFixed(3);
                        }
                        return '0.000';
                    },
                    className: 'text-end'
                },
                {
                    data: 'transaction_rate',
                    title: 'Txn Rate',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            return parseFloat(data).toFixed(2);
                        }
                        return '0.00';
                    },
                    className: 'text-end'
                },
                {
                    data: 'transaction_value',
                    title: 'Txn Value',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            var value = parseFloat(data);
                            var className = value >= 0 ? 'text-success' : 'text-danger';
                            return '<span class="' + className + '">' + value.toFixed(2) + '</span>';
                        }
                        return '0.00';
                    },
                    className: 'text-end'
                },
                {
                    data: 'balance_qty',
                    title: 'Balance Qty',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            var qty = parseFloat(data);
                            var className = qty >= 0 ? 'text-primary fw-bold' : 'text-danger fw-bold';
                            return '<span class="' + className + '">' + qty.toFixed(3) + '</span>';
                        }
                        return '0.000';
                    },
                    className: 'text-end'
                },
                {
                    data: 'balance_rate',
                    title: 'Balance Rate',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            return '<span class="text-info">' + parseFloat(data).toFixed(2) + '</span>';
                        }
                        return '0.00';
                    },
                    className: 'text-end'
                },
                {
                    data: 'balance_value',
                    title: 'Balance Value',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            var value = parseFloat(data);
                            var className = value >= 0 ? 'text-primary fw-bold' : 'text-danger fw-bold';
                            return '<span class="' + className + '">' + value.toFixed(2) + '</span>';
                        }
                        return '0.00';
                    },
                    className: 'text-end'
                },
                {
                    data: 'opening_qty',
                    title: 'Opening Qty',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            return '<span class="text-warning fw-bold">' + parseFloat(data).toFixed(3) + '</span>';
                        }
                        return '0.000';
                    },
                    className: 'text-end'
                },
                {
                    data: 'opening_val',
                    title: 'Opening Value',
                    render: function(data) {
                        if (data !== null && data !== undefined) {
                            return '<span class="text-warning fw-bold">' + parseFloat(data).toFixed(2) + '</span>';
                        }
                        return '0.00';
                    },
                    className: 'text-end'
                }
            ],
             language: {
                 processing: "Loading item ledger data...",
                 emptyTable: "Select an item and date range to view ledger data",
                 zeroRecords: "No transactions found for the selected criteria"
             },
            //  ordering: false, // Disable client-side sorting to use server-side ORDER BY
             pageLength: 25,
             lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-3 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
            displayLength: 25,
            lengthMenu: [10, 25, 50, 75, 100],
            buttons: [
                {
                    extend: 'collection',
                    className: 'btn btn-label-primary dropdown-toggle me-2',
                    text: '<i class="ti ti-file-export me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
                    buttons: [
                        {
                            extend: 'print',
                            text: '<i class="ti ti-printer me-1"></i>Print',
                            className: 'dropdown-item',
                            exportOptions: {
                                columns: ':visible',
                                format: {
                                    body: function (data, row, column, node) {
                                        // Remove HTML tags and return plain text
                                        return $('<div>').html(data).text();
                                    }
                                }
                            }
                        },
                        {
                            extend: 'csv',
                            text: '<i class="ti ti-file-text me-1"></i>Csv',
                            className: 'dropdown-item',
                            exportOptions: {
                                columns: ':visible',
                                format: {
                                    body: function (data, row, column, node) {
                                        // Remove HTML tags and return plain text
                                        return $('<div>').html(data).text();
                                    }
                                }
                            }
                        },
                        {
                            extend: 'excel',
                            text: '<i class="ti ti-file-spreadsheet me-1"></i>Excel',
                            className: 'dropdown-item',
                            exportOptions: {
                                columns: ':visible',
                                format: {
                                    body: function (data, row, column, node) {
                                        // Remove HTML tags and return plain text
                                        return $('<div>').html(data).text();
                                    }
                                }
                            }
                        },
                        {
                            extend: 'pdf',
                            text: '<i class="ti ti-file-description me-1"></i>Pdf',
                            className: 'dropdown-item',
                            exportOptions: {
                                columns: ':visible',
                                format: {
                                    body: function (data, row, column, node) {
                                        // Remove HTML tags and return plain text
                                        return $('<div>').html(data).text();
                                    }
                                }
                            }
                        },
                        {
                            extend: 'copy',
                            text: '<i class="ti ti-copy me-1"></i>Copy',
                            className: 'dropdown-item',
                            exportOptions: {
                                columns: ':visible',
                                format: {
                                    body: function (data, row, column, node) {
                                        // Remove HTML tags and return plain text
                                        return $('<div>').html(data).text();
                                    }
                                }
                            }
                        }
                    ]
                },
                {
                    text: '<i class="ti ti-refresh me-sm-1"></i> <span class="d-none d-sm-inline-block">Refresh</span>',
                    className: 'btn btn-primary',
                    action: function (e, dt, node, config) {
                        dt.ajax.reload();
                    }
                }
            ],
            responsive: {
                details: {
                    display: $.fn.dataTable.Responsive.display.modal({
                        header: function (row) {
                            var data = row.data();
                            return 'Details of Item: ' + (data['xitem'] || 'N/A');
                        }
                    }),
                    type: 'column',
                    renderer: function (api, rowIdx, columns) {
                        var data = $.map(columns, function (col, i) {
                            return col.columnIndex !== 0 ?
                                '<tr data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                                '<td>' + col.title + ':' + '</td> ' +
                                '<td>' + col.data + '</td>' +
                                '</tr>' : '';
                        }).join('');

                        return data ?
                            $('<table class="table"/>').append('<tbody>' + data + '</tbody>') : false;
                    }
                }
            },
            language: {
                search: '',
                searchPlaceholder: 'Search Item Ledger...',
                lengthMenu: '_MENU_',
                info: 'Showing _START_ to _END_ of _TOTAL_ entries',
                infoEmpty: 'Showing 0 to 0 of 0 entries',
                infoFiltered: '(filtered from _MAX_ total entries)',
                paginate: {
                    first: 'First',
                    last: 'Last',
                    next: 'Next',
                    previous: 'Previous'
                }
            }
        });

        // Add title to the DataTable
        $('div.head-label').html('<h5 class="card-title mb-0">Item Ledger Data</h5>');
    }

    // Wait a bit to ensure all libraries are loaded
    setTimeout(function() {
        // Initialize filter components
        initializeFilters();
    }, 500);

    // Filter functionality
    function initializeFilters() {
        console.log("Initializing filters...");
        console.log("jQuery version:", $.fn.jquery);
        console.log("Document ready state:", document.readyState);

        // Check if Select2 is available
        if (typeof $.fn.select2 === 'undefined') {
            console.error("Select2 is not loaded!");
            return;
        } else {
            console.log("Select2 is available");
        }

        // Check if elements exist
        var warehouseEl = $('#warehouse');
        var selectItemEl = $('#select_item');

        console.log("Warehouse element found:", warehouseEl.length > 0);
        console.log("Select item element found:", selectItemEl.length > 0);

        if (warehouseEl.length === 0) {
            console.error("Warehouse element not found!");
        }
        if (selectItemEl.length === 0) {
            console.error("Select item element not found!");
        }

        // Initialize Select2 for warehouse dropdown
        try {
            $('#warehouse').select2({
                placeholder: 'Select warehouse',
                allowClear: true
            });
            console.log("Warehouse Select2 initialized successfully");
        } catch (error) {
            console.error("Error initializing warehouse Select2:", error);
        }

        // Initialize Select2 for item selection using reusable function
        if (typeof window.initItemSelect === 'function') {
            initItemSelect('#select_item', {
                placeholder: 'Search for an item...',
                minimumInputLength: 1
            });
        } else {
            console.error("initItemSelect function not found. Make sure items.js is loaded.");
        }


        // Initialize Bootstrap date pickers
        $('#from_date, #to_date').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true,
            clearBtn: true,
            orientation: 'bottom auto',
            container: 'body'
        });

        // Auto-trigger data fetch when item is selected
        $('#select_item').on('select2:select', function(e) {
            var selectedItem = $(this).val();
            var fromDate = $('#from_date').val();

            if (selectedItem && fromDate) {
                // Automatically reload the DataTable when item is selected
                dt_item_ledger.ajax.reload();
            } else if (selectedItem && !fromDate) {
                // Show message if from_date is not selected
                alert('Please select a from date to view item ledger.');
                $('#from_date').focus();
            }
        });

        // Also trigger when from_date changes and item is already selected
        $('#from_date').on('change', function() {
            var selectedItem = $('#select_item').val();
            var fromDate = $(this).val();

            if (selectedItem && fromDate) {
                // Automatically reload the DataTable when from_date is set
                dt_item_ledger.ajax.reload();
            }
        });

        // Trigger when to_date changes (optional filter)
        $('#to_date').on('change', function() {
            var selectedItem = $('#select_item').val();
            var fromDate = $('#from_date').val();

            if (selectedItem && fromDate) {
                // Automatically reload the DataTable when to_date changes
                dt_item_ledger.ajax.reload();
            }
        });

        // Trigger when warehouse changes (optional filter)
        $('#warehouse').on('change', function() {
            var selectedItem = $('#select_item').val();
            var fromDate = $('#from_date').val();

            if (selectedItem && fromDate) {
                // Automatically reload the DataTable when warehouse changes
                dt_item_ledger.ajax.reload();
            }
        });
    }



    // Refresh data every 30 seconds (optional)
    // setInterval(function() {
    //     if (dt_item_ledger) {
    //         dt_item_ledger.ajax.reload(null, false);
    //     }
    // }, 30000);
});
