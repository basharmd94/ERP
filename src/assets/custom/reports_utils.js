$(document).ready(function() {
  // Initialize date pickers
  $('#from_date, #to_date').datepicker({
    format: 'yyyy-mm-dd',
    autoclose: true,
    todayHighlight: true,
    orientation: 'bottom auto',
    clearBtn: true
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



  // // Initialize Select2 for brands using XCode API
  // $('#brands').xcodeSelect2('brand', {
  //   placeholder: 'Select Brands (Optional)',
  //   allowClear: true,
  //   width: '100%',
  //   multiple: true
  // });



});
