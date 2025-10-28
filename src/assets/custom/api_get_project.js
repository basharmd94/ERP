$(document).ready(function(){
  const $project = $('#project');

  // Load all warehouses
  $.ajax({
    url: '/api/get-project/',
    type: 'GET',
    dataType: 'json',
    success: function(data) {
      // Add project options
      if (data.results && data.results.length > 0) {
        data.results.forEach(function(project) {
          $project.append(new Option(project.text, project.id));
        });
        
        // Set the first project as default
        $project.val(data.results[0].id);
      }

      // Wrap the project element to fix scrollbar issue
      $project.wrap('<div class="position-relative"></div>');

      // Initialize Select2
      $project.select2({
        placeholder: 'Select project...',
        allowClear: true,
        dropdownParent: $project.parent() // Fix for scrollbar issue
      });
      
      // Trigger change event to ensure the default value is properly set
      if (data.results && data.results.length > 0) {
        $project.trigger('change');
      }


    }
  });
});
