/**
 * DataTables Basic
 */

$(function () {
    'use strict';

    console.log("loaded")

    var dt_basic_table = $('.datatables-ajax'),
        dt_basic;

    // DataTable with Ajax
    // ---------------------------------------------------------------------

    if (dt_basic_table.length) {
        dt_basic = dt_basic_table.DataTable({
            processing: true,
            serverSide: false,
            ajax: {
                url: '/crossapp/api/item_group/',
                type: 'GET',
                dataSrc: 'item_group',
                error: function (xhr, error, thrown) {
                    console.error('Error loading item group:', error);
                }
            },
            columns: [
                { data: 'xcode', title: 'Item Group Code' },
                { data: 'xdescdet', title: 'Description' },
                { data: 'zactive', title: 'Status',
                    render: function(data) {
                        return (
                            '<span class="badge ' +
                            (data === '1' ? 'bg-label-success' : 'bg-label-danger') +
                            '">' +
                            (data === '1' ? 'Active' : 'Inactive') +
                            '</span>'
                        );
                    }
                },
                {   data: null, title: 'Actions',
                    orderable: false,
                    searchable: false,
                    render: function (data, type, full, meta) {
                        return (
                            '<div class="btn-group">' +
                            '<button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">' +
                            'Actions' +
                            '</button>' +
                            '<ul class="dropdown-menu">' +
                            '<li><a class="dropdown-item" href="javascript:;">Details</a></li>' +
                            '<li><a class="dropdown-item edit-item-group" href="javascript:;" data-item-group-code="' + full.xcode + '" data-item-group-name="' + (full.xdescdet || 'Unknown') + '">Edit</a></li>' +
                            '<li><a class="dropdown-item text-danger delete-item-group" href="javascript:;" data-item-group-code="' + full.xcode + '" data-item-group-name="' + (full.xdescdet || 'Unknown') + '">Delete</a></li>' +
                            '</ul>' +
                            '</div>'
                        );
                    }
                }
            ],
            order: [[0, 'asc']],
            dom:
                '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t' +
                '<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
            displayLength: 7,
            lengthMenu: [7, 10, 25, 50, 75, 100],
            // Removed buttons array since Add Brand button is already in HTML template
            responsive: {
                details: {
                    display: $.fn.dataTable.Responsive.display.modal({
                        header: function (row) {
                            var data = row.data();
                            return 'Details of ' + data['xcode'];
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
            }
        });
        // Header is already defined in HTML template, no need to add it here
    }

    // Clear form when Add Brand button is clicked
    $('[data-bs-target="#addItemGroupModal"]').on('click', function() {
        $('#addItemGroupForm')[0].reset();
        $('#itemGroupName').val('');
    });

    // Add Brand Modal Logic
    $('#addItemGroupForm').on('submit', function (e) {
        e.preventDefault();
        
        var itemGroupName = $('#itemGroupName').val().trim();
        
        // Basic validation
        if (!itemGroupName) {
            Swal.fire({
                icon: 'warning',
                title: 'Validation Error',
                text: 'Item group name is required!',
                customClass: {
                    confirmButton: 'btn btn-primary'
                }
            });
            return;
        }
        
        // Get CSRF token
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();
        // Send AJAX request to create item group (NOW AS JSON)
        $.ajax({
            url: '/crossapp/api/item_group/create/',
            type: 'POST',
            contentType: 'application/json',  // 👈 CRITICAL: Tell server we're sending JSON
            headers: {
                'X-CSRFToken': csrfToken  // 👈 Use header for CSRF (standard for JSON APIs)
            },
            data: JSON.stringify({  // 👈 Wrap data in JSON.stringify()
                'item_group_description': itemGroupName
                // Do NOT include csrfmiddlewaretoken in body — send in header instead
            }),
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Item group created successfully!',   
                        customClass: {
                            confirmButton: 'btn btn-success'
                        }
                    });
                    $('#addItemGroupModal').modal('hide');
                    $('#addItemGroupForm')[0].reset();
                    dt_basic.ajax.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.message || 'Unknown error occurred while creating the item group.',
                        customClass: {
                            confirmButton: 'btn btn-primary'
                        }
                    });
                }
            },
            error: function(xhr) {
                var errorMsg = 'Error creating item group';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: errorMsg,
                    customClass: {
                        confirmButton: 'btn btn-primary'
                    }
                });
            }
        });
    });

    // Edit Item Group Event Handler
    $(document).on('click', '.edit-item-group', function() {
        var itemGroupCode = $(this).data('item-group-code');
        var itemGroupName = $(this).data('item-group-name');
        
        // Populate edit form
        $('#editItemGroupCode').val(itemGroupCode);
        $('#editItemGroupName').val(itemGroupName);
        
        // Show edit modal
        $('#editItemGroupModal').modal('show');
    });

    // Update Item Group
    $('#editItemGroupForm').on('submit', function(e) {
        e.preventDefault();
        var itemGroupCode = $('#editItemGroupCode').val();
        var itemGroupName = $('#editItemGroupName').val().trim();

        if (!itemGroupName) {
            Swal.fire({
                icon: 'warning',
                title: 'Validation Error',
                text: 'Item group name is required!',
                customClass: {
                    confirmButton: 'btn btn-primary'
                }
            });
            return;
        }

        // Get CSRF token
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        // Send AJAX request to update item group (AS JSON!)
        $.ajax({
            url: '/crossapp/api/item_group/update/' + encodeURIComponent(itemGroupCode) + '/',
            type: 'POST',
            contentType: 'application/json',  // 👈 CRITICAL: Tell server we're sending JSON
            headers: {
                'X-CSRFToken': csrfToken  // 👈 Send CSRF in header, not body
            },
            data: JSON.stringify({  // 👈 Wrap payload in JSON.stringify()
                'item_group_description': itemGroupName
                // Do NOT include csrfmiddlewaretoken here — use header instead
            }),
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Item group updated successfully!',
                        customClass: {
                            confirmButton: 'btn btn-success'
                        }
                    });
                    $('#editItemGroupModal').modal('hide');
                    dt_basic.ajax.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.message || 'Unknown error occurred while updating the item group.',
                        customClass: {
                            confirmButton: 'btn btn-primary'
                        }
                    });
                }
            },
            error: function(xhr) {
                var errorMsg = 'Error updating item group';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: errorMsg,
                    customClass: {
                        confirmButton: 'btn btn-primary'
                    }
                });
            }
});
    });

    // Delete Item Group Event Handler
    $(document).on('click', '.delete-item-group', function() {
        var itemGroupCode = $(this).data('item-group-code');
        var itemGroupName = $(this).data('item-group-name');
        
        Swal.fire({
            title: 'Are you sure?',
            text: "You are about to delete the item group '" + itemGroupName + "'. You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!',
            customClass: {
                confirmButton: 'btn btn-primary me-3',
                cancelButton: 'btn btn-label-secondary'
            },
            buttonsStyling: false
        }).then(function (result) {
            if (result.value) {
                deleteItemGroup(itemGroupCode);
            }
        });
    });

    function deleteItemGroup(itemGroupCode) {
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        // Validate itemGroupCode before making request
        if (!itemGroupCode || !itemGroupCode.trim()) {
            Swal.fire("Error", "Invalid item group code", "error");
            return;
        }
        $.ajax({
            url: '/crossapp/api/item_group/delete/' + encodeURIComponent(itemGroupCode) + '/',
            type: 'POST',
            // 👇 REMOVE data: {} — we don't need to send anything in body!
            headers: {
                'X-CSRFToken': csrfToken  // 👈 Send CSRF token in header (best practice)
            },
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Deleted!',
                        text: `Itemgroup code ${itemGroupCode} deleted successfully`,
                        customClass: {
                            confirmButton: 'btn btn-success'
                        }
                    });
                    dt_basic.ajax.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.message || 'Unknown error occurred while deleting the item group.',
                        customClass: {
                            confirmButton: 'btn btn-primary'
                        }
                    });
                }
            },
            error: function(xhr) {
                var errorMsg = 'Error deleting item group';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: errorMsg,
                    customClass: {
                        confirmButton: 'btn btn-primary'
                    }
                });
            }
        });
}


});