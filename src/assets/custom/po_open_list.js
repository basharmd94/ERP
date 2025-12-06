$(function () {
  let poTable;

  function initializeDataTable() {
    if ($.fn.DataTable.isDataTable('#po-open-list-table')) {
      $('#po-open-list-table').DataTable().destroy();
    }

    poTable = $('#po-open-list-table').DataTable({
      processing: true,
      serverSide: true,
      ajax: {
        url: '/purchase/po-open-list/',
        type: 'GET',
        error: function (xhr, error) {
          showError('Failed to load purchase orders. Please try again.');
        }
      },
      columns: [
        {
          data: 0,
          title: 'Date',
          orderable: true,
          searchable: true,
          render: function (data, type) {
            if (type === 'display' && data) {
              return '<span class="badge rounded-pill bg-label-dark">' + data + '</span>';
            }
            return data || '';
          }
        },
        {
          data: 1,
          title: 'PO Number',
          orderable: true,
          searchable: true,
          render: function (data, type) {
            if (type === 'display' && data) {
              return '<strong class="text-primary">' + data + '</strong>';
            }
            return data || '';
          }
        },
        {
          data: 2,
          title: 'GRN Number',
          orderable: true,
          searchable: true,
          render: function (data, type) {
            if (type === 'display' && data) {
              return '<strong class="text-info">' + data + '</strong>';
            }
            return data || '';
          }
        },
        {
          data: 3,
          title: 'Supplier',
          orderable: true,
          searchable: true,
          render: function (data, type) {
            if (type === 'display' && data) {
              return '<span class="badge rounded-pill bg-label-primary">' + data + '</span>';
            }
            return data || '';
          }
        },
        {
          data: 4,
          title: 'Supplier Name',
          orderable: true,
          searchable: true,
          render: function (data, type) {
            if (type === 'display' && data) {
              return '<span class="text-muted">' + data + '</span>';
            }
            return data || '';
          }
        },
        {
          data: 5,
          title: 'Status',
          orderable: true,
          searchable: true,
          render: function (data, type) {
            if (type === 'display' && data) {
              var badgeClass = 'bg-secondary';
              if (data === '1-Open') badgeClass = 'bg-warning';
              if (data === '5-Confirmed') badgeClass = 'badge rounded-pill bg-label-success';
              return '<span class="badge ' + badgeClass + '">' + data + '</span>';
            }
            return data || '';
          }
        },
        {
          data: 6,
          title: 'Confirm',
          orderable: false,
          searchable: false,
          className: 'text-center',
          width: '100px',
          render: function (data, type, row) {
            if (type === 'display' && data) {
              var grnNumber = data;
              return '<button type="button" class="btn btn-sm btn-primary btn-confirm-grn" data-grn="' + grnNumber + '" title="Confirm">Confirm</button>';
            }
            return '';
          }
        },
        {
          data: 7,
          title: 'Quick Act',
          orderable: false,
          searchable: false,
          className: 'text-center',
          width: '120px',
          render: function (data, type, row) {
            if (type === 'display' && data) {
              var poNumber = data;
              var grnNumber = row[2];
              return (
                '<div class="btn-group" role="group" aria-label="Quick Actions">' +

                (grnNumber ? '<a href="/purchase/po-grn-detail/' + grnNumber + '/" target="_blank" class="btn btn-sm btn-outline-primary" title="GRN Detail"><i class="tf-icons ti ti-eye"></i></a>' : '') +
                '<a href="/purchase/po-update/' + poNumber + '/" class="btn btn-sm btn-outline-warning" title="Edit">' +
                '<i class="tf-icons ti ti-edit"></i></a>' +
                '<a href="/purchase/po-req-print/' + poNumber + '/" target="_blank" class="btn btn-sm btn-outline-info" title="Print Requisition">' +
                '<i class="tf-icons ti ti-printer"></i></a>' +
                (grnNumber ? '<a href="/purchase/po-grn-print/' + grnNumber + '/" target="_blank" class="btn btn-sm btn-outline-info" title="Print GRN"><i class="tf-icons ti ti-printer"></i></a>' : '') +
                (grnNumber ? '<a href="/purchase/po-export-excel/' + grnNumber + '/" class="btn btn-sm btn-outline-success" title="Export Excel">' : '') +
                '<i class="tf-icons ti ti-file-spreadsheet"></i></a>' +
                '</div>'
              );
            }
            return '';
          }
        },
        {
          data: 8,
          title: 'Actions',
          orderable: false,
          searchable: false,
          className: 'text-center',
          render: function (data, type, row) {
            if (type === 'display' && data) {
              var poNumber = data;
              var grnNumber = row[2];
              return (
                '<div class="dropdown">' +
                '<button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">' +
                '<i class="tf-icons ti ti-dots-vertical"></i></button>' +
                '<ul class="dropdown-menu">' +

                (grnNumber ? '<li><a class="dropdown-item" href="/purchase/po-grn-detail/' + grnNumber + '/"><i class="tf-icons ti ti-eye me-1"></i>View GRN</a></li>' : '') +
                '<li><a class="dropdown-item" href="/purchase/po-update/' + poNumber + '/"><i class="tf-icons ti ti-edit me-1"></i>Edit</a></li>' +
                '<li><a class="dropdown-item" href="/purchase/po-req-print/' + poNumber + '/" target="_blank"><i class="tf-icons ti ti-printer me-1"></i>Print Requisition</a></li>' +
                (grnNumber ? '<li><a class="dropdown-item" href="/purchase/po-grn-print/' + grnNumber + '/" target="_blank"><i class="tf-icons ti ti-printer me-1"></i>Print GRN</a></li>' : '') +
                (grnNumber ? '<li><a class="dropdown-item" href="/purchase/po-export-excel/' + grnNumber + '/"><i class="tf-icons ti ti-file-spreadsheet me-1"></i>Export Excel</a></li>' : '') +
                '<li><hr class="dropdown-divider"></li>' +
                '<li><a class="dropdown-item text-danger" href="#" onclick="deletePO(\'' + poNumber + '\')"><i class="tf-icons ti ti-trash me-1"></i>Delete</a></li>' +
                '</ul>' +
                '</div>'
              );
            }
            return '';
          }
        }
      ],
      order: [[0, 'desc']],
      pageLength: 10,
      lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
      dom:
        '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>' +
        '<"table-responsive"t>' +
        '<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      language: {
        processing:
          '<div class="d-flex justify-content-center align-items-center">' +
          '<div class="spinner-border text-primary me-2" role="status">' +
          '<span class="visually-hidden">Loading...</span></div>' +
          'Loading purchase orders...</div>',
        emptyTable:
          '<div class="text-center py-4">' +
          '<i class="tf-icons ti ti-arrow-back-up ti-lg text-muted mb-2 d-block"></i>' +
          '<div class="text-muted">No purchase orders found</div>' +
          '<small class="text-muted">Try adjusting your search criteria</small></div>',
        zeroRecords:
          '<div class="text-center py-4">' +
          '<i class="tf-icons ti ti-search-off ti-lg text-muted mb-2 d-block"></i>' +
          '<div class="text-muted">No matching records found</div>' +
          '<small class="text-muted">Try different search terms</small></div>',
        search: '<i class="tf-icons ti ti-search me-1"></i>',
        searchPlaceholder: 'Search purchase orders...',
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
      drawCallback: function () {
        $('[data-bs-toggle="tooltip"]').tooltip();
      }
    });
  }

  $(document).ready(function () {
    initializeDataTable();
  });

  function showError(message) {
    if (typeof Swal !== 'undefined') {
      Swal.fire({ icon: 'error', title: 'Error', text: message, confirmButtonText: 'OK' });
    } else {
      alert(message);
    }
  }
});

function deletePO(poNumber) {
  if (typeof Swal !== 'undefined') {
    Swal.fire({
      title: 'Are you sure?',
      text: 'Delete functionality will be implemented later.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes',
      cancelButtonText: 'Cancel'
    });
  }
}
