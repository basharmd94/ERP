$(document).ready(function() {
  // Initialize date pickers
  $('#from_date, #to_date').datepicker({
    format: 'yyyy-mm-dd',
    autoclose: true,
    todayHighlight: true,
    orientation: 'bottom auto',
    clearBtn: true,
    fullscreen: true,

  });
  // Set default dates (last 30 days)
  var today = new Date();

  $('#to_date').datepicker('setDate', today);
  $('#from_date').datepicker('setDate', today);


  // Initialize Select2 for report type
  const select2 = $('#report_type');
  // Default
  if (select2.length) {
    select2.each(function () {
      var $this = $(this);
      $this.wrap('<div class="position-relative"></div>').select2({
        placeholder: 'Select value',
        dropdownParent: $this.parent(),
        minimumResultsForSearch: Infinity // Disable search for small list
      });
    });
  }

  // Handle form target based on report type
  function updateFormTarget() {
    const reportType = $('#report_type').val();
    const form = $('#dailySalesReportForm');

    if (reportType === 'pdf') {
      form.attr('target', '_blank');
    } else {
      form.removeAttr('target');
    }
  }

  // Set initial target on page load
  updateFormTarget();

  // Update target when report type changes
  $('#report_type').on('change', updateFormTarget);
  // form validation
    $('#dailySalesReportForm').on('submit', function(e) {
    const from = $('#from_date').val();
    const to = $('#to_date').val();
    const format = $('#report_type').val();
    if (format === 'pdf' && from && to) {
      const fromDate = new Date(from);
      const toDate = new Date(to);
      const diffTime = Math.abs(toDate - fromDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // inclusive

      if (diffDays >= 7) {
        e.preventDefault(); // Stop form submission
        Swal.fire({
          icon: 'warning',
          title: 'Large Date Range Detected',
          text: `Your selected date range is ${diffDays} days. PDF export is limited to 7 days for performance. Switching to CSV.`,
          showConfirmButton: true,
          confirmButtonText: 'Export as CSV'
        }).then((result) => {
          if (result.isConfirmed) {
            $('#report_type').val('csv');
            $(this).removeAttr('target'); // ensure no _blank
            this.submit(); // resubmit form
          }
        });
        return false;
      }
    }
  });

  // Handle target for PDF
  function updateFormTarget() {
    const reportType = $('#report_type').val();
    const form = $('#dailySalesReportForm');
    if (reportType === 'pdf') {
      form.attr('target', '_blank');
    } else {
      form.removeAttr('target');
    }
  }

  updateFormTarget();
  $('#report_type').on('change', updateFormTarget);


  // // Initialize Select2 for brands using XCode API
  // $('#brands').xcodeSelect2('brand', {
  //   placeholder: 'Select Brands (Optional)',
  //   allowClear: true,
  //   width: '100%',
  //   multiple: true
  // });



});
