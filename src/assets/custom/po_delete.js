/**
 * Purchase Order Deletion Module
 *
 * Provides a safe, user-confirmed workflow for deleting Purchase Orders and
 * all strongly related records via the backend endpoint. The UX prioritizes
 * clarity, irreversible action warnings, and resilience (DataTable reload
 * when present, full page reload fallback otherwise).
 */
$(document).ready(function() {
  // Entry point exposed globally so action menus can call deletePO('PO123') directly.
  window.deletePO = function(poNumber) {
    if (!poNumber) {
      toastr.error('PO Number is required for deletion');
      return;
    }

    // Confirm destructive action with detailed context to prevent accidental deletions.
    const title = 'Confirm Deletion';
    const html = `Are you sure you want to delete Purchase Order <strong>${poNumber}</strong>?<br><br>This action cannot be undone and will remove all related records including GRN and GL entries if posted.`;

    Swal.fire({
      title: title,
      html: html,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'Cancel',
      focusCancel: true
    }).then((result) => {
      if (!result.isConfirmed) return;
      performDelete(poNumber);
    });
  };

  // Resolve CSRF token from standard hidden input or meta tag to satisfy Django CSRF protection.
  function getCsrfToken() {
    // Prefer standard hidden input or meta tag; fall back to cookie 'csrftoken' for AJAX
    const inputToken = $('[name=csrfmiddlewaretoken]').val();
    if (inputToken && inputToken.length > 0) return inputToken;

    const metaToken = $('meta[name=csrf-token]').attr('content');
    if (metaToken && metaToken.length > 0) return metaToken;

    const cookieToken = (function getCookie(name) {
      const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
      return match ? decodeURIComponent(match[2]) : '';
    })('csrftoken');

    return cookieToken || '';
  }

  // Perform the AJAX deletion request with a non-dismissible loading state and robust UI updates.
  function performDelete(poNumber) {
    const loadingToast = toastr.info('Deleting purchase order...', 'Please wait', {
      timeOut: 0,
      extendedTimeOut: 0,
      closeButton: false,
      tapToDismiss: false
    });

    const csrfToken = getCsrfToken();
    if (!csrfToken || csrfToken.length < 32) {
      toastr.error('CSRF token missing. Please refresh the page and try again.');
      toastr.clear(loadingToast);
      return;
    }

    $.ajax({
      url: `/purchase/po-delete/${poNumber}/`,
      type: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      success: function(response) {
        toastr.clear(loadingToast);
        if (response && response.success) {
          toastr.success(response.message || 'Purchase order deleted successfully');
          // Prefer DataTable redraw when available to avoid a full page refresh.
          if ($.fn.DataTable && $('#po-open-list-table').length && $('#po-open-list-table').DataTable) {
            try {
              $('#po-open-list-table').DataTable().ajax.reload(null, false);
            } catch (e) {
              window.location.reload();
            }
          } else {
            window.location.reload();
          }
        } else {
          toastr.error((response && response.message) || 'Failed to delete purchase order');
        }
      },
      error: function(xhr, status, error) {
        toastr.clear(loadingToast);
        let message = 'Error deleting purchase order';
        // Server-provided messages are preferred; fall back to status-aware defaults.
        if (xhr.responseJSON && xhr.responseJSON.message) {
          message = xhr.responseJSON.message;
        } else if (xhr.status === 404) {
          message = 'Purchase order not found';
        } else if (xhr.status === 401) {
          message = 'Session expired. Please login again';
          setTimeout(() => window.location.href = '/login/', 1500);
        }
        toastr.error(message);
        // Capture diagnostics to assist in field debugging without exposing sensitive data to users.
        console.error('Delete PO error:', { status: xhr.status, error: error, responseText: xhr.responseText });
      }
    });
  }
});
