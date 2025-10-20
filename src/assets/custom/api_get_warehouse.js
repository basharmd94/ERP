$(document).ready(function(){
  const $warehouse = $('#warehouse');
  
  // Load all warehouses
  $.ajax({
    url: '/api/get-warehouse/',
    type: 'GET',
    dataType: 'json',
    success: function(data) {
      // Add warehouse options
      if (data.results && data.results.length > 0) {
        data.results.forEach(function(warehouse) {
          $warehouse.append(new Option(warehouse.text, warehouse.id));
        });
      }
      
      // Wrap the warehouse element to fix scrollbar issue
      $warehouse.wrap('<div class="position-relative"></div>');
      
      // Initialize Select2
      $warehouse.select2({
        placeholder: 'Select warehouse...',
        allowClear: true,
        dropdownParent: $warehouse.parent() // Fix for scrollbar issue
      });
    }
  });
});