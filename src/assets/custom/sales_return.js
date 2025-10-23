// Sales Return Cart Management
$(document).ready(function() {
    // Cart array to store items
    window.cartItems = [];
    window.cartCounter = 0;
    window.cartDataTable = null;
    window.currentZid = null;

    // Initialize Bootstrap Date Pickers with YYYY-MM-DD format
    $('#transaction-date, #invoice-date').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true,
        clearBtn: true,
        orientation: 'bottom auto',
        container: 'body'
    });

    // Set today's date as default for both date pickers
    var today = new Date();
    $('#transaction-date, #invoice-date').datepicker('setDate', today);

    // LocalStorage functionality with ZID-based keys
    window.salesReturnStorage = {
        // Get current ZID from server
        getCurrentZid: function() {
            return new Promise((resolve, reject) => {
                $.ajax({
                    url: '/api/get-current-zid/',
                    type: 'GET',
                    cache: false,
                    data: { '_': new Date().getTime() }, // Cache busting
                    success: function(response) {
                        console.log('ZID API Response:', response);
                        if (response.success) {
                            window.currentZid = response.zid;
                            console.log('Current ZID loaded:', response.zid);
                            resolve(response.zid);
                        } else {
                            console.error('ZID API failed:', response.message);
                            if (response.debug_info) {
                                console.error('Debug info:', response.debug_info);
                            }
                            reject(response.message || 'Failed to get ZID');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('ZID API Error:', {
                            status: xhr.status,
                            statusText: xhr.statusText,
                            responseText: xhr.responseText,
                            error: error
                        });
                        reject('Error getting ZID: ' + error);
                    }
                });
            });
        },

        // Generate storage key with ZID
        getStorageKey: function(key) {
            return `sales_return_${window.currentZid}_${key}`;
        },

        // Save cart data to localStorage
        saveCartData: function() {
            if (!window.currentZid) return;

            const cartData = {
                items: window.cartItems,
                counter: window.cartCounter,
                timestamp: new Date().toISOString(),
                // Save form data as well
                formData: {
                    invoice_date: $('#invoice-date').val() || '',
                    receive_type: $('#receive-type').val() || '0',
                    supplier_select: $('#supplierSelect').val() || '',
                    warehouse: $('#warehouse').val() || '',
                    notes: $('#notes').val() || ''
                }
            };

            try {
                localStorage.setItem(this.getStorageKey('cart'), JSON.stringify(cartData));
                console.log('Cart data saved to localStorage for ZID:', window.currentZid);
            } catch (e) {
                console.error('Error saving to localStorage:', e);
            }
        },

        // Load cart data from localStorage
        loadCartData: function() {
            if (!window.currentZid) return null;

            try {
                const savedData = localStorage.getItem(this.getStorageKey('cart'));
                if (savedData) {
                    const cartData = JSON.parse(savedData);
                    console.log('Cart data loaded from localStorage for ZID:', window.currentZid);
                    return cartData;
                }
            } catch (e) {
                console.error('Error loading from localStorage:', e);
            }
            return null;
        },

        // Clear cart data from localStorage
        clearCartData: function() {
            if (!window.currentZid) return;

            try {
                localStorage.removeItem(this.getStorageKey('cart'));
                console.log('Cart data cleared from localStorage for ZID:', window.currentZid);
            } catch (e) {
                console.error('Error clearing localStorage:', e);
            }
        },

        // Auto-save function (debounced)
        autoSave: function() {
            clearTimeout(window.autoSaveTimeout);
            window.autoSaveTimeout = setTimeout(() => {
                this.saveCartData();
            }, 500); // Save after 500ms of inactivity
        }
    };

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
            // fixed header
            fixedHeader: true,
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
                    title: 'Mkt Price',
                    data: null,
                    width: '15%',
                    render: function(data, type, row) {
                        const mktPrice = row.mkt_price || row.avg_price;
                        return `
                            <input type="number"
                                   class="form-control form-control-sm mkt-price-input"
                                   value="${mktPrice}"
                                   min="0.01"
                                   step="0.01"
                                   data-cart-id="${row.cartId}"
                                   style="width: 80px; font-size: 0.875rem;"
                                   placeholder="Price">
                        `;
                    }
                },
                {
                    title: 'Subtotal',
                    data: null,
                    width: '15%',
                    render: function(data, type, row) {
                        const mktPrice = row.mkt_price || row.avg_price;
                        const subtotal = mktPrice * row.quantity;
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

        // Handle market price change
        $('#cart-datatable').on('change', '.mkt-price-input', function() {
            const cartId = parseInt($(this).data('cart-id'));
            const newMktPrice = parseFloat($(this).val());
            updateMktPrice(cartId, newMktPrice);
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
        let targetCartId;

        if (existingItemIndex !== -1) {
            // Item exists, increase quantity
            cartItems[existingItemIndex].quantity += 1;
            targetCartId = cartItems[existingItemIndex].cartId;
        } else {
            // New item, add to cart
            const cartItem = {
                ...item,
                quantity: 1,
                mkt_price: item.avg_price, // Initialize mkt_price with avg_price
                cartId: ++cartCounter
            };
            cartItems.push(cartItem);
            targetCartId = cartItem.cartId;
        }

        // Refresh DataTable with updated data
        refreshCartDataTable();
        updateCartTotals();
        showCartSection();

        // Auto-focus and select quantity input for the added/updated item
        setTimeout(() => {
            const quantityInput = $(`.quantity-input[data-cart-id="${targetCartId}"]`);
            if (quantityInput.length > 0) {
                quantityInput.focus().select();

                // Scroll to the input if it's not visible
                const cartTable = $('.card-datatable');
                const inputOffset = quantityInput.offset();
                const tableOffset = cartTable.offset();

                if (inputOffset && tableOffset) {
                    const relativeTop = inputOffset.top - tableOffset.top;
                    const tableHeight = cartTable.height();

                    // If input is not fully visible, scroll to it
                    if (relativeTop < 0 || relativeTop > tableHeight - 50) {
                        cartTable.animate({
                            scrollTop: cartTable.scrollTop() + relativeTop - (tableHeight / 2)
                        }, 300);
                    }
                }
            }
        }, 100); // Small delay to ensure DOM is updated

        // Auto-save to localStorage
        if (window.salesReturnStorage) {
            window.salesReturnStorage.autoSave();
        }

        // Show success message
        toastr.success('Item added to cart successfully!');

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

            // Auto-save to localStorage
            if (window.salesReturnStorage) {
                window.salesReturnStorage.autoSave();
            }

            toastr.info(`${removedItem.xitem} removed from cart`);
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

            // Auto-save to localStorage
            if (window.salesReturnStorage) {
                window.salesReturnStorage.autoSave();
            }
        }
    }

    // Update market price
    window.updateMktPrice = function(cartId, newMktPrice) {
        if (newMktPrice <= 0) {
            return; // Don't allow zero or negative prices
        }

        const itemIndex = cartItems.findIndex(item => item.cartId === cartId);
        if (itemIndex !== -1) {
            cartItems[itemIndex].mkt_price = newMktPrice;
            refreshCartDataTable();
            updateCartTotals();

            // Auto-save to localStorage
            if (window.salesReturnStorage) {
                window.salesReturnStorage.autoSave();
            }
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
            const mktPrice = item.mkt_price || item.avg_price;
            totalAmount += mktPrice * item.quantity;
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
            toastr.info('Cart is already empty');
            return;
        }

        if (confirm('Are you sure you want to clear the entire cart?')) {
            cartItems = [];
            refreshCartDataTable();
            updateCartTotals();
            toggleCartSection();

            // Clear localStorage data
            if (window.salesReturnStorage) {
                window.salesReturnStorage.clearCartData();
            }

            toastr.success('Cart cleared successfully');
        }
    };

    // Initialize DataTable when document is ready
    initCartDataTable();

    // Function to restore supplier selection with proper AJAX loading
    function restoreSupplierSelection(supplierCode) {
        console.log('Restoring supplier selection:', supplierCode);

        // Make AJAX call to get supplier details
        $.ajax({
            url: '/api/get-supplier/',
            type: 'GET',
            dataType: 'json',
            data: { q: supplierCode },
            success: function(response) {
                console.log('Supplier search response:', response);

                if (response.results && response.results.length > 0) {
                    const supplier = response.results.find(s => s.text === supplierCode);
                    if (supplier) {
                        // Create option and add to select
                        const option = new Option(supplier.text, supplier.id, true, true);
                        $('#supplierSelect').append(option);

                        // Trigger change to update Select2
                        $('#supplierSelect').trigger('change');

                        console.log('Supplier restored successfully:', supplier.text);
                    } else {
                        console.log('Supplier not found in results:', supplierCode);
                    }
                } else {
                    console.log('No suppliers found for code:', supplierCode);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading supplier:', error);
            }
        });
    }

    // Initialize localStorage functionality
    function initializeLocalStorage() {
        console.log('Initializing localStorage functionality...');

        window.salesReturnStorage.getCurrentZid()
            .then(function(zid) {
                console.log('Successfully loaded ZID:', zid);

                // Load saved cart data
                const savedData = window.salesReturnStorage.loadCartData();
                if (savedData) {
                    console.log('Found saved data:', savedData);

                    // Restore cart items
                    window.cartItems = savedData.items || [];
                    window.cartCounter = savedData.counter || 0;

                    // Restore form data
                    if (savedData.formData) {
                        $('#invoice-date').val(savedData.formData.invoice_date || '');
                        $('#receive-type').val(savedData.formData.receive_type || '0').trigger('change');

                        // Restore supplier with proper AJAX loading
                        if (savedData.formData.supplier_select) {
                            restoreSupplierSelection(savedData.formData.supplier_select);
                        }

                        $('#warehouse').val(savedData.formData.warehouse || '').trigger('change');
                        $('#notes').val(savedData.formData.notes || '');
                    }

                    // Refresh the cart display
                    refreshCartDataTable();
                    updateCartTotals();
                    toggleCartSection();

                    if (window.cartItems.length > 0) {
                        toastr.success(`Restored ${window.cartItems.length} items from previous session`);
                    }
                } else {
                    console.log('No saved data found for ZID:', zid);
                }

                // Setup auto-save triggers after ZID is loaded
                setupAutoSaveTriggers();
            })
            .catch(function(error) {
                console.error('Error initializing localStorage:', error);
                toastr.warning('Session data unavailable: ' + error);
                // Still setup auto-save triggers even if ZID loading fails
                setupAutoSaveTriggers();
            });
    }

    // Initialize localStorage after a short delay to ensure DOM is ready
    setTimeout(initializeLocalStorage, 100);

    // Add auto-save triggers for form inputs
    function setupAutoSaveTriggers() {
        // Auto-save on form field changes - simplified to avoid redundancy
        $(document).on('change input', '#invoice-date, #receive-type, #supplierSelect, #warehouse, #notes', function() {
            console.log('Form field changed:', this.id);
            if (window.salesReturnStorage) {
                window.salesReturnStorage.autoSave();
            }
        });

        // Auto-save on Select2 changes
        $(document).on('select2:select select2:unselect select2:clear', '#receive-type, #supplierSelect, #warehouse', function() {
            console.log('Select2 changed:', this.id);
            if (window.salesReturnStorage) {
                window.salesReturnStorage.autoSave();
            }
        });

        console.log('Auto-save triggers setup completed');
    }

    // Format number helper
    function formatNumber(num) {
        return parseFloat(num || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Form validation function
    function validateForm() {
        let isValid = true;
        let errorMessages = [];

        // Validate transaction date
        const transactionDate = $('#transaction-date').val();
        if (!transactionDate || transactionDate.trim() === '') {
            isValid = false;
            errorMessages.push('Transaction Date is required');
            $('#transaction-date').addClass('is-invalid');
        } else {
            $('#transaction-date').removeClass('is-invalid');
        }

        // Validate invoice date
        const invoiceDate = $('#invoice-date').val();
        if (!invoiceDate || invoiceDate.trim() === '') {
            isValid = false;
            errorMessages.push('Invoice Date is required');
            $('#invoice-date').addClass('is-invalid');
        } else {
            $('#invoice-date').removeClass('is-invalid');
        }

        // Validate supplier
        const supplier = $('#supplierSelect').val();
        if (!supplier || supplier.trim() === '') {
            isValid = false;
            errorMessages.push('Supplier Number is required');
            $('#supplierSelect').next('.select2-container').find('.select2-selection').addClass('is-invalid');
        } else {
            $('#supplierSelect').next('.select2-container').find('.select2-selection').removeClass('is-invalid');
        }

        // Validate warehouse (already has required attribute)
        const warehouse = $('#warehouse').val();
        if (!warehouse || warehouse.trim() === '') {
            isValid = false;
            errorMessages.push('Warehouse is required');
            $('#warehouse').next('.select2-container').find('.select2-selection').addClass('is-invalid');
        } else {
            $('#warehouse').next('.select2-container').find('.select2-selection').removeClass('is-invalid');
        }

        // Show validation errors
        if (!isValid) {
            toastr.error('Please fix the following errors:<br>• ' + errorMessages.join('<br>• '));
        }

        return isValid;
    }

    // Make validateForm globally accessible
    window.validateSalesReturnForm = validateForm;
});

/**
 * Configure toastr notifications
 */
toastr.options = {
    closeButton: true,
    debug: false,
    newestOnTop: true,
    progressBar: true,
    positionClass: 'toast-top-right',
    preventDuplicates: false,
    onclick: null,
    showDuration: '300',
    hideDuration: '1000',
    timeOut: '5000',
    extendedTimeOut: '1000',
    showEasing: 'swing',
    hideEasing: 'linear',
    showMethod: 'fadeIn',
    hideMethod: 'fadeOut'
};
