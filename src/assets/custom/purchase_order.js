// Purchase Order Create Cart Management
$(document).ready(function() {
    // Cart array to store items
    window.cartItems = [];
    window.cartCounter = 0;
    window.cartDataTable = null;
    window.currentZid = null;

    // Initialize Bootstrap Date Pickers with YYYY-MM-DD format
    $('#transaction-date').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true,
        clearBtn: true,
        orientation: 'bottom auto',
        container: 'body'
    });

    // Set today's date as default
    var today = new Date();
    $('#transaction-date').datepicker('setDate', today);

    // LocalStorage functionality with ZID-based keys
    window.poCreateStorage = {
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
                    return Promise.reject(response.message || 'Failed to get ZID');
                }
            }).catch(xhr => {
                console.error('ZID API Error:', xhr);
                return Promise.reject('Error getting ZID');
            });
        },

        // Generate storage key with ZID
        getStorageKey: function(key) {
            return `po_create_${window.currentZid}_${key}`;
        },

        // Save cart data to localStorage
        saveCartData: function() {
            if (!window.currentZid) return;

            const cartData = {
                items: window.cartItems,
                counter: window.cartCounter,
                timestamp: new Date().toISOString(),
                // Save form data
                formData: {
                    transaction_date: $('#transaction-date').val() || '',
                    supplier_select: $('#supplierSelect').val() || '',
                    warehouse: $('#warehouse').val() || '',
                    project: $('#project').val() || '',
                    discount_percent: $('#discount-percent').val() || '',
                    fixed_discount: $('#fixed-discount').val() || '',
                    notes: $('#notes').val() || '',
                    transaction_prefix: $('#transaction-prefix').val() || 'PO--'
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
                    return JSON.parse(savedData);
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
            paging: false,
            info: false,
            searching: false,
            fixedHeader: true,
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
                    title: 'Item Code',
                    data: 'xitem',
                    width: '20%',
                    render: function(data, type, row) {
                        return `<div class="text-start" style="font-size: 0.875rem;">${data}</div>`;
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
                            <div class="fw-bold text-truncate text-start" style="font-size: 0.875rem;">${description}</div>
                            <small class="text-muted text-truncate d-block" title="${description}" style="font-size: 0.75rem;">${truncatedDesc}</small>
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
                    title: 'Rate',
                    data: 'rate',
                    width: '15%',
                    render: function(data, type, row) {
                        return `
                            <input type="number"
                                   class="form-control form-control-sm rate-input"
                                   value="${data}"
                                   min="0.01"
                                   step="0.01"
                                   data-cart-id="${row.cartId}"
                                   style="width: 80px; font-size: 0.875rem;">
                        `;
                    }
                },
                {
                    title: 'Line Amount',
                    data: null,
                    width: '15%',
                    render: function(data, type, row) {
                        const amount = row.rate * row.quantity;
                        return `<div class="fw-bold text-success text-center" style="font-size: 0.875rem;">৳${formatNumber(amount)}</div>`;
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

        // Handle rate change
        $('#cart-datatable').on('change', '.rate-input', function() {
            const cartId = parseInt($(this).data('cart-id'));
            const newRate = parseFloat($(this).val());
            updateRate(cartId, newRate);
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
            // Use cost price as default rate for PO
            const initialRate = item.xstdcost || 0;
            const cartItem = {
                ...item,
                quantity: 1,
                rate: initialRate,
                cartId: ++cartCounter
            };
            cartItems.push(cartItem);
            targetCartId = cartItem.cartId;
        }

        // Refresh DataTable with updated data
        refreshCartDataTable();
        updateCartTotals();
        showCartSection();

        // Auto-focus and select quantity input
        setTimeout(() => {
            const quantityInput = $(`.quantity-input[data-cart-id="${targetCartId}"]`);
            if (quantityInput.length > 0) {
                quantityInput.focus().select();

                // Scroll to input if needed
                const cartTable = $('.card-datatable');
                const inputOffset = quantityInput.offset();
                const tableOffset = cartTable.offset();

                if (inputOffset && tableOffset) {
                    const relativeTop = inputOffset.top - tableOffset.top;
                    const tableHeight = cartTable.height();

                    if (relativeTop < 0 || relativeTop > tableHeight - 50) {
                        cartTable.animate({
                            scrollTop: cartTable.scrollTop() + relativeTop - (tableHeight / 2)
                        }, 300);
                    }
                }
            }
        }, 100);

        // Auto-save to localStorage
        if (window.poCreateStorage) {
            window.poCreateStorage.autoSave();
        }

        toastr.success('Item added to cart successfully!');

        // Clear search selection
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

            if (window.poCreateStorage) {
                window.poCreateStorage.autoSave();
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

            if (window.poCreateStorage) {
                window.poCreateStorage.autoSave();
            }
        }
    }

    // Update rate
    window.updateRate = function(cartId, newRate) {
        if (newRate < 0) {
            toastr.warning('Rate cannot be negative');
            return;
        }

        const itemIndex = cartItems.findIndex(item => item.cartId === cartId);
        if (itemIndex !== -1) {
            cartItems[itemIndex].rate = newRate;
            refreshCartDataTable();
            updateCartTotals();

            if (window.poCreateStorage) {
                window.poCreateStorage.autoSave();
            }
        }
    }

    // Refresh DataTable
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
            totalAmount += item.rate * item.quantity;
        });

        // Calculate discounts
        const discountPercent = parseFloat($('#discount-percent').val()) || 0;
        const fixedDiscount = parseFloat($('#fixed-discount').val()) || 0;

        let discountAmount = 0;
        if (discountPercent > 0) {
            discountAmount += (totalAmount * discountPercent / 100);
        }
        discountAmount += fixedDiscount;

        const netAmount = Math.max(0, totalAmount - discountAmount);

        $('#cart-total-items').text(formatNumber(totalItems));
        $('#cart-total-amount').text(`৳${formatNumber(totalAmount)}`);
        $('#cart-total-discount').text(`৳${formatNumber(discountAmount)}`);
        $('#cart-net-amount').text(`৳${formatNumber(netAmount)}`);
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

    function toggleCartSection() {
        if (cartItems.length > 0) {
            showCartSection();
        } else {
            hideCartSection();
        }
    }

    // Clear entire cart
    window.clearCart = function() {
        if (cartItems.length === 0) {
            toastr.info('Cart is already empty');
            return;
        }

        cartItems = [];
        refreshCartDataTable();
        updateCartTotals();
        toggleCartSection();

        if (window.poCreateStorage) {
            window.poCreateStorage.clearCartData();
        }

        toastr.success('Cart cleared successfully');
    };

    // Initialize DataTable
    initCartDataTable();

    // Restore supplier selection
    function restoreSupplierSelection(supplierCode) {
        console.log('Restoring supplier selection:', supplierCode);

        $.ajax({
            url: '/api/get-supplier/',
            type: 'GET',
            dataType: 'json',
            data: { q: supplierCode },
            success: function(response) {
                if (response.results && response.results.length > 0) {
                    const supplier = response.results.find(s => s.text === supplierCode);
                    if (supplier) {
                        const option = new Option(supplier.text, supplier.id, true, true);
                        $('#supplierSelect').append(option).trigger('change');
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading supplier:', error);
            }
        });
    }

    // Initialize localStorage
    function initializeLocalStorage() {
        console.log('Initializing localStorage functionality...');

        window.poCreateStorage.getCurrentZid()
            .then(function(zid) {
                console.log('Successfully loaded ZID:', zid);

                const savedData = window.poCreateStorage.loadCartData();
                if (savedData) {
                    console.log('Found saved data:', savedData);

                    window.cartItems = savedData.items || [];
                    window.cartCounter = savedData.counter || 0;

                    if (savedData.formData) {
                        $('#transaction-date').val(savedData.formData.transaction_date || '');
                        $('#transaction-prefix').val(savedData.formData.transaction_prefix || 'PO--').trigger('change');

                        if (savedData.formData.supplier_select) {
                            restoreSupplierSelection(savedData.formData.supplier_select);
                        }

                        $('#warehouse').val(savedData.formData.warehouse || '').trigger('change');
                        $('#project').val(savedData.formData.project || '').trigger('change');
                        $('#discount-percent').val(savedData.formData.discount_percent || '');
                        $('#fixed-discount').val(savedData.formData.fixed_discount || '');
                        $('#notes').val(savedData.formData.notes || '');
                    }

                    refreshCartDataTable();
                    updateCartTotals();
                    toggleCartSection();

                    if (window.cartItems.length > 0) {
                        toastr.success(`Restored ${window.cartItems.length} items from previous session`);
                    }
                }
                setupAutoSaveTriggers();
            })
            .catch(function(error) {
                console.error('Error initializing localStorage:', error);
                toastr.warning('Session data unavailable: ' + error);
                setupAutoSaveTriggers();
            });
    }

    // Initialize after delay
    setTimeout(initializeLocalStorage, 100);

    // Setup auto-save triggers
    function setupAutoSaveTriggers() {
        $(document).on('change input', '#transaction-date, #discount-percent, #fixed-discount, #notes, #transaction-prefix', function() {
            if (window.poCreateStorage) {
                window.poCreateStorage.autoSave();
                updateCartTotals(); // Recalculate totals on discount change
            }
        });

        $(document).on('select2:select select2:unselect select2:clear', '#supplierSelect, #warehouse, #project', function() {
            if (window.poCreateStorage) {
                window.poCreateStorage.autoSave();
            }
        });
    }

    // Format number helper
    function formatNumber(num) {
        return parseFloat(num || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Form validation
    function validateForm() {
        let isValid = true;
        let errorMessages = [];

        const transactionDate = $('#transaction-date').val();
        if (!transactionDate || transactionDate.trim() === '') {
            isValid = false;
            errorMessages.push('Date is required');
            $('#transaction-date').addClass('is-invalid');
        } else {
            $('#transaction-date').removeClass('is-invalid');
        }

        const supplier = $('#supplierSelect').val();
        if (!supplier || supplier.trim() === '') {
            isValid = false;
            errorMessages.push('Supplier Number is required');
            $('#supplierSelect').next('.select2-container').find('.select2-selection').addClass('is-invalid');
        } else {
            $('#supplierSelect').next('.select2-container').find('.select2-selection').removeClass('is-invalid');
        }

        const warehouse = $('#warehouse').val();
        if (!warehouse || warehouse.trim() === '') {
            isValid = false;
            errorMessages.push('Warehouse is required');
            $('#warehouse').next('.select2-container').find('.select2-selection').addClass('is-invalid');
        } else {
            $('#warehouse').next('.select2-container').find('.select2-selection').removeClass('is-invalid');
        }

        const project = $('#project').val();
        if (!project || project.trim() === '') {
            isValid = false;
            errorMessages.push('Project is required');
            $('#project').next('.select2-container').find('.select2-selection').addClass('is-invalid');
        } else {
            $('#project').next('.select2-container').find('.select2-selection').removeClass('is-invalid');
        }

        if (!isValid) {
            toastr.error('Please fix the following errors:<br>• ' + errorMessages.join('<br>• '));
        }

        return isValid;
    }

    // Make validation accessible
    window.validatePOForm = validateForm;

    // Process PO
    window.processPO = function() {
        if (validateForm()) {
            if (cartItems.length === 0) {
                toastr.warning('Please add items to the cart');
                return;
            }

            // Confirm submission
            Swal.fire({
                title: 'Are you sure?',
                text: "Do you want to create this Purchase Order?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, create it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Prepare data for API
                    const poData = {
                        header: {
                            xdate: $('#transaction-date').val(),
                            xsup: $('#supplierSelect').val(),
                            xsupref: '', // Add if there's a field for supplier ref
                            xdiv: '',
                            xsec: 'Any',
                            xproj: $('#project').val(),
                            xwh: $('#warehouse').val(),
                            xrem: $('#notes').val(),
                            xdisc: $('#discount-percent').val() || 0,
                            xdtdisc: $('#fixed-discount').val() || 0,
                            xtrnpor: $('#transaction-prefix').val()
                        },
                        details: cartItems.map(item => ({
                            xitem: item.xitem,
                            xqtyord: item.quantity,
                            xrate: item.rate
                        }))
                    };

                    // Show loading state
                    const submitBtn = $('#process-po');
                    const originalBtnText = submitBtn.html();
                    submitBtn.html('<i class="fas fa-spinner fa-spin me-1"></i>Processing...').prop('disabled', true);

                    // API Call
                    $.ajax({
                        url: '/purchase/po-create/',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(poData),
                        success: function(response) {
                            if (response.success) {
                                Swal.fire(
                                    'Created!',
                                    `Purchase Order ${response.voucher_number} has been created successfully.`,
                                    'success'
                                ).then(() => {
                                    // Clear cart and reload or redirect
                                    window.clearCart();
                                    // Optional: Redirect to PO List or PO Details
                                    // window.location.href = '/purchase/po-list/';
                                });
                            } else {
                                toastr.error(response.message || 'Failed to create Purchase Order');
                            }
                        },
                        error: function(xhr) {
                            console.error('Error creating PO:', xhr);
                            let errorMsg = 'An error occurred while creating the Purchase Order.';
                            if (xhr.responseJSON && xhr.responseJSON.message) {
                                errorMsg = xhr.responseJSON.message;
                            }
                            toastr.error(errorMsg);
                        },
                        complete: function() {
                            // Reset button state
                            submitBtn.html(originalBtnText).prop('disabled', false);
                        }
                    });
                }
            });
        }
    };
});
