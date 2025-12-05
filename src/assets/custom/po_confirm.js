$(function () {
  function getCsrfToken() {
    var name = 'csrftoken=';
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i].trim();
      if (c.indexOf(name) === 0) return c.substring(name.length, c.length);
    }
    return '';
  }

  $(document).on('click', '.btn-confirm-grn', function () {
    var grn = $(this).data('grn');
    if (!grn) {
      if (typeof Swal !== 'undefined') {
        Swal.fire({ icon: 'error', title: 'Error', text: 'Invalid GRN number' });
      }
      return;
    }

    var confirmAction = function () {
      $.ajax({
        url: '/purchase/po-confirm/' + encodeURIComponent(grn) + '/',
        type: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        success: function (resp) {
          if (resp && resp.success) {
            if (typeof toastr !== 'undefined') {
              toastr.success('GRN confirmed successfully');
            }
            if ($.fn.DataTable.isDataTable('#po-open-list-table')) {
              $('#po-open-list-table').DataTable().ajax.reload(null, false);
            }
          } else {
            var msg = (resp && (resp.message || resp.error)) || 'Confirmation failed';
            if (typeof Swal !== 'undefined') {
              Swal.fire({ icon: 'error', title: 'Error', text: msg });
            }
          }
        },
        error: function (xhr) {
          var msg = 'Confirmation failed';
          try { msg = JSON.parse(xhr.responseText).details || JSON.parse(xhr.responseText).message || msg; } catch (e) {}
          if (typeof Swal !== 'undefined') {
            Swal.fire({ icon: 'error', title: 'Error', text: msg });
          }
        }
      });
    };

    if (typeof Swal !== 'undefined') {
      Swal.fire({
        title: 'Confirm GRN?',
        text: 'This will post receipt entries into inventory.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, confirm',
        cancelButtonText: 'Cancel'
      }).then(function (result) {
        if (result.isConfirmed) confirmAction();
      });
    } else {
      if (confirm('Confirm GRN ' + grn + '?')) confirmAction();
    }
  });
});

