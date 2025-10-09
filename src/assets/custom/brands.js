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
            serverSide: true,
            ajax: {
                url: '/crossapp/api/brands/',
                type: 'GET',
                dataSrc: 'brands',
                error: function (xhr, error, thrown) {
                    console.error('Error loading brands:', error);
                }
            },
            columns: [
                { data: 'xcode', title: 'Brand Code' },
                { data: 'xdescdet', title: 'Description' },
                {  data: 'zactive',  title: 'Status',
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
                            '<li><a class="dropdown-item edit-brand" href="javascript:;" data-brand-code="' + full.xcode + '" data-brand-name="' + (full.xcode || 'Unknown') + '">Edit</a></li>' +
                            '<li><a class="dropdown-item text-danger delete-brand" href="javascript:;" data-brand-code="' + full.xcode + '" data-brand-name="' + (full.xcode || 'Unknown') + '">Delete</a></li>' +
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
    $('[data-bs-target="#addBrandModal"]').on('click', function() {
        $('#addBrandForm')[0].reset();
        $('#brandName').val('');
    });

    // Add Brand Modal Logic
    $('#addBrandForm').on('submit', function (e) {
        e.preventDefault();

        var brandName = $('#brandName').val().trim();

        // Basic validation
        if (!brandName) {
            Swal.fire({
                icon: 'warning',
                title: 'Validation Error',
                text: 'Brand name is required!',
                customClass: {
                    confirmButton: 'btn btn-primary'
                }
            });
            return;
        }

        // Get CSRF token
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        // Send AJAX request to create brand
        $.ajax({
            url: '/crossapp/api/brands/create/',
            type: 'POST',
            data: {
                'brandName': brandName,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Brand created successfully!',
                        customClass: {
                            confirmButton: 'btn btn-success'
                        }
                    });
                    $('#addBrandModal').modal('hide');
                    $('#addBrandForm')[0].reset();
                    dt_basic.ajax.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.error || 'Unknown error occurred while creating the brand.',
                        customClass: {
                            confirmButton: 'btn btn-primary'
                        }
                    });
                }
            },
            error: function(xhr) {
                var errorMsg = 'Error creating brand';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
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

    // Edit Brand Event Handler
    $(document).on('click', '.edit-brand', function() {

        var brandCode = $(this).data('brand-code');
        var brandName = $(this).data('brand-name');

        // Populate edit form
        $('#editBrandCode').val(brandCode);
        $('#editBrandName').val(brandName);

        // Show edit modal
        $('#editBrandModal').modal('show');
    });

    // Delete Brand Event Handler
    $(document).on('click', '.delete-brand', function() {
        var brandCode = $(this).data('brand-code');
        var brandName = $(this).data('brand-name');

        Swal.fire({
            title: 'Are you sure?',
            text: "You are about to delete the brand '" + brandName + "'. You won't be able to revert this!",
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
                deleteBrand(brandCode);
            }
        });
    });

    // Edit Brand Form Submission
    $('#editBrandForm').on('submit', function(e) {
        e.preventDefault();

        var brandCode = $('#editBrandCode').val();
        var newBrandName = $('#editBrandName').val().trim();

        if (!newBrandName) {
            Swal.fire({
                icon: 'warning',
                title: 'Validation Error',
                text: 'Brand name is required!',
                customClass: {
                    confirmButton: 'btn btn-primary'
                }
            });
            return;
        }

        updateBrand(brandCode, newBrandName);
    });

    // Function to update brand
    function updateBrand(brandCode, newBrandName) {
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        $.ajax({
            url: '/crossapp/api/brands/update/' + encodeURIComponent(brandCode) + '/',
            type: 'POST',
            data: {
                'brandName': newBrandName,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Brand updated successfully!',
                        customClass: {
                            confirmButton: 'btn btn-success'
                        }
                    });
                    $('#editBrandModal').modal('hide');
                    dt_basic.ajax.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.error || 'Unknown error occurred while updating the brand.',
                        customClass: {
                            confirmButton: 'btn btn-primary'
                        }
                    });
                }
            },
            error: function(xhr) {
                var errorMsg = 'Error updating brand';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
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

    // Function to delete brand
    function deleteBrand(brandCode) {
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        $.ajax({
            url: '/crossapp/api/brands/delete/' + encodeURIComponent(brandCode) + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Deleted!',
                        text: 'Brand has been deleted successfully.',
                        customClass: {
                            confirmButton: 'btn btn-success'
                        }
                    });
                    dt_basic.ajax.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.error || 'Unknown error occurred while deleting the brand.',
                        customClass: {
                            confirmButton: 'btn btn-primary'
                        }
                    });
                }
            },
            error: function(xhr) {
                var errorMsg = 'Error deleting brand';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
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
