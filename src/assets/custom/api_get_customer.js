
$(document).ready(function(){
  const $customer = $('#customer');

  // Wrap the customer element to fix scrollbar issue
  $customer.wrap('<div class="position-relative"></div>');

  $customer.select2({
    placeholder: 'Search customers...',
    allowClear: true,
    dropdownParent: $customer.parent(), // Fix for scrollbar issue
    ajax: {
      url: '/api/get-customer/',
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
      // Show both customer code and name in dropdown for better UX
      return $('<div>' + item.text + ' -- ' + (item.xshort || '') + '</div>');
    },
    templateSelection: function(item) {
      // Show only customer code when selected
      return item.text || item.id;
    }
  });


});
