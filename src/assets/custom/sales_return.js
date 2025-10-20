// Sales Return Cart Management
$(document).ready(function() {
    // Cart array to store items
    window.cartItems = [];
    window.cartCounter = 0;
    window.cartDataTable = null;

    // Initialize DataTable for cart
    function initCartDataTable() {
        if (window.cartDataTable) {
            window.cartDataTable.destroy();
        }

        window.cartDataTable = $('#cart-datatable').DataTable({
            data: [],
            // footer pagination make false
            paging: false,
            // footer x of y show false
            info: false,
            // searching false
            searching: false,
            columns: [
                {
                    title: 'Item Name',
                    data: null,
                    width: '25%',
                    render: function(data, type, row) {
                        const description = row.xdesc || 'No Description';
                        const truncatedDesc = description.length > 30 ? description.substring(0, 30) + '...' : description;
                        return `
                            <div class="fw-bold text-truncate" style="font-size: 0.875rem;">${row.xitem}</div>
                            <small class="text-muted text-truncate d-block" title="${description}" style="font-size: 0.75rem;">${truncatedDesc}</small>
                        `;
                    }
                },
                {
                    title: 'Stock',
                    data: null,
                    width: '15%',
                    render: function(data, type, row) {
                        return `
                            <div class="text-center">
                                <span class="text-info fw-bold" style="font-size: 0.875rem;">${formatNumber(row.stock)}</span>
                                <br><small class="text-muted" style="font-size: 0.7rem;">${row.xunitstk || 'PCS'}</small>
                            </div>
                        `;
                    }
                },
                {
                    title: 'Price',
                    data: null,
                    width: '15%',
                    render: function(data, type, row) {
                        return `
                            <div class="text-end">
                                <div style="font-size: 0.875rem;">৳${formatNumber(row.avg_price)}</div>
                                <small class="text-muted" style="font-size: 0.7rem;">Std: ৳${formatNumber(row.xstdprice)}</small>
                            </div>
                        `;
                    }
                },
                {
                    title: 'Qty',
                    data: 'quantity',
                    width: '15%',
                    render: function(data, type, row) {
                        return `
                            <input type="number"
                                   class="form-control form-control-sm quantity-input"
                                   value="${data}"
                                   min="0.01"
                                   step="0.01"
                                   data-cart-id="${row.cartId}"
                                   style="width: 70px; font-size: 0.875rem;">
                        `;
                    }
                },
                {
                    title: 'Subtotal',
                    data: null,
                    width: '15%',
                    render: function(data, type, row) {
                        const subtotal = row.avg_price * row.quantity;
                        return `<div class="fw-bold text-success text-center" style="font-size: 0.875rem;">৳${formatNumber(subtotal)}</div>`;
                    }
                },
                {
                    title: 'Action',
                    data: null,
                    width: '10%',
                    orderable: false,
                    render: function(data, type, row) {
                        return `
                            <button type="button"
                                    class="btn btn-sm btn-outline-danger remove-item"
                                    data-cart-id="${row.cartId}"
                                    title="Remove item"
                                    style="padding: 0.25rem 0.5rem;">
                                <i class="fas fa-trash" style="font-size: 0.75rem;"></i>
                            </button>
                        `;
                    }
                }
            ],
            responsive: true,
            pageLength: 10,
            lengthMenu: [[5, 10, 25, 50], [5, 10, 25, 50]],
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            language: {
                search: "Search cart:",
                lengthMenu: "Show _MENU_ items",
                info: "Showing _START_ to _END_ of _TOTAL_ items",
                emptyTable: "No items in cart"
            },
            drawCallback: function() {
                // Make table rows more compact
                $('#cart-datatable tbody tr').css({
                    'height': '45px',
                    'line-height': '1.2'
                });
                $('#cart-datatable tbody td').css({
                    'padding': '0.5rem 0.75rem',
                    'vertical-align': 'middle'
                });
            }
        });

        // Handle quantity change
        $('#cart-datatable').on('change', '.quantity-input', function() {
            const cartId = parseInt($(this).data('cart-id'));
            const newQuantity = parseFloat($(this).val());
            updateQuantity(cartId, newQuantity);
        });

        // Handle remove item
        $('#cart-datatable').on('click', '.remove-item', function() {
            const cartId = parseInt($(this).data('cart-id'));
            removeFromCart(cartId);
        });
    }

    // Add item to cart function
    window.addToCart = function(item) {
        // Check if item already exists in cart
        const existingItemIndex = cartItems.findIndex(cartItem => cartItem.xitem === item.xitem);

        if (existingItemIndex !== -1) {
            // Item exists, increase quantity
            cartItems[existingItemIndex].quantity += 1;
        } else {
            // New item, add to cart
            const cartItem = {
                ...item,
                quantity: 1,
                cartId: ++cartCounter
            };
            cartItems.push(cartItem);
        }

        // Refresh DataTable with updated data
        refreshCartDataTable();
        updateCartTotals();
        showCartSection();

        // Show success message
        showToast('Item added to cart successfully!', 'success');

        // Clear the search selection
        $('#avg-item-search').val(null).trigger('change');
    };

    // Remove item from cart
    window.removeFromCart = function(cartId) {
        const itemIndex = cartItems.findIndex(item => item.cartId === cartId);
        if (itemIndex !== -1) {
            const removedItem = cartItems.splice(itemIndex, 1)[0];
            refreshCartDataTable();
            updateCartTotals();
            toggleCartSection();
            showToast(`${removedItem.xitem} removed from cart`, 'info');
        }
    };

    // Update quantity
    window.updateQuantity = function(cartId, newQuantity) {
        if (newQuantity <= 0) {
            removeFromCart(cartId);
            return;
        }

        const itemIndex = cartItems.findIndex(item => item.cartId === cartId);
        if (itemIndex !== -1) {
            cartItems[itemIndex].quantity = newQuantity;
            refreshCartDataTable();
            updateCartTotals();
        }
    }

    // Refresh DataTable with current cart data
    function refreshCartDataTable() {
        if (window.cartDataTable) {
            window.cartDataTable.clear().rows.add(cartItems).draw();
        }
    }



    // Update cart totals
    function updateCartTotals() {
        let totalItems = 0;
        let totalAmount = 0;

        cartItems.forEach(item => {
            totalItems += item.quantity;
            totalAmount += item.avg_price * item.quantity;
        });

        $('#cart-total-items').text(formatNumber(totalItems));
        $('#cart-total-amount').text(`৳${formatNumber(totalAmount)}`);
        $('#cart-items-count').text(cartItems.length);
    }

    // Show/Hide cart section
    function showCartSection() {
        $('#cart-section').show();
        $('#empty-cart-message').hide();
    }

    function hideCartSection() {
        $('#cart-section').hide();
        $('#empty-cart-message').show();
    }

    // Toggle cart section visibility
    function toggleCartSection() {
        if (cartItems.length > 0) {
            showCartSection();
            $('#empty-cart-message').hide();
        } else {
            hideCartSection();
            $('#empty-cart-message').show();
        }
    }

    // Clear entire cart
    window.clearCart = function() {
        if (cartItems.length === 0) {
            showToast('Cart is already empty', 'info');
            return;
        }

        if (confirm('Are you sure you want to clear the entire cart?')) {
            cartItems = [];
            refreshCartDataTable();
            updateCartTotals();
            toggleCartSection();
            showToast('Cart cleared successfully', 'success');
        }
    };

    // Initialize DataTable when document is ready
    initCartDataTable();

    // Format number helper
    function formatNumber(num) {
        return parseFloat(num || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Toast notification helper
    function showToast(message, type = 'info') {
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'bg-success' :
                       type === 'error' ? 'bg-danger' :
                       type === 'warning' ? 'bg-warning' : 'bg-info';

        const toast = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        // Add to toast container or create one
        if ($('#toast-container').length === 0) {
            $('body').append('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
        }

        $('#toast-container').append(toast);

        // Initialize and show toast
        const toastElement = new bootstrap.Toast(document.getElementById(toastId));
        toastElement.show();

        // Remove toast element after it's hidden
        $(`#${toastId}`).on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }
});
