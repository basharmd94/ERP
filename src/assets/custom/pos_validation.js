/**
 * POS Validation Module
 * Comprehensive validation system for Point of Sale transactions
 * Author: CodeWeaver AI Assistant
 * Version: 1.0
 */

// Validation Configuration
const VALIDATION_CONFIG = {
    payment: {
        cardNumber: { length: 4, required: true },
        amounts: { min: 0, max: 999999.99, decimals: 2 }
    },
    discount: {
        fixed: { min: 0, max: 999999.99, decimals: 2 },
        percent: { min: 0, max: 100, decimals: 1 }
    },
    product: {
        barcode: { min: 3, max: 20, pattern: /^[A-Z0-9]+$/ },
        quantity: { min: 1, max: 9999 }
    },
    notes: { max: 500 }
};

// Validation State Management
const ValidationState = {
    errors: {},
    isValid: true,
    
    setError(field, message) {
        this.errors[field] = message;
        this.isValid = false;
        this.showFieldError(field, message);
    },
    
    clearError(field) {
        delete this.errors[field];
        this.hideFieldError(field);
        this.updateValidationState();
    },
    
    clearAllErrors() {
        this.errors = {};
        this.isValid = true;
        $('.validation-error').remove();
        $('.is-invalid').removeClass('is-invalid');
    },
    
    updateValidationState() {
        this.isValid = Object.keys(this.errors).length === 0;
    },
    
    showFieldError(field, message) {
        const $field = $(`#${field}`);
        $field.addClass('is-invalid');
        
        // Remove existing error message
        $field.siblings('.validation-error').remove();
        
        // Add new error message
        $field.after(`<div class="validation-error text-danger small mt-1">${message}</div>`);
    },
    
    hideFieldError(field) {
        const $field = $(`#${field}`);
        $field.removeClass('is-invalid');
        $field.siblings('.validation-error').remove();
    }
};

// Core Validation Functions
const Validators = {
    
    // Payment Validators
    validateCardAmount(amount, total) {
        const numAmount = parseFloat(amount) || 0;
        
        if (numAmount < 0) {
            return { valid: false, message: 'Card amount cannot be negative' };
        }
        
        if (numAmount > total) {
            return { valid: false, message: 'Card amount cannot exceed total amount' };
        }
        
        if (numAmount === 0 && window.selectedPaymentMethod === 'card') {
            return { valid: false, message: 'Card amount is required for card payment' };
        }
        
        return { valid: true, value: parseFloat(numAmount.toFixed(2)) };
    },
    
    validateCardNumber(cardNumber) {
        if (!cardNumber || cardNumber.trim().length === 0) {
            if (window.selectedPaymentMethod === 'card') {
                return { valid: false, message: 'Card number is required for card payment' };
            }
            return { valid: true, value: '' };
        }
        
        // Clean card number (remove spaces, dashes)
        const cleanCard = cardNumber.replace(/[\s\-]/g, '');
        
        if (!/^\d{4}$/.test(cleanCard)) {
            return { valid: false, message: 'Card number must be 4 digits' };
        }
        
        return { valid: true, value: cleanCard };
    },
    
    validatePayAmount(amount, total, cardAmount = 0) {
        const numAmount = parseFloat(amount) || 0;
        
        if (numAmount < 0) {
            return { valid: false, message: 'Pay amount cannot be negative' };
        }
        
        // For card payment, validate against cash portion needed
        if (window.selectedPaymentMethod === 'card') {
            const cashNeeded = Math.max(0, total - cardAmount);
            // Allow any amount >= 0 for cash portion (can be less for partial payment)
        } else if (window.selectedPaymentMethod === 'cash') {
            // For cash payment, require full amount
            if (numAmount < total) {
                return { valid: false, message: `Cash payment must be at least ${total.toFixed(2)}` };
            }
        }
        
        return { valid: true, value: parseFloat(numAmount.toFixed(2)) };
    },
    
    validateBankName(bankName) {
        if (!bankName || bankName.trim() === '' || bankName === '-- Select a bank --') {
            if (window.selectedPaymentMethod === 'card') {
                return { valid: false, message: 'Please select a bank for card payment' };
            }
            return { valid: true, value: '' };
        }
        
        return { valid: true, value: bankName.trim() };
    },
    
    // Discount Validators
    validateFixedDiscount(discount, subtotal) {
        const numDiscount = parseFloat(discount) || 0;
        
        if (numDiscount < 0) {
            return { valid: false, message: 'Discount cannot be negative' };
        }
        
        if (numDiscount > subtotal) {
            return { valid: false, message: 'Fixed discount cannot exceed subtotal amount' };
        }
        
        return { valid: true, value: parseFloat(numDiscount.toFixed(2)) };
    },
    
    validatePercentDiscount(percent, subtotal, fixedDiscount = 0) {
        const numPercent = parseFloat(percent) || 0;
        
        if (numPercent < 0) {
            return { valid: false, message: 'Discount percentage cannot be negative' };
        }
        
        if (numPercent > 100) {
            return { valid: false, message: 'Discount percentage cannot exceed 100%' };
        }
        
        // Check if combined discounts exceed subtotal
        const percentAmount = subtotal * numPercent / 100;
        if ((fixedDiscount + percentAmount) > subtotal) {
            return { valid: false, message: 'Combined discounts cannot exceed subtotal' };
        }
        
        return { valid: true, value: parseFloat(numPercent.toFixed(1)) };
    },
    
    // Product Validators
    validateBarcode(barcode) {
        if (!barcode || barcode.trim().length === 0) {
            return { valid: false, message: 'Barcode cannot be empty' };
        }
        
        const cleanBarcode = barcode.trim().toUpperCase();
        
        if (cleanBarcode.length < VALIDATION_CONFIG.product.barcode.min) {
            return { valid: false, message: `Barcode must be at least ${VALIDATION_CONFIG.product.barcode.min} characters` };
        }
        
        if (cleanBarcode.length > VALIDATION_CONFIG.product.barcode.max) {
            return { valid: false, message: `Barcode cannot exceed ${VALIDATION_CONFIG.product.barcode.max} characters` };
        }
        
        if (!VALIDATION_CONFIG.product.barcode.pattern.test(cleanBarcode)) {
            return { valid: false, message: 'Barcode can only contain letters and numbers' };
        }
        
        return { valid: true, value: cleanBarcode };
    },
    
    validateQuantity(quantity, stock) {
        const numQuantity = parseInt(quantity) || 0;
        
        if (numQuantity < VALIDATION_CONFIG.product.quantity.min) {
            return { valid: false, message: `Quantity must be at least ${VALIDATION_CONFIG.product.quantity.min}` };
        }
        
        if (numQuantity > VALIDATION_CONFIG.product.quantity.max) {
            return { valid: false, message: `Quantity cannot exceed ${VALIDATION_CONFIG.product.quantity.max}` };
        }
        
        if (numQuantity > stock) {
            return { valid: false, message: `Only ${stock} items available in stock` };
        }
        
        return { valid: true, value: numQuantity };
    },
    
    // Order Notes Validator
    validateOrderNotes(notes) {
        if (!notes) {
            return { valid: true, value: '' };
        }
        
        if (notes.length > VALIDATION_CONFIG.notes.max) {
            return { valid: false, message: `Notes cannot exceed ${VALIDATION_CONFIG.notes.max} characters` };
        }
        
        // Basic XSS prevention
        const cleanNotes = notes.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
        
        return { valid: true, value: cleanNotes };
    },
    
    // Business Logic Validators
    validateTransaction() {
        const errors = [];
        
        // Check if cart is not empty
        if (!window.cart || window.cart.length === 0) {
            errors.push('Cart cannot be empty');
        }
        
        // Check if total is greater than 0
        const total = window.getCurrentTotal ? window.getCurrentTotal() : 0;
        if (total <= 0) {
            errors.push('Total amount must be greater than 0');
        }
        
        // Check payment method specific validations
        if (window.selectedPaymentMethod === 'card') {
            const cardAmount = parseFloat($('#card-amount').val()) || 0;
            const cardNumber = $('#card-number').val().trim();
            const bankName = $('#bank-name').val();
            
            if (cardAmount === 0) {
                errors.push('Card amount is required for card payment');
            }
            
            if (!cardNumber) {
                errors.push('Card number is required for card payment');
            }
            
            if (!bankName || bankName === '') {
                errors.push('Please select a bank for card payment');
            }
        } else if (window.selectedPaymentMethod === 'cash') {
            const payAmount = parseFloat($('#pay-amount').val()) || 0;
            
            if (payAmount < total) {
                errors.push(`Cash payment amount (${payAmount.toFixed(2)}) must be at least the total amount (${total.toFixed(2)})`);
            }
        }
        

        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    },
    
    // Utility Functions
    luhnCheck(cardNumber) {
        let sum = 0;
        let alternate = false;
        
        for (let i = cardNumber.length - 1; i >= 0; i--) {
            let n = parseInt(cardNumber.charAt(i), 10);
            
            if (alternate) {
                n *= 2;
                if (n > 9) {
                    n = (n % 10) + 1;
                }
            }
            
            sum += n;
            alternate = !alternate;
        }
        
        return (sum % 10) === 0;
    },
    
    formatCurrency(amount) {
        return parseFloat(amount).toFixed(2);
    },
    
    formatPhone(phone) {
        // Format as: 01712-345678
        if (phone.length === 11) {
            return phone.replace(/(\d{5})(\d{6})/, '$1-$2');
        }
        return phone;
    }
};

// Real-time Validation Setup
const ValidationSetup = {
    
    initialize() {
        this.setupPaymentValidation();
        this.setupDiscountValidation();
        this.setupProductValidation();
        this.setupOrderNotesValidation();
        this.setupFormSubmissionValidation();
        
        console.log('POS Validation system initialized');
    },
    

    
    setupPaymentValidation() {
        // Card Amount
        $('#card-amount').on('blur', function() {
            const total = window.getCurrentTotal ? window.getCurrentTotal() : 0;
            const result = Validators.validateCardAmount($(this).val(), total);
            if (!result.valid) {
                ValidationState.setError('card-amount', result.message);
            } else {
                ValidationState.clearError('card-amount');
                $(this).val(result.value);
            }
        });
        
        // Card Number
        $('#card-number').on('blur', function() {
            const result = Validators.validateCardNumber($(this).val());
            if (!result.valid) {
                ValidationState.setError('card-number', result.message);
            } else {
                ValidationState.clearError('card-number');
                $(this).val(result.value);
            }
        });
        
        // Pay Amount
        $('#pay-amount').on('blur', function() {
            const total = window.getCurrentTotal ? window.getCurrentTotal() : 0;
            const cardAmount = parseFloat($('#card-amount').val()) || 0;
            const result = Validators.validatePayAmount($(this).val(), total, cardAmount);
            if (!result.valid) {
                ValidationState.setError('pay-amount', result.message);
            } else {
                ValidationState.clearError('pay-amount');
                $(this).val(result.value);
            }
        });
        
        // Bank Name
        $('#bank-name').on('change', function() {
            const result = Validators.validateBankName($(this).val());
            if (!result.valid) {
                ValidationState.setError('bank-name', result.message);
            } else {
                ValidationState.clearError('bank-name');
            }
        });
    },
    
    setupDiscountValidation() {
        // Fixed Discount
        $('#fixed-discount').on('blur', function() {
            const subtotal = window.cart ? window.cart.reduce((sum, item) => sum + item.total, 0) : 0;
            const result = Validators.validateFixedDiscount($(this).val(), subtotal);
            if (!result.valid) {
                ValidationState.setError('fixed-discount', result.message);
            } else {
                ValidationState.clearError('fixed-discount');
                $(this).val(result.value);
            }
        });
        
        // Percent Discount
        $('#percent-discount').on('blur', function() {
            const subtotal = window.cart ? window.cart.reduce((sum, item) => sum + item.total, 0) : 0;
            const fixedDiscount = parseFloat($('#fixed-discount').val()) || 0;
            const result = Validators.validatePercentDiscount($(this).val(), subtotal, fixedDiscount);
            if (!result.valid) {
                ValidationState.setError('percent-discount', result.message);
            } else {
                ValidationState.clearError('percent-discount');
                $(this).val(result.value);
            }
        });
    },
    
    setupProductValidation() {
        // Barcode Input
        $('#barcode-input').on('input', function() {
            const value = $(this).val().toUpperCase();
            $(this).val(value);
        });
        
        $('#barcode-input').on('blur', function() {
            if ($(this).val().trim()) {
                const result = Validators.validateBarcode($(this).val());
                if (!result.valid) {
                    ValidationState.setError('barcode-input', result.message);
                } else {
                    ValidationState.clearError('barcode-input');
                    $(this).val(result.value);
                }
            }
        });
    },
    
    setupOrderNotesValidation() {
        $('#order-notes').on('blur', function() {
            const result = Validators.validateOrderNotes($(this).val());
            if (!result.valid) {
                ValidationState.setError('order-notes', result.message);
            } else {
                ValidationState.clearError('order-notes');
                $(this).val(result.value);
            }
        });
    },
    
    setupFormSubmissionValidation() {
        // Override processPayment function to include validation
        if (window.processPayment) {
            window.originalProcessPayment = window.processPayment;
            window.processPayment = function() {
                if (ValidationSetup.validateBeforeSubmission()) {
                    window.originalProcessPayment();
                }
            };
        }
        
        // Override holdTransaction function to include validation
        if (window.holdTransaction) {
            window.originalHoldTransaction = window.holdTransaction;
            window.holdTransaction = function() {
                if (ValidationSetup.validateBeforeHold()) {
                    window.originalHoldTransaction();
                }
            };
        }
    },
    
    validateBeforeSubmission() {
        ValidationState.clearAllErrors();
        
        const transactionResult = Validators.validateTransaction();
        if (!transactionResult.valid) {
            transactionResult.errors.forEach(error => {
                toastr.error(error);
            });
            return false;
        }
        
        // Validate all fields
        let allValid = true;
        
        // Payment validation for card
        if (window.selectedPaymentMethod === 'card') {
            const total = window.getCurrentTotal ? window.getCurrentTotal() : 0;
            
            const cardAmount = Validators.validateCardAmount($('#card-amount').val(), total);
            if (!cardAmount.valid) {
                ValidationState.setError('card-amount', cardAmount.message);
                allValid = false;
            }
            
            const cardNumber = Validators.validateCardNumber($('#card-number').val());
            if (!cardNumber.valid) {
                ValidationState.setError('card-number', cardNumber.message);
                allValid = false;
            }
            
            const bankName = Validators.validateBankName($('#bank-name').val());
            if (!bankName.valid) {
                ValidationState.setError('bank-name', bankName.message);
                allValid = false;
            }
        }
        
        if (!allValid) {
            toastr.error('Please fix the validation errors before proceeding');
        }
        
        return allValid;
    },
    
    validateBeforeHold() {
        // Less strict validation for holding transactions
        if (!window.cart || window.cart.length === 0) {
            toastr.warning('Cart is empty');
            return false;
        }
        
        return true;
    }
};

// Public API
window.POSValidation = {
    initialize: () => ValidationSetup.initialize(),
    validate: Validators,
    state: ValidationState,
    config: VALIDATION_CONFIG
};

// Auto-initialize when DOM is ready
$(document).ready(function() {
    // Small delay to ensure other scripts are loaded
    setTimeout(() => {
        if (window.POSValidation) {
            window.POSValidation.initialize();
        }
    }, 500);
});