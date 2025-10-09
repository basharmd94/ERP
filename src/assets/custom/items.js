$(function () {
  var dt_ajax_table = $('.datatables-ajax');
  if (dt_ajax_table.length) {
    dt_ajax_table.DataTable({
      processing: true,
      serverSide: true,
      ajax: {
        url: '/crossapp/api/items/',
        type: 'GET',
        dataSrc: 'items',
        error: function (xhr, error, thrown) {
          console.error('Error loading items:', error);
        }
      },
      columns: [
        { data: 'xitem', title: 'Item Code' },
        { data: 'xdesc', title: 'Description' },
        { data: 'xunitstk', title: 'Stock Unit' },
        { data: 'xgitem', title: 'Item Group' },
        { data: 'xwh', title: 'Warehouse' },
        {  data: 'xstdcost',  title: 'Standard Cost',
          render: function(data) {
            return data ? data : '0.00';
          }
        },
        {  data: 'xstdprice',  title: 'Standard Price',
          render: function(data) {
            return data ? data : '0.00';
          }
        },
        {
          // Actions column
          title: 'Actions',
          orderable: false,
          data: 'xitem',
          render: function (data, type, row) {
            return (
              '<div class="d-inline-block">' +
              '<a href="javascript:;" class="btn btn-sm btn-icon dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical"></i></a>' +
              '<div class="dropdown-menu dropdown-menu-end m-0">' +
              '<a href="javascript:;" class="dropdown-item"><i class="ti ti-eye me-1"></i>Details</a>' +
              '<a href="javascript:;" class="dropdown-item"><i class="ti ti-edit me-1"></i>Edit</a>' +
              '<a href="javascript:;" class="dropdown-item text-danger delete-item" data-item-code="' + data + '" data-item-desc="' + (row.xdesc || data) + '"><i class="ti ti-trash me-1"></i>Delete</a>' +
              '</div>' +
              '</div>'
            );
          }
        }
      ],
      dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>><"table-responsive"t><"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      language: {
        processing: "Loading items...",
        emptyTable: "No items found",
        zeroRecords: "No matching items found"
      }
    });
  }

  // Delete item event handler
  $(document).on('click', '.delete-item', function() {
    var itemCode = $(this).data('item-code');
    var itemDesc = $(this).data('item-desc');

    // SweetAlert2 confirmation dialog
    Swal.fire({
      title: 'Are you sure?',
      text: `You are about to delete item: ${itemDesc}`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'No, cancel',
      customClass: {
        confirmButton: 'btn btn-danger me-3',
        cancelButton: 'btn btn-label-secondary'
      },
      buttonsStyling: false
    }).then(function (result) {
      if (result.isConfirmed) {
        deleteItem(itemCode);
      }
    });
  });

  // Function to delete an item
  function deleteItem(itemCode) {
    $.ajax({
      url: `/crossapp/api/items/delete/${itemCode}/`,
      type: 'POST',
      success: function(response) {
        // Show success message with SweetAlert2
        Swal.fire({
          icon: 'success',
          title: 'Deleted!',
          text: 'Item has been deleted successfully.',
          customClass: {
            confirmButton: 'btn btn-success'
          },
          buttonsStyling: false
        });

        // Reload the DataTable
        $('.datatables-ajax').DataTable().ajax.reload();
      },
      error: function(xhr) {
        // Show error message with SweetAlert2
        var errorMessage = 'An error occurred while deleting the item.';
        if (xhr.responseJSON && xhr.responseJSON.error) {
          errorMessage = xhr.responseJSON.error;
        }

        Swal.fire({
          icon: 'error',
          title: 'Error!',
          text: errorMessage,
          customClass: {
            confirmButton: 'btn btn-primary'
          },
          buttonsStyling: false
        });
      }
    });
  }
});
