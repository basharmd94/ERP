$(document).ready(function(){
  const $itemSearch = $('#avg-item-search');

  // Wrap the item search element to fix scrollbar issue
  $itemSearch.wrap('<div class="position-relative"></div>');

  $itemSearch.select2({
    placeholder: 'Search items by code, description, or barcode...',
    allowClear: true,
    minimumInputLength: 2,
    dropdownParent: $itemSearch.parent(), // Fix for scrollbar issue
    ajax: {
      url: '/api/avg-item-price/',
      dataType: 'json',
      delay: 250,
      data: params => ({search: params.term || '', page: params.page || 1}),
      processResults: (data, params) => ({
        results: data.results || [],
        pagination: {more: data.pagination?.more || false}
      })
    },
    templateResult: function(item) {
      if (item.loading) return item.text;
      const avgPrice = item.avg_price || 0;
      const stock = item.stock || 0;
      return $(`
        <div>
          <div class="fw-bold">${item.text}</div>
          <div class="small text-muted">
            Avg Price: ৳${parseFloat(avgPrice).toFixed(2)} | Stock: ${parseFloat(stock).toFixed(2)} | Barcode: ${item.xbarcode || 'N/A'}
          </div>
        </div>
      `);
    }
  });

  // Handle item selection - directly add to cart
  $itemSearch.on('select2:select', function (e) {
    const item = e.params.data;

    // Directly add item to cart
    if (typeof addToCart === 'function') {
      addToCart(item);
    }

    // Clear the selection
    $(this).val(null).trigger('change');
  });
});
