
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
    }
  });
});
