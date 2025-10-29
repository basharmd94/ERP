// Sales Return Update Cart Management
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

    // LocalStorage functionality with ZID-based keys
    window.salesReturnUpdateStorage = {
        // Get current ZID from server
        getCurrentZid: function() {
            return $.ajax({
                url: '/api/get-current-zid/',
                type: 'GET',
                cache: false,
                data: { '_': Date.now() }
            }).then(response => {
                console.log('ZID API Response:', response);
                if (response.success) {
                    window.currentZid = response.zid;
                    console.log('Current ZID loaded:', response.zid);
                    return response.zid;
                } else {
                    console.error('ZID API failed:', response.message);
                    if (response.debug_info) console.error('Debug info:', response.debug_info);
                    return Promise.reject(response.message || 'Failed to get ZID');
                }
            }).catch(xhr => {
                console.error('ZID API Error:', {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    responseText: xhr.responseText
                });
                return Promise.reject('Error getting ZID');
            });
        },

        // Generate storage key with ZID
        getStorageKey: function(key) {
            return `sales_return_update_${window.currentZid}_${key}`;
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
                    transaction_date: $('#transaction-date').val() || '',
                    invoice_date: $('#invoice-date').val() || '',
                    customer: $('#customer').val() || '',
                    supplier_select: $('#supplierSelect').val() || '',
                    warehouse: $('#warehouse').val() || '',
                    project: $('#project').val() || '',
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
            //
            columns: [
                {
                    title: 'Sl',
                    data: null,
                    width: '5%',
                    orderable: false,
                    render: function(data, type, row, meta) {
                        return `<div class="text-center fw-bold" style="font-size: 0.875rem;">${meta.row + 1}</div>`;
                    }
                },
                {
                    title: 'Item Name',
                    data: null,
                    width: '25%',
                    render: function(data, type, row) {
                        const description = row.xdesc || 'No Description';
                        const truncatedDesc = description.length > 30 ? description.substring(0, 30) + '...' : description;
                        return `
                            <div class="fw-bold text-truncate text-start" style="font-size: 0.875rem;">${row.xitem}</div>
                            <small class="text-muted text-truncate d-block" title="${description}" style="font-size: 0.75rem;">${truncatedDesc}</small>
                        `;
                    }
                },
                {
                    title: 'Stock',
                    data: null,
                    width: '10%',
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
                        const displayPrice = row.avg_price <= 0 ? row.xstdcost : row.avg_price;
                        return `
                            <div class="flex-column text-center ">
                                <div class="text-muted text-start" style="font-size: 0.7rem;">avg: ৳${formatNumber(displayPrice)}</div>
                                <div  class="text-muted text-start" style="font-size: 0.7rem;">sale: ৳${formatNumber(row.xstdprice)}</div>
                            </div>
                        `;
                    }
                },
                {
                    title: 'Qty',
                    data: 'quantity',
                    width: '10%',
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
                    title: 'Inv Value',
                    data: null,
                    width: '10%',
                    render: function(data, type, row) {
                        const fallbackPrice = row.avg_price <= 0 ? row.xstdcost : row.avg_price;
                        const invPrice = row.mkt_price || fallbackPrice;
                        const invValue = invPrice * row.quantity;
                        return `<div class="fw-bold text-success text-center" style="font-size: 0.875rem;">৳${formatNumber(invValue)}</div>`;
                    }
                },
                {
                    title: 'Mkt Value',
                    data: null,
                    width: '10%',
                    render: function(data, type, row) {
                        const mktPrice = row.xstdprice;
                        const mktValue = mktPrice * row.quantity;
                        return `<div class="fw-bold text-success text-center" style="font-size: 0.875rem;">৳${formatNumber(mktValue)}</div>`;
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
                                    class="btn btn-sm btn-outline-danger remove-item "
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
            const initialPrice = item.avg_price <= 0 ? item.xstdcost : item.avg_price;
            const cartItem = {
                ...item,
                quantity: 1,
                mkt_price: initialPrice, // Initialize mkt_price with avg_price or xstdcost if avg_price <= 0
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
        if (window.salesReturnUpdateStorage) {
            window.salesReturnUpdateStorage.autoSave();
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
            if (window.salesReturnUpdateStorage) {
                window.salesReturnUpdateStorage.autoSave();
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
            if (window.salesReturnUpdateStorage) {
                window.salesReturnUpdateStorage.autoSave();
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
            if (window.salesReturnUpdateStorage) {
                window.salesReturnUpdateStorage.autoSave();
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
        let totalInvValue = 0;
        let totalMktValue = 0;

        cartItems.forEach(item => {
            totalItems += item.quantity;

            // Calculate Total Inv Value (matches individual row: mkt_price || fallbackPrice)
            const fallbackPrice = item.avg_price <= 0 ? item.xstdcost : item.avg_price;
            const invPrice = item.mkt_price || fallbackPrice;
            totalInvValue += invPrice * item.quantity;

            // Calculate Total Mkt Value (matches individual row: xstdprice * quantity)
            const mktPrice = item.xstdprice || 0;
            totalMktValue += mktPrice * item.quantity;
        });

        $('#cart-total-items').text(formatNumber(totalItems));
        $('#cart-total-inv-value').text(`৳${formatNumber(totalInvValue)}`);
        $('#cart-total-mkt-value').text(`৳${formatNumber(totalMktValue)}`);
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

        // Clear cart immediately without confirmation
        cartItems = [];
        refreshCartDataTable();
        updateCartTotals();
        toggleCartSection();

        // Clear localStorage data
        if (window.salesReturnUpdateStorage) {
            window.salesReturnUpdateStorage.clearCartData();
        }

        toastr.success('Cart cleared successfully');
    };

    // Initialize DataTable when document is ready
    initCartDataTable();

    // Load existing cart items from template context
    function loadExistingCartItems() {
        if (typeof window.existingCartItems !== 'undefined' && window.existingCartItems.length > 0) {
            console.log('Loading existing cart items:', window.existingCartItems);
            
            // Clear existing cart
            cartItems = [];
            cartCounter = 0;
            
            // Add each item to cart with proper structure and fetch item details
            window.existingCartItems.forEach(function(item, index) {
                const quantity = parseFloat(item.quantity || 0);
                const mktValue = parseFloat(item.mkt_value || 0);
                
                // Calculate xstdprice from mkt_value and quantity for market value calculation
                const calculatedXstdprice = quantity > 0 ? (mktValue / quantity) : 0;
                
                const cartItem = {
                    cartId: ++cartCounter,
                    xitem: item.item_code,
                    xdesc: item.item_code, // Will be populated when item details are loaded
                    quantity: quantity,
                    avg_price: parseFloat(item.rate || 0), // Use rate as avg_price (inventory value)
                    xstdprice: calculatedXstdprice, // Calculate from existing mkt_value
                    xstdcost: 0, // Will be populated when item details are loaded
                    mkt_price: parseFloat(item.amount || 0) / parseFloat(item.quantity || 1), // Calculate from amount
                    stock: 0, // Will be populated when item details are loaded
                    xunitstk: 'PCS' // Will be populated when item details are loaded
                };
                cartItems.push(cartItem);
                
                // Fetch item details to populate correct prices (but preserve calculated xstdprice)
                fetchItemDetails(item.item_code, cartItem);
            });
            
            refreshCartDataTable();
            updateCartTotals();
            toggleCartSection();
            console.log(`Loaded ${cartItems.length} existing items into cart`);
        } else {
            console.log('No existing cart items found, starting with empty cart');
            toggleCartSection();
        }
    }

    // Fetch item details for existing cart items
    function fetchItemDetails(itemCode, cartItem) {
        $.ajax({
            url: '/api/avg-item-price/',
            method: 'GET',
            data: {
                search: itemCode,
                page: 1
            },
            success: function(response) {
                if (response.results && response.results.length > 0) {
                    const itemData = response.results.find(item => item.xitem === itemCode);
                    if (itemData) {
                        // Update cart item with correct item details
                        cartItem.xdesc = itemData.xdesc || itemCode;
                        
                        // Only update xstdprice if it's currently 0 (not calculated from existing data)
                        if (cartItem.xstdprice === 0) {
                            cartItem.xstdprice = parseFloat(itemData.xstdprice || 0);
                        }
                        
                        cartItem.xstdcost = parseFloat(itemData.xstdcost || 0);
                        cartItem.stock = parseFloat(itemData.stock || 0);
                        cartItem.xunitstk = itemData.xunitstk || 'PCS';
                        
                        // Keep the original avg_price from rate, but update if API has better data
                        if (itemData.avg_price && itemData.avg_price > 0) {
                            cartItem.avg_price = parseFloat(itemData.avg_price);
                        }
                        
                        // Refresh the table to show updated data
                        refreshCartDataTable();
                        updateCartTotals(); // Ensure totals are recalculated with correct data
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching item details for', itemCode, ':', error);
            }
        });
    }

    // Initialize localStorage functionality
    function initializeLocalStorage() {
        console.log('Initializing localStorage functionality...');

        window.salesReturnUpdateStorage.getCurrentZid()
            .then(function(zid) {
                console.log('Successfully loaded ZID:', zid);
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

    // Add auto-save triggers for form inputs
    function setupAutoSaveTriggers() {
        // Auto-save on form field changes - simplified to avoid redundancy
        $(document).on('change input', '#transaction-date, #invoice-date, #customer, #supplierSelect, #warehouse, #project, #notes', function() {
            console.log('Form field changed:', this.id);
            if (window.salesReturnUpdateStorage) {
                window.salesReturnUpdateStorage.autoSave();
            }
        });

        // Auto-save on Select2 changes
        $(document).on('select2:select select2:unselect select2:clear', '#customer, #supplierSelect, #warehouse, #project', function() {
            console.log('Select2 changed:', this.id);
            if (window.salesReturnUpdateStorage) {
                window.salesReturnUpdateStorage.autoSave();
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

    // Sales Return Update Module for form submission
    window.SalesReturnUpdate = {
        handleFormSubmission: function() {
            // Validate form first
            if (!validateForm()) {
                return;
            }

            // Check if cart has items
            if (cartItems.length === 0) {
                toastr.error('Please add at least one item to the cart');
                return;
            }

            // Collect form data and submit via AJAX
            const formData = {
                transaction_id: $('#transaction-id').val(),
                transaction_date: $('#transaction-date').val(),
                invoice_date: $('#invoice-date').val(),
                customer: $('#customer').val(),
                supplier: $('#supplierSelect').val(),
                warehouse: $('#warehouse').val(),
                project: $('#project').val(),
                notes: $('#notes').val(),
                items: [],
                totals: {}
            };

            // Calculate totals while collecting cart items
            let totalInvValue = 0;
            let totalMktValue = 0;
            let totalItems = 0;

            // Collect cart items
            cartItems.forEach(function(item) {
                // Rate should be inventory value per unit (avg_price)
                const inventoryRate = item.avg_price || item.xstdcost || 0;
                // Amount should be market value total (mkt_price * quantity)
                const marketPrice = item.mkt_price || item.xstdprice || inventoryRate;
                const quantity = parseFloat(item.quantity) || 0;
                
                const cartItem = {
                    item_code: item.xitem,
                    quantity: quantity,
                    rate: inventoryRate,  // INV Value per unit
                    amount: marketPrice * quantity  // MKT Value total
                };
                formData.items.push(cartItem);

                // Calculate totals
                totalInvValue += inventoryRate * quantity;
                totalMktValue += marketPrice * quantity;
                totalItems += quantity;
            });

            // Add totals to form data
            formData.totals = {
                totalInvValue: totalInvValue,
                totalMktValue: totalMktValue,
                totalItems: totalItems
            };

            // Submit via AJAX
            $.ajax({
                url: window.location.href, // Current URL
                type: 'POST',
                data: JSON.stringify(formData),
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.success) {
                        toastr.success('Sales return updated successfully!');
                        
                        // Clear localStorage data
                        if (window.salesReturnUpdateStorage) {
                            window.salesReturnUpdateStorage.clearCartData();
                        }
                        
                        // Redirect to detail page after short delay
                        setTimeout(function() {
                            if (response.redirect_url) {
                                window.location.href = response.redirect_url;
                            } else {
                                window.location.href = `/sales-return-detail/${response.transaction_id}/`;
                            }
                        }, 1500);
                    } else {
                        toastr.error(response.message || 'Error updating sales return');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error updating sales return:', error);
                    
                    let errorMessage = 'Error updating sales return';
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        try {
                            const errorData = JSON.parse(xhr.responseText);
                            errorMessage = errorData.message || errorMessage;
                        } catch (e) {
                            // Use default message
                        }
                    }
                    
                    toastr.error(errorMessage);
                }
            });
        }
    };

    // Load existing cart items after initialization
    loadExistingCartItems();
    
    // Initialize localStorage after a short delay to ensure DOM is ready
    setTimeout(initializeLocalStorage, 100);

    // Make validateForm globally accessible
    window.validateSalesReturnUpdateForm = validateForm;
});