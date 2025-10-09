// POS System JavaScript
$(document).ready(function() {
    // Initialize POS system
    initializePOS();
});

function initializePOS() {
    console.log('Initializing POS System...');
    
    // Initialize product search
    initializeProductSearch();
    
    // Initialize cart
    initializeCart();
    
    // Initialize customer form
    initializeCustomerForm();
    
    // Initialize payment methods
    initializePaymentMethods();
    
    // Initialize barcode scanner
    initializeBarcodeScanner();
    
    // Load saved transactions
    loadSavedTransactions();
    
    // Initialize hold list popover
    initializeHoldListPopover();
    
    console.log('POS System initialized successfully');
}

function initializeProductSearch() {
    $('#product-search').select2({
        placeholder: 'Search products by name, code, or barcode...',
        allowClear: true,
        minimumInputLength: 1,
        ajax: {
            url: '/sales/api/pos/products/',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.results,
                    pagination: {
                        more: data.pagination.more
                    }
                };
            },
            cache: true
        },
        templateResult: function(item) {
            if (item.loading) return item.text;
            
            return $(`
                <div class="product-result">
                    <div class="fw-bold">${item.text}</div>
                    <div class="small text-muted">
                        Price: ৳${item.xstdprice} | Stock: ${item.stock} | Barcode: ${item.xbarcode || 'N/A'}
                    </div>
                </div>
            `);
        },
        templateSelection: function(item) {
            return item.text || item.id;
        }
    });
    
    // Handle product selection
    $('#product-search').on('select2:select', function (e) {
        const product = e.params.data;
        addToCart(product);
        $(this).val(null).trigger('change');
    });
}

function initializeCart() {
    // Load cart from localStorage
    loadCart();
    // Clear discount fields on page load
    clearDiscountFields();
    updateCartDisplay();
}

function initializeCustomerForm() {
    // Initialize header customer fields with default values
    $('#header-customer-name').val('CUS-000001');
    $('#header-warehouse').val('Fixit Gulshan');
    $('#header-salesman').val('Ohidul');
    console.log('Header customer fields initialized with defaults');
}

function clearInput() {
    console.log('Clearing all input fields...');
    
    // Reset payment method to cash
    $('#payment-method-select').val('cash');
    window.selectedPaymentMethod = 'cash';
    
    // Hide and clear card sections
    $('#card-amount-section').removeClass('show');
    $('#card-number-section').hide();
    $('#card-amount').val('');
    $('#card-number').val('');
    
    // Clear discount fields
    $('#fixed-discount').val('0');
    $('#percent-discount').val('0');
    
    // Clear customer notes
    $('#order-notes').val('');
    
    // Clear pay amount and hide return amount
    $('#pay-amount').val('0');
    $('#return-amount-section').hide();
    
    // Update cash amount display
    $('#cash-amount').text('0.00');
    
    console.log('All input fields cleared successfully');
}

function initializePaymentMethods() {
    // Set default payment method
    window.selectedPaymentMethod = 'cash';
    $('#payment-method-select').val('cash');
    
    // Handle payment method selection via dropdown
    $('#payment-method-select').on('change', function() {
        const method = $(this).val();
        console.log('Payment method selected:', method);
        
        // Store selected payment method
        window.selectedPaymentMethod = method;
        
        // Show/hide card amount and card number sections
        if (method === 'card') {
            $('#card-amount-section').addClass('show');
            $('#card-number-section').show();
            updateCardAmountFromTotal();
        } else {
            $('#card-amount-section').removeClass('show');
            $('#card-number-section').hide();
            $('#card-number').val(''); // Clear card number when switching to cash
        }
    });
    
    // Handle card amount input
    $('#card-amount').on('input', function() {
        const cardAmount = parseFloat($(this).val()) || 0;
        const total = getCurrentTotal();
        const cashAmount = Math.max(0, total - cardAmount);
        $('#cash-amount').text(cashAmount.toFixed(2));
        $('#pay-amount').val(cashAmount.toFixed(2));
        updateReturnAmount();
    });
    
    // Handle pay amount input
    $('#pay-amount').on('input', function() {
        updateReturnAmount();
    });
    
    // Handle discount inputs
    $('#fixed-discount, #percent-discount').on('input', function() {
        updateCartDisplay();
    });
    
    console.log('Payment methods initialized');
}

function getCurrentTotal() {
    const subtotal = cart.reduce((sum, item) => sum + item.total, 0);
    const fixedDiscount = parseFloat($('#fixed-discount').val()) || 0;
    const percentDiscount = parseFloat($('#percent-discount').val()) || 0;
    const discountAmount = fixedDiscount + (subtotal * percentDiscount / 100);
    const discountedSubtotal = Math.max(0, subtotal - discountAmount);
    const tax = subtotal * 0.075; // 7.5% VAT on original subtotal
    return discountedSubtotal + tax;
}

function updateCardAmount(total) {
    if (window.selectedPaymentMethod === 'card') {
        const currentCardAmount = parseFloat($('#card-amount').val()) || 0;
        if (currentCardAmount === 0 || currentCardAmount > total) {
            $('#card-amount').val(total.toFixed(2));
            $('#cash-amount').text('0.00');
            $('#pay-amount').val('0.00');
        } else {
            const cashAmount = Math.max(0, total - currentCardAmount);
            $('#cash-amount').text(cashAmount.toFixed(2));
            $('#pay-amount').val(cashAmount.toFixed(2));
        }
        updateReturnAmount();
    }
}

function updateCardAmountFromTotal() {
    const total = getCurrentTotal();
    $('#card-amount').val(total.toFixed(2));
    $('#cash-amount').text('0.00');
}

function updatePayAmount(total) {
    // Always update Pay Amount field to match the current total
    $('#pay-amount').val(total.toFixed(2));
    updateReturnAmount();
}

function updateReturnAmount() {
    const total = getCurrentTotal();
    const payAmount = parseFloat($('#pay-amount').val()) || 0;
    
    let returnAmount = 0;
    
    if (window.selectedPaymentMethod === 'card') {
        // For card payment: Return = Cash paid - Cash portion needed
        const cardAmount = parseFloat($('#card-amount').val()) || 0;
        const cashPortionNeeded = Math.max(0, total - cardAmount);
        returnAmount = Math.max(0, payAmount - cashPortionNeeded);
    } else {
        // For cash payment: Return = Cash paid - Total amount
        returnAmount = Math.max(0, payAmount - total);
    }
    
    if (returnAmount > 0) {
        $('#return-amount-section').show();
        $('#return-amount').text(`৳${returnAmount.toFixed(2)}`);
    } else {
        $('#return-amount-section').hide();
    }
}

function updateCashAmountFromPayAmount() {
    if (window.selectedPaymentMethod === 'card') {
        const total = getCurrentTotal();
        const cardAmount = parseFloat($('#card-amount').val()) || 0;
        const cashAmount = Math.max(0, total - cardAmount);
        
        // Update Pay Amount to reflect the cash portion
        $('#pay-amount').val(cashAmount.toFixed(2));
        updateReturnAmount();
    }
}

function initializeBarcodeScanner() {
    // Auto-focus the barcode input when page loads
    $('#barcode-input').focus();
    
    $('#barcode-input').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            const barcode = $(this).val().trim();
            if (barcode) {
                searchProductByBarcode(barcode);
                $(this).val('');
                // Re-focus after processing barcode
                setTimeout(() => {
                    $('#barcode-input').focus();
                }, 100);
            }
        }
    });
    
    // Re-focus barcode input when clicking anywhere on the page
    $(document).on('click', function(e) {
        // Don't interfere with other input fields or buttons
        if (!$(e.target).is('input, button, select, textarea, a')) {
            $('#barcode-input').focus();
        }
    });
}

function loadSavedTransactions() {
    // Load saved transactions from localStorage
    console.log('Loading saved transactions...');
}

function initializeHoldListPopover() {
    // Initialize Bootstrap 5 popover for hold list
    const holdListBtn = document.getElementById('hold-list-btn');
    if (holdListBtn) {
        // Create Bootstrap 5 popover instance
        window.holdListPopover = new bootstrap.Popover(holdListBtn, {
            trigger: 'click',
            html: true,
            sanitize: false,
            content: '<div class="p-2 text-muted">No held transactions</div>',
            placement: 'bottom'
        });
        
        // Update popover content on initialization
        updateHoldListPopover();
        
        // Close popover when clicking outside
        $(document).on('click', function (e) {
            if (!$(e.target).closest('#hold-list-btn').length) {
                if (window.holdListPopover) {
                    window.holdListPopover.hide();
                }
            }
        });
    }
}

// Cart management functions
let cart = [];
// Make cart accessible to validation module
window.cart = cart;

function addToCart(product) {
    // Check if product has zero stock
    if (product.stock <= 0) {
        toastr.error(`${product.xdesc} is out of stock and cannot be added to cart`);
        return;
    }
    
    const existingItem = cart.find(item => item.xitem === product.xitem);
    
    if (existingItem) {
        // Check if adding one more would exceed stock
        if (existingItem.quantity >= product.stock) {
            toastr.warning(`Cannot add more ${product.xdesc}. Only ${product.stock} items available in stock`);
            return;
        }
        existingItem.quantity += 1;
        existingItem.total = existingItem.quantity * existingItem.xstdprice;
    } else {
        cart.push({
            xitem: product.xitem,
            xdesc: product.xdesc,
            xstdprice: product.xstdprice,
            stock: product.stock,
            quantity: 1,
            total: product.xstdprice
        });
    }
    
    saveCart();
    updateCartDisplay();
    
    toastr.success(`${product.xdesc} added to cart`);
}

function removeFromCart(xitem) {
    cart = cart.filter(item => item.xitem !== xitem);
    window.cart = cart; // Sync with validation module
    saveCart();
    updateCartDisplay();
    toastr.info('Item removed from cart');
}

function updateCartQuantity(xitem, quantity) {
    const item = cart.find(item => item.xitem === xitem);
    if (item) {
        const newQuantity = Math.max(1, quantity);
        
        // Check if new quantity exceeds available stock
        if (newQuantity > item.stock) {
            toastr.warning(`Cannot set quantity to ${newQuantity}. Only ${item.stock} items available in stock for ${item.xdesc}`);
            // Reset to current quantity in the input field
            $(`input[onchange*="${xitem}"]`).val(item.quantity);
            return;
        }
        
        item.quantity = newQuantity;
        item.total = item.quantity * item.xstdprice;
        saveCart();
        updateCartDisplay();
    }
}

function updateCartDisplay() {
    const cartContainer = $('#cart-items');
    const cartTotals = $('#cart-totals');
    
    if (cart.length === 0) {
        cartContainer.html(`
            <div class="empty-cart">
                <i class="ti ti-shopping-cart ti-3x mb-3 text-muted"></i>
                <h5 class="text-muted">Cart is empty</h5>
                <p class="text-muted">Search and add products to start a sale</p>
            </div>
        `);
        cartTotals.hide();
        
        // Reset cart count displays
        $('#cart-count').text('0 items');
        $('#summary-items').text('0');
        $('#main-total-display').text('Total: ৳0.00');
        
        // Reset summary displays
        $('#summary-subtotal').text('৳0.00');
        $('#summary-tax').text('৳0.00');
        $('#summary-total').text('৳0.00');
        
        // Hide discount rows
        $('#fixed-discount-row').hide();
        $('#percent-discount-row').hide();
        
        return;
    }
    
    let html = `
        <table class="cart-table">
            <thead>
                <tr>
                    <th style="width: 15%;">Code</th>
                    <th style="width: 25%;">Item Name</th>
                    <th style="width: 10%;">Stock</th>
                    <th style="width: 15%;">Rate</th>
                    <th style="width: 12%;">Qty</th>
                    <th style="width: 15%;">Amount</th>
                    <th style="width: 8%;">Del</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    let subtotal = 0;
    
    cart.forEach(item => {
        subtotal += item.total;
        html += `
            <tr data-xitem="${item.xitem}">
                <td class="item-code">${item.xitem}</td>
                <td class="item-name" title="${item.xdesc}">${item.xdesc}</td>
                <td>${item.stock}</td>
                <td class="rate-cell">৳${item.xstdprice.toFixed(2)}</td>
                <td>
                    <input type="number" class="quantity-input" 
                           value="${item.quantity}" min="1" 
                           onchange="updateCartQuantity('${item.xitem}', this.value)">
                </td>
                <td class="amount-cell">৳${item.total.toFixed(2)}</td>
                <td>
                    <button class="btn btn-outline-danger btn-sm delete-btn" onclick="removeFromCart('${item.xitem}')">
                        <i class="ti ti-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    cartContainer.html(html);
    
    // Calculate discounts
    const fixedDiscount = parseFloat($('#fixed-discount').val()) || 0;
    const percentDiscount = parseFloat($('#percent-discount').val()) || 0;
    const percentDiscountAmount = subtotal * percentDiscount / 100;
    const totalDiscountAmount = fixedDiscount + percentDiscountAmount;
    const discountedSubtotal = Math.max(0, subtotal - totalDiscountAmount);
    
    // Calculate totals - VAT on original subtotal, not after discount
    const tax = subtotal * 0.075; // 7.5% tax on original subtotal
    const total = discountedSubtotal + tax;
    
    cartTotals.html(`
        <div class="total-line">
            <span>Subtotal:</span>
            <span>৳${subtotal.toFixed(2)}</span>
        </div>
        ${fixedDiscount > 0 ? `<div class="total-line text-success">
            <span>Fixed Discount:</span>
            <span>-৳${fixedDiscount.toFixed(2)}</span>
        </div>` : ''}
        ${percentDiscount > 0 ? `<div class="total-line text-success">
            <span>Percent Discount (${percentDiscount}%):</span>
            <span>-৳${percentDiscountAmount.toFixed(2)}</span>
        </div>` : ''}
        <div class="total-line">
            <span>Tax (7.5%):</span>
            <span>৳${tax.toFixed(2)}</span>
        </div>
        <div class="total-line grand-total">
            <span>Total:</span>
            <span>৳${total.toFixed(2)}</span>
        </div>
    `).show();
    
    // Update main total display
    $('#main-total-display').text(`Total: ৳${total.toFixed(2)}`);
    
    // Update cart count displays
    const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    $('#cart-count').text(`${itemCount} item${itemCount !== 1 ? 's' : ''}`);
    $('#summary-items').text(itemCount);
    
    // Update summary section
    $('#summary-subtotal').text(`৳${subtotal.toFixed(2)}`);
    $('#summary-tax').text(`৳${tax.toFixed(2)}`);
    $('#summary-total').text(`৳${total.toFixed(2)}`);
    
    // Update discount displays
    const fixedDiscountAmount = fixedDiscount;
    
    if (fixedDiscountAmount > 0) {
        $('#fixed-discount-row').show();
        $('#summary-fixed-discount').text(`-৳${fixedDiscountAmount.toFixed(2)}`);
    } else {
        $('#fixed-discount-row').hide();
    }
    
    if (percentDiscountAmount > 0) {
        $('#percent-discount-row').show();
        $('#summary-percent-discount').text(`-৳${percentDiscountAmount.toFixed(2)} (${percentDiscount}%)`);
    } else {
        $('#percent-discount-row').hide();
    }
    
    // Update card amount if card is selected
    updateCardAmount(total);
    
    // Update pay amount
    updatePayAmount(total);
}

function saveCart() {
    localStorage.setItem('pos_cart', JSON.stringify(cart));
}

function loadCart() {
    const savedCart = localStorage.getItem('pos_cart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        window.cart = cart; // Sync with validation module
    }
}

function clearDiscountFields() {
    $('#fixed-discount').val('');
    $('#percent-discount').val('');
}

function clearCart() {
    cart = [];
    window.cart = cart; // Sync with validation module
    saveCart();
    clearDiscountFields();
    updateCartDisplay();
    toastr.success('Cart cleared');
    
    // Reload the page to reset all fields and state
    setTimeout(() => {
        location.reload();
    }, 1000); // Wait 1 second to show the success message
}

function searchProductByBarcode(barcode) {
    // Search product by barcode
    $.ajax({
        url: '/sales/api/pos/products/',
        data: { search: barcode },
        success: function(data) {
            if (data.results && data.results.length > 0) {
                addToCart(data.results[0]);
            } else {
                toastr.error('Product not found');
            }
        },
        error: function() {
            toastr.error('Error searching product');
        }
    });
}

// Transaction management
function holdTransaction() {
    if (cart.length === 0) {
        toastr.warning('Cart is empty');
        return;
    }
    
    const transactionId = 'HOLD-' + Date.now();
    const transaction = {
        id: transactionId,
        items: [...cart],
        customer: {
            name: $('#customer-name').val(),
            phone: $('#customer-phone').val(),
            email: $('#customer-email').val()
        },
        paymentMethod: $('#payment-method-select').val() || 'cash',
        cardNumber: $('#card-number').val() || '',
        payAmount: parseFloat($('#pay-amount').val()) || 0,
        notes: $('#order-notes').val(),
        timestamp: new Date().toISOString(),
        total: calculateTotal()
    };
    
    // Save to localStorage
    const heldTransactions = JSON.parse(localStorage.getItem('pos_held_transactions') || '[]');
    heldTransactions.push(transaction);
    localStorage.setItem('pos_held_transactions', JSON.stringify(heldTransactions));
    
    // Clear current cart
    clearCart();
    
    toastr.success(`Transaction ${transactionId} held successfully`);
    updateHoldListPopover();
    
    // Reload the page to reset all fields and state
    setTimeout(() => {
        location.reload();
    }, 1000); // Wait 1 second to show the success message
}

function calculateTotal() {
    const subtotal = cart.reduce((sum, item) => sum + item.total, 0);
    const fixedDiscount = parseFloat($('#fixed-discount').val()) || 0;
    const percentDiscount = parseFloat($('#percent-discount').val()) || 0;
    const discountAmount = fixedDiscount + (subtotal * percentDiscount / 100);
    const discountedSubtotal = Math.max(0, subtotal - discountAmount);
    const tax = subtotal * 0.075; // 7.5% tax on original subtotal
    return discountedSubtotal + tax;
}

function updateHoldListPopover() {
    const heldTransactions = JSON.parse(localStorage.getItem('pos_held_transactions') || '[]');
    
    let content;
    if (heldTransactions.length === 0) {
        content = '<div class="p-2 text-muted">No held transactions</div>';
    } else {
        content = '<div class="hold-list-popover" style="max-width: 300px; max-height: 400px; overflow-y: auto;">';
        
        heldTransactions.forEach((transaction, index) => {
            const date = new Date(transaction.timestamp).toLocaleString();
            const itemCount = transaction.items.reduce((sum, item) => sum + item.quantity, 0);
            
            content += `
                <div class="hold-item p-2 border-bottom" style="cursor: pointer;" onclick="loadHeldTransaction('${transaction.id}')">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${transaction.id}</strong><br>
                            <small class="text-muted">${date}</small><br>
                            <small>${itemCount} items - ৳${transaction.total.toFixed(2)}</small>
                            ${transaction.customer.name ? `<br><small>Customer: ${transaction.customer.name}</small>` : ''}
                        </div>
                        <button class="btn btn-outline-danger btn-sm" onclick="event.stopPropagation(); deleteHeldTransaction('${transaction.id}')" title="Delete">
                            <i class="ti ti-trash" style="font-size: 12px;"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        content += '</div>';
    }
    
    // Update Bootstrap 5 popover content
    if (window.holdListPopover) {
        // Dispose of the old popover and create a new one with updated content
        window.holdListPopover.dispose();
        const holdListBtn = document.getElementById('hold-list-btn');
        if (holdListBtn) {
            window.holdListPopover = new bootstrap.Popover(holdListBtn, {
                trigger: 'click',
                html: true,
                sanitize: false,
                content: content,
                placement: 'bottom'
            });
        }
    }
}

function loadHeldTransaction(transactionId) {
    const heldTransactions = JSON.parse(localStorage.getItem('pos_held_transactions') || '[]');
    const transaction = heldTransactions.find(t => t.id === transactionId);
    
    if (!transaction) {
        toastr.error('Transaction not found');
        return;
    }
    
    // Save current cart if it has items
    if (cart.length > 0) {
        const currentTransactionId = 'HOLD-' + Date.now();
        const currentTransaction = {
            id: currentTransactionId,
            items: [...cart],
            customer: {
                name: $('#customer-name').val(),
                phone: $('#customer-phone').val(),
                email: $('#customer-email').val()
            },
            paymentMethod: $('#payment-method-select').val() || 'cash',
            cardNumber: $('#card-number').val() || '',
            notes: $('#order-notes').val(),
            timestamp: new Date().toISOString(),
            total: calculateTotal()
        };
        
        const updatedHeldTransactions = JSON.parse(localStorage.getItem('pos_held_transactions') || '[]');
        updatedHeldTransactions.push(currentTransaction);
        localStorage.setItem('pos_held_transactions', JSON.stringify(updatedHeldTransactions));
        
        toastr.info(`Current order saved as ${currentTransactionId}`);
    }
    
    // Load the selected transaction
    cart = [...transaction.items];
    window.cart = cart; // Sync with validation module
    
    // Restore customer information
    $('#customer-name').val(transaction.customer.name || '');
    $('#customer-phone').val(transaction.customer.phone || '');
    $('#customer-email').val(transaction.customer.email || '');
    
    // Restore payment method
    if (transaction.paymentMethod) {
        $('#payment-method-select').val(transaction.paymentMethod);
        window.selectedPaymentMethod = transaction.paymentMethod;
        
        // Show/hide card amount and card number sections based on payment method
        if (transaction.paymentMethod === 'card') {
            $('#card-amount-section').addClass('show');
            $('#card-number-section').show();
            // Restore card number
            $('#card-number').val(transaction.cardNumber || '');
        } else {
            $('#card-amount-section').removeClass('show');
            $('#card-number-section').hide();
            $('#card-number').val('');
        }
    }
    
    // Restore notes
    $('#order-notes').val(transaction.notes || '');
    
    // Restore pay amount
    $('#pay-amount').val(transaction.payAmount || 0);
    
    // Remove the loaded transaction from held transactions
    const remainingTransactions = heldTransactions.filter(t => t.id !== transactionId);
    localStorage.setItem('pos_held_transactions', JSON.stringify(remainingTransactions));
    
    // Update displays
    updateCartDisplay();
    updateHoldListPopover();
    
    // Hide popover
    if (window.holdListPopover) {
        window.holdListPopover.hide();
    }
    
    toastr.success(`Loaded transaction ${transactionId}`);
}

function deleteHeldTransaction(transactionId) {
    const heldTransactions = JSON.parse(localStorage.getItem('pos_held_transactions') || '[]');
    const remainingTransactions = heldTransactions.filter(t => t.id !== transactionId);
    localStorage.setItem('pos_held_transactions', JSON.stringify(remainingTransactions));
    
    updateHoldListPopover();
    toastr.success('Held transaction deleted');
}

function processPayment() {
    if (cart.length === 0) {
        toastr.warning('Cart is empty');
        return;
    }
    
    // Calculate totals for logging
    const subtotal = cart.reduce((sum, item) => sum + item.total, 0);
    const fixedDiscount = parseFloat($('#fixed-discount').val()) || 0;
    const percentDiscount = parseFloat($('#percent-discount').val()) || 0;
    const percentDiscountAmount = subtotal * percentDiscount / 100;
    const totalDiscountAmount = fixedDiscount + percentDiscountAmount;
    const discountedSubtotal = Math.max(0, subtotal - totalDiscountAmount);
    const tax = subtotal * 0.075; // 7.5% tax
    const grandTotal = discountedSubtotal + tax;
    
    // Prepare sale data
    const saleData = {
        customer: {
            name: $('#customer-name').val(),
            phone: $('#customer-phone').val(),
            email: $('#customer-email').val()
        },
        items: cart,
        payment_method: window.selectedPaymentMethod,
        card_number: $('#card-number').val() || '',
        card_amount: parseFloat($('#card-amount').val()) || 0,
        cash_amount: parseFloat($('#cash-amount').text()) || 0,
        pay_amount: parseFloat($('#pay-amount').val()) || 0,
        return_amount: parseFloat($('#return-amount').text().replace('৳', '')) || 0,
        discounts: {
            fixed_discount: fixedDiscount,
            percent_discount: percentDiscount,
            percent_discount_amount: percentDiscountAmount,
            total_discount_amount: totalDiscountAmount
        },
        totals: {
            subtotal: subtotal,
            discounted_subtotal: discountedSubtotal,
            tax_amount: tax,
            grand_total: grandTotal
        },
        header_info: {
            customer_name: $('#header-customer-name').val(),
            customer_phone: $('#header-customer-phone').val(),
            warehouse: $('#header-warehouse').val(),
            salesman: $('#header-salesman').val()
        },
        notes: $('#order-notes').val(),
        timestamp: new Date().toISOString()
    };
    
    // Console logging for debugging
    console.log('=== POS ORDER PROCESSING ===');
    console.log('Complete Sale Data Structure:');
    console.log(JSON.stringify(saleData, null, 2));
    console.log('');
    console.log('=== SUMMARY ===');
    console.log(`Items Count: ${cart.length}`);
    console.log(`Total Quantity: ${cart.reduce((sum, item) => sum + item.quantity, 0)}`);
    console.log(`Subtotal: ৳${subtotal.toFixed(2)}`);
    console.log(`Fixed Discount: ৳${fixedDiscount.toFixed(2)}`);
    console.log(`Percent Discount: ${percentDiscount}% (৳${percentDiscountAmount.toFixed(2)})`);
    console.log(`Total Discount: ৳${totalDiscountAmount.toFixed(2)}`);
    console.log(`Tax (7.5%): ৳${tax.toFixed(2)}`);
    console.log(`Grand Total: ৳${grandTotal.toFixed(2)}`);
    console.log(`Payment Method: ${window.selectedPaymentMethod}`);
    if (window.selectedPaymentMethod === 'card') {
        console.log(`Card Amount: ৳${saleData.card_amount.toFixed(2)}`);
        console.log(`Cash Amount: ৳${saleData.cash_amount.toFixed(2)}`);
        console.log(`Card Number: ${saleData.card_number}`);
    }
    console.log(`Pay Amount: ৳${saleData.pay_amount.toFixed(2)}`);
    console.log(`Return Amount: ৳${saleData.return_amount.toFixed(2)}`);
    console.log('=== END SUMMARY ===');
    
    // Send to server
    $.ajax({
        url: '/sales/api/pos/complete-sale/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(saleData),
        success: function(response) {
            if (response.success) {
                if (response.validation_passed) {
                    toastr.success(`${response.message} Order: ${response.order_number}`);
                } else {
                    toastr.success(`Sale completed! Order: ${response.order_number}`);
                }
                clearCart();
                clearInput(); // Clear all form fields
                // Reset header customer fields to defaults
                $('#header-customer-name').val('CUS-000001');
                $('#header-customer-phone').val('');
                $('#header-warehouse').val('Fixit Gulshan');
                $('#header-salesman').val('Ohidul');
            } else {
                toastr.error(response.error || 'Sale failed');
            }
        },
        error: function(xhr) {
            try {
                const errorResponse = JSON.parse(xhr.responseText);
                
                if (errorResponse.validation_failed && errorResponse.errors) {
                    // Handle inventory validation errors
                    toastr.error(errorResponse.message || 'Inventory validation failed');
                    
                    // Show detailed error for each item with insufficient stock
                    errorResponse.errors.forEach(function(error) {
                        toastr.error(
                            `${error.xitem}: Requested ${error.requested_quantity}, Available ${error.available_stock}`,
                            'Insufficient Stock',
                            { timeOut: 8000 }
                        );
                    });
                } else {
                    toastr.error(errorResponse.error || errorResponse.message || 'Sale failed');
                }
            } catch (e) {
                toastr.error('Error completing sale');
            }
        }
    });
}