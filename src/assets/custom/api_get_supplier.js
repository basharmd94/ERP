
$(document).ready(function(){
  const $supplier = $('#supplierSelect');

  // Wrap the supplier element to fix scrollbar issue
  $supplier.wrap('<div class="position-relative"></div>');

  $supplier.select2({
    placeholder: 'Search suppliers...',
    allowClear: true,
    dropdownParent: $supplier.parent(), // Fix for scrollbar issue
    ajax: {
      url: '/api/get-supplier/',
      dataType: 'json',
      delay: 250,
      data: params => ({q: params.term || '', page: params.page || 1}),
      processResults: (data, params) => ({
        results: data.results || [],
        pagination: {more: data.pagination?.more || false}
      })
    },
    templateResult: function(item) {
      if (item.loading) return item.text;
      // Show both supplier code and name in dropdown for better UX
      return $('<div>' + item.text + ' -- ' + (item.xshort || '') + '</div>');
    },
    templateSelection: function(item) {
      // Show only supplier code when selected
      return item.text || item.id;
    }
  });


});
