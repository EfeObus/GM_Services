// GM Services Main JavaScript

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    $('.alert:not(.alert-permanent)').delay(5000).fadeOut('slow');

    // Form validation
    $('.needs-validation').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // Password strength indicator
    $('#password').on('input', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        updatePasswordStrengthIndicator(strength);
    });

    // Confirm password validation
    $('#confirm_password').on('input', function() {
        const password = $('#password').val();
        const confirmPassword = $(this).val();
        
        if (password !== confirmPassword) {
            this.setCustomValidity('Passwords do not match');
        } else {
            this.setCustomValidity('');
        }
    });

    // Search functionality
    $('#search-input').on('input', debounce(function() {
        const query = $(this).val();
        if (query.length >= 2) {
            performSearch(query);
        } else {
            hideSearchResults();
        }
    }, 300));

    // File upload handling
    $('.file-upload-area').on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });

    $('.file-upload-area').on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });

    $('.file-upload-area').on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        const files = e.originalEvent.dataTransfer.files;
        handleFileUpload(files);
    });

    // Dynamic form fields
    $('.add-field-btn').on('click', function() {
        const template = $(this).data('template');
        const container = $(this).data('container');
        addFormField(template, container);
    });

    $(document).on('click', '.remove-field-btn', function() {
        $(this).closest('.dynamic-field').remove();
    });

    // AJAX form submission
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        submitAjaxForm($(this));
    });

    // Live chat toggle
    $('#chat-toggle').on('click', function() {
        $('#chat-widget').toggle();
        if ($('#chat-widget').is(':visible')) {
            connectToChat();
        }
    });

    // Status update functionality
    $('.status-update-btn').on('click', function() {
        const itemId = $(this).data('id');
        const currentStatus = $(this).data('status');
        showStatusUpdateModal(itemId, currentStatus);
    });

    // Data tables initialization
    if ($('.data-table').length) {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search records:",
                lengthMenu: "Show _MENU_ records per page",
                info: "Showing _START_ to _END_ of _TOTAL_ records",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    }

    // Dashboard widgets
    initializeDashboardWidgets();

    // Real-time notifications
    if (typeof socket !== 'undefined') {
        initializeNotifications();
    }
});

// Password strength calculation
function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 6) strength += 1;
    if (password.length >= 10) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    return strength;
}

// Update password strength indicator
function updatePasswordStrengthIndicator(strength) {
    const indicator = $('#password-strength');
    const progressBar = indicator.find('.progress-bar');
    
    let percentage = 0;
    let className = '';
    let text = '';
    
    switch(strength) {
        case 0:
        case 1:
            percentage = 20;
            className = 'bg-danger';
            text = 'Very Weak';
            break;
        case 2:
            percentage = 40;
            className = 'bg-warning';
            text = 'Weak';
            break;
        case 3:
            percentage = 60;
            className = 'bg-info';
            text = 'Fair';
            break;
        case 4:
            percentage = 80;
            className = 'bg-primary';
            text = 'Good';
            break;
        case 5:
        case 6:
            percentage = 100;
            className = 'bg-success';
            text = 'Strong';
            break;
    }
    
    progressBar.removeClass('bg-danger bg-warning bg-info bg-primary bg-success')
              .addClass(className)
              .css('width', percentage + '%')
              .text(text);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality
function performSearch(query) {
    $.ajax({
        url: '/services/api/search',
        method: 'GET',
        data: { q: query, limit: 5 },
        success: function(data) {
            displaySearchResults(data);
        },
        error: function() {
            console.error('Search failed');
        }
    });
}

function displaySearchResults(results) {
    const resultsContainer = $('#search-results');
    resultsContainer.empty();
    
    if (results.length === 0) {
        resultsContainer.append('<div class="search-result-item">No results found</div>');
    } else {
        results.forEach(function(result) {
            const item = $(`
                <div class="search-result-item">
                    <a href="/services/${result.id}" class="text-decoration-none">
                        <strong>${result.name}</strong>
                        <br>
                        <small class="text-muted">${result.category} - $${result.price}</small>
                    </a>
                </div>
            `);
            resultsContainer.append(item);
        });
    }
    
    resultsContainer.show();
}

function hideSearchResults() {
    $('#search-results').hide();
}

// File upload handling
function handleFileUpload(files) {
    const formData = new FormData();
    
    for (let i = 0; i < files.length; i++) {
        formData.append('files[]', files[i]);
    }
    
    $.ajax({
        url: '/upload',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            handleUploadSuccess(response);
        },
        error: function() {
            showAlert('Upload failed', 'danger');
        }
    });
}

function handleUploadSuccess(response) {
    if (response.success) {
        showAlert('Files uploaded successfully', 'success');
        // Update UI with uploaded files
        response.files.forEach(function(file) {
            addUploadedFileToList(file);
        });
    } else {
        showAlert(response.message || 'Upload failed', 'danger');
    }
}

// Dynamic form fields
function addFormField(template, container) {
    const fieldHtml = $(template).html();
    const fieldCount = $(container + ' .dynamic-field').length;
    const newField = fieldHtml.replace(/\[INDEX\]/g, fieldCount);
    $(container).append(newField);
}

// AJAX form submission
function submitAjaxForm(form) {
    const submitBtn = form.find('button[type="submit"]');
    const originalText = submitBtn.text();
    
    submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Processing...');
    
    $.ajax({
        url: form.attr('action') || window.location.href,
        method: form.attr('method') || 'POST',
        data: form.serialize(),
        success: function(response) {
            handleFormSuccess(response, form);
        },
        error: function(xhr) {
            handleFormError(xhr, form);
        },
        complete: function() {
            submitBtn.prop('disabled', false).text(originalText);
        }
    });
}

function handleFormSuccess(response, form) {
    if (response.success) {
        showAlert(response.message || 'Operation completed successfully', 'success');
        if (response.redirect) {
            window.location.href = response.redirect;
        } else if (response.reload) {
            window.location.reload();
        }
    } else {
        showAlert(response.message || 'Operation failed', 'danger');
    }
}

function handleFormError(xhr, form) {
    let message = 'An error occurred';
    
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    }
    
    showAlert(message, 'danger');
}

// Alert system
function showAlert(message, type = 'info', timeout = 5000) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('#alert-container').append(alertHtml);
    
    if (timeout > 0) {
        setTimeout(function() {
            $('#alert-container .alert:last').fadeOut('slow', function() {
                $(this).remove();
            });
        }, timeout);
    }
}

// Status update modal
function showStatusUpdateModal(itemId, currentStatus) {
    $('#status-update-modal').modal('show');
    $('#status-item-id').val(itemId);
    $('#status-select').val(currentStatus);
}

// Dashboard widgets
function initializeDashboardWidgets() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Real-time data updates
    setInterval(updateDashboardData, 30000); // Update every 30 seconds
}

function initializeCharts() {
    // Example chart initialization
    const ctx = document.getElementById('dashboardChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Service Requests',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: 'rgb(13, 110, 253)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

function updateDashboardData() {
    $.ajax({
        url: '/api/dashboard-data',
        method: 'GET',
        success: function(data) {
            updateDashboardWidgets(data);
        },
        error: function() {
            console.log('Failed to update dashboard data');
        }
    });
}

function updateDashboardWidgets(data) {
    // Update dashboard statistics
    Object.keys(data).forEach(function(key) {
        const element = $(`[data-stat="${key}"]`);
        if (element.length) {
            element.text(data[key]);
        }
    });
}

// Real-time notifications
function initializeNotifications() {
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    // Socket event listeners
    socket.on('notification', function(data) {
        showNotification(data);
    });
    
    socket.on('status_update', function(data) {
        updateItemStatus(data);
    });
}

function showNotification(data) {
    // Show in-app notification
    const notificationHtml = `
        <div class="notification-item alert alert-info alert-dismissible fade show">
            <strong>${data.title}</strong>
            <p class="mb-0">${data.message}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('#notification-container').prepend(notificationHtml);
    
    // Show browser notification if permitted
    if (Notification.permission === 'granted') {
        new Notification(data.title, {
            body: data.message,
            icon: '/static/images/logo.png'
        });
    }
}

function updateItemStatus(data) {
    const statusElement = $(`[data-status-id="${data.id}"]`);
    if (statusElement.length) {
        statusElement.removeClass('badge-warning badge-info badge-success badge-danger')
                   .addClass(`badge-${data.status_class}`)
                   .text(data.status_text);
    }
}

// Utility functions
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ==================== SERVICE REQUEST FUNCTIONALITY ====================

// Service Request Form Handler
class ServiceRequestForm {
    constructor() {
        this.form = document.getElementById('serviceRequestForm');
        this.requestTypeSelect = document.getElementById('request_type_id');
        this.stateSelect = document.getElementById('customer_state');
        this.lgaSelect = document.getElementById('customer_lga');
        this.subjectInput = document.getElementById('subject');
        this.descriptionTextarea = document.getElementById('description');
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        this.bindEvents();
        this.setupValidation();
        this.loadStatesIfNeeded();
    }
    
    bindEvents() {
        // Request type change handler
        if (this.requestTypeSelect) {
            this.requestTypeSelect.addEventListener('change', (e) => {
                this.handleRequestTypeChange(e);
            });
        }
        
        // State change handler for LGA loading
        if (this.stateSelect) {
            this.stateSelect.addEventListener('change', (e) => {
                this.loadLGAs(e.target.value);
            });
        }
        
        // Form submission handler
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        }
        
        // Real-time validation
        const requiredInputs = this.form.querySelectorAll('input[required], select[required], textarea[required]');
        requiredInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }
    
    handleRequestTypeChange(event) {
        const selectedOption = event.target.selectedOptions[0];
        if (!selectedOption) return;
        
        const description = selectedOption.getAttribute('data-description');
        const category = selectedOption.getAttribute('data-category');
        const requiredFields = JSON.parse(selectedOption.getAttribute('data-required-fields') || '[]');
        const optionalFields = JSON.parse(selectedOption.getAttribute('data-optional-fields') || '[]');
        
        // Update description
        const descriptionDiv = document.getElementById('requestTypeDescription');
        if (descriptionDiv) {
            descriptionDiv.textContent = description || '';
            descriptionDiv.style.display = description ? 'block' : 'none';
        }
        
        // Update form fields based on requirements
        this.updateFormFieldRequirements(requiredFields, optionalFields);
        
        // Auto-suggest subject based on category
        if (category && this.subjectInput && !this.subjectInput.value) {
            this.suggestSubject(category);
        }
    }
    
    updateFormFieldRequirements(requiredFields, optionalFields) {
        const allFields = ['customer_phone', 'customer_address', 'related_service'];
        
        allFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            const label = document.querySelector(`label[for="${fieldName}"]`);
            
            if (field && label) {
                const isRequired = requiredFields.includes(fieldName);
                field.required = isRequired;
                
                // Update label to show/hide required indicator
                const requiredSpan = label.querySelector('.required');
                if (isRequired && !requiredSpan) {
                    label.innerHTML += ' <span class="required">*</span>';
                } else if (!isRequired && requiredSpan) {
                    requiredSpan.remove();
                }
            }
        });
    }
    
    suggestSubject(category) {
        const suggestions = {
            'inquiry': 'General inquiry about services',
            'quote_request': 'Request for service quotation',
            'complaint': 'Service complaint',
            'support': 'Technical support needed'
        };
        
        if (suggestions[category]) {
            this.subjectInput.placeholder = suggestions[category];
        }
    }
    
    loadLGAs(stateName) {
        if (!stateName || !this.lgaSelect) return;
        
        // Get state ID from the selected option
        const selectedOption = this.stateSelect.selectedOptions[0];
        const stateId = selectedOption.getAttribute('data-state-id');
        
        if (!stateId) return;
        
        // Show loading state
        this.lgaSelect.innerHTML = '<option value="">Loading LGAs...</option>';
        this.lgaSelect.disabled = true;
        
        // Fetch LGAs
        fetch(`/services/api/states/${stateId}/lgas`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to load LGAs');
                return response.json();
            })
            .then(lgas => {
                this.populateLGAs(lgas);
            })
            .catch(error => {
                console.error('Error loading LGAs:', error);
                this.lgaSelect.innerHTML = '<option value="">Error loading LGAs</option>';
                showAlert('Failed to load local government areas. Please try again.', 'warning');
            });
    }
    
    populateLGAs(lgas) {
        this.lgaSelect.innerHTML = '<option value="">Select LGA...</option>';
        
        lgas.forEach(lga => {
            const option = document.createElement('option');
            option.value = lga.name;
            option.textContent = `${lga.name}${lga.headquarters ? ` (${lga.headquarters})` : ''}`;
            this.lgaSelect.appendChild(option);
        });
        
        this.lgaSelect.disabled = false;
    }
    
    loadStatesIfNeeded() {
        // If states dropdown is empty, load them via API
        if (this.stateSelect && this.stateSelect.options.length <= 1) {
            fetch('/services/api/states')
                .then(response => response.json())
                .then(states => {
                    states.forEach(state => {
                        const option = document.createElement('option');
                        option.value = state.name;
                        option.setAttribute('data-state-id', state.id);
                        option.textContent = `${state.name} (${state.zone})`;
                        this.stateSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error loading states:', error);
                });
        }
    }
    
    validateField(field) {
        const isValid = field.checkValidity();
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
        
        return isValid;
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        if (field.value.trim()) {
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
        }
    }
    
    setupValidation() {
        // Email validation
        const emailField = document.getElementById('customer_email');
        if (emailField) {
            emailField.addEventListener('blur', () => {
                if (emailField.value && !this.isValidEmail(emailField.value)) {
                    emailField.setCustomValidity('Please enter a valid email address');
                } else {
                    emailField.setCustomValidity('');
                }
                this.validateField(emailField);
            });
        }
        
        // Phone validation
        const phoneField = document.getElementById('customer_phone');
        if (phoneField) {
            phoneField.addEventListener('input', (e) => {
                // Format phone number as user types
                let value = e.target.value.replace(/\D/g, '');
                if (value.startsWith('234')) {
                    value = '+' + value;
                } else if (value.startsWith('0')) {
                    value = '+234' + value.substring(1);
                } else if (value.length > 0 && !value.startsWith('+')) {
                    value = '+234' + value;
                }
                e.target.value = value;
            });
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    handleFormSubmit(event) {
        const requiredFields = this.form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        // Validate all required fields
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            showAlert('Please fill in all required fields correctly.', 'error');
            
            // Focus on first invalid field
            const firstInvalid = this.form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }
        
        // Show loading state
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Submitting...';
            submitBtn.disabled = true;
            
            // Reset button after timeout (in case form submission fails)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 10000);
        }
    }
}

// Request Tracking Functionality
class RequestTracker {
    constructor() {
        this.trackForm = document.getElementById('trackForm');
        this.requestNumberInput = document.getElementById('request_number');
        
        this.init();
    }
    
    init() {
        if (!this.trackForm) return;
        
        this.bindEvents();
        this.setupValidation();
    }
    
    bindEvents() {
        if (this.requestNumberInput) {
            this.requestNumberInput.addEventListener('input', (e) => {
                this.formatRequestNumber(e);
            });
            
            // Auto-focus on page load
            this.requestNumberInput.focus();
        }
        
        if (this.trackForm) {
            this.trackForm.addEventListener('submit', (e) => {
                this.handleTrackSubmit(e);
            });
        }
    }
    
    formatRequestNumber(event) {
        let value = event.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        event.target.value = value;
    }
    
    setupValidation() {
        if (this.requestNumberInput) {
            this.requestNumberInput.addEventListener('blur', () => {
                const value = this.requestNumberInput.value.trim();
                if (value && !this.isValidRequestNumber(value)) {
                    this.requestNumberInput.setCustomValidity('Please enter a valid request number (e.g., SR240919ABC123)');
                } else {
                    this.requestNumberInput.setCustomValidity('');
                }
            });
        }
    }
    
    isValidRequestNumber(requestNumber) {
        // Basic validation for request number format
        const pattern = /^SR\d{6}[A-Z0-9]{6}$/;
        return pattern.test(requestNumber);
    }
    
    handleTrackSubmit(event) {
        const requestNumber = this.requestNumberInput.value.trim();
        
        if (!requestNumber) {
            event.preventDefault();
            showAlert('Please enter a request number.', 'error');
            this.requestNumberInput.focus();
            return;
        }
        
        if (!this.isValidRequestNumber(requestNumber)) {
            event.preventDefault();
            showAlert('Please enter a valid request number format.', 'error');
            this.requestNumberInput.focus();
            return;
        }
    }
}

// Status Auto-refresh for Request Status Page
class StatusAutoRefresh {
    constructor() {
        this.isActive = false;
        this.interval = null;
        this.refreshRate = 30000; // 30 seconds
        
        this.init();
    }
    
    init() {
        // Only auto-refresh on request status pages for active requests
        const isStatusPage = window.location.pathname.includes('/request/track');
        const statusElement = document.querySelector('.status-badge');
        
        if (isStatusPage && statusElement) {
            const status = statusElement.textContent.trim().toLowerCase();
            const activeStatuses = ['submitted', 'assigned', 'in progress'];
            
            if (activeStatuses.some(s => status.includes(s))) {
                this.startAutoRefresh();
            }
        }
    }
    
    startAutoRefresh() {
        this.isActive = true;
        this.interval = setInterval(() => {
            if (!document.hidden) {
                this.refreshStatus();
            }
        }, this.refreshRate);
        
        // Stop auto-refresh when page becomes hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.resumeAutoRefresh();
            }
        });
    }
    
    pauseAutoRefresh() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }
    
    resumeAutoRefresh() {
        if (this.isActive && !this.interval) {
            this.startAutoRefresh();
        }
    }
    
    refreshStatus() {
        // Simple page reload for now
        // In production, this could be an AJAX request to update only the status
        window.location.reload();
    }
}

// Copy to Clipboard Functionality
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert(successMessage, 'success');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            fallbackCopyTextToClipboard(text, successMessage);
        });
    } else {
        fallbackCopyTextToClipboard(text, successMessage);
    }
}

function fallbackCopyTextToClipboard(text, successMessage) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert(successMessage, 'success');
    } catch (err) {
        console.error('Fallback: Could not copy text: ', err);
        showAlert('Copy failed. Please select and copy manually.', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Initialize Service Request Components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize service request form
    if (document.getElementById('serviceRequestForm')) {
        new ServiceRequestForm();
    }
    
    // Initialize request tracker
    if (document.getElementById('trackForm')) {
        new RequestTracker();
    }
    
    // Initialize status auto-refresh
    new StatusAutoRefresh();
    
    // Add click-to-copy functionality for request numbers
    const requestNumbers = document.querySelectorAll('.request-number, .request-number-display');
    requestNumbers.forEach(element => {
        if (element.textContent.trim().match(/^SR\d{6}[A-Z0-9]{6}$/)) {
            element.style.cursor = 'pointer';
            element.title = 'Click to copy request number';
            
            element.addEventListener('click', function() {
                copyToClipboard(this.textContent.trim(), 'Request number copied!');
            });
        }
    });
});

// Export functions for global use
window.GMServices = {
    showAlert: showAlert,
    formatCurrency: formatCurrency,
    formatDate: formatDate,
    formatDateTime: formatDateTime,
    submitAjaxForm: submitAjaxForm,
    copyToClipboard: copyToClipboard,
    ServiceRequestForm: ServiceRequestForm,
    RequestTracker: RequestTracker
};