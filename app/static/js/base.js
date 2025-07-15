/**
 * Phoenix Web Application - Base JavaScript
 * Core functionality and utilities used across the application
 */

(function() {
    'use strict';

    // Global Phoenix namespace
    window.Phoenix = window.Phoenix || {};

    /**
     * Core utility functions
     */
    Phoenix.Utils = {
        /**
         * Make AJAX requests with proper error handling
         * @param {string} url - The URL to make the request to
         * @param {Object} options - Request options
         * @returns {Promise} - Promise that resolves with the response
         */
        async ajax(url, options = {}) {
            const defaults = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };

            // Add CSRF token if available
            if (Phoenix.csrfToken) {
                defaults.headers['X-CSRFToken'] = Phoenix.csrfToken;
            }

            const config = { ...defaults, ...options };

            // Convert data to JSON if it's an object and method is not GET
            if (config.data && config.method !== 'GET') {
                if (config.headers['Content-Type'] === 'application/json') {
                    config.body = JSON.stringify(config.data);
                } else if (config.data instanceof FormData) {
                    config.body = config.data;
                    delete config.headers['Content-Type']; // Let browser set it
                }
                delete config.data;
            }

            try {
                const response = await fetch(url, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }
            } catch (error) {
                console.error('AJAX Error:', error);
                throw error;
            }
        },

        /**
         * Show toast notification
         * @param {string} message - Message to show
         * @param {string} type - Type of notification (success, error, warning, info)
         * @param {number} duration - Duration in milliseconds
         */
        showToast(message, type = 'info', duration = 5000) {
            const toastContainer = this.getToastContainer();
            const toastId = 'toast-' + Date.now();
            
            const iconMap = {
                success: 'fas fa-check-circle',
                error: 'fas fa-exclamation-triangle',
                warning: 'fas fa-exclamation-triangle',
                info: 'fas fa-info-circle'
            };

            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0 phoenix-toast`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="${iconMap[type]} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close" onclick="closeToast(this)"></button>
                </div>
            `;

            toastContainer.appendChild(toast);

            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: duration
            });

            bsToast.show();

            // Remove toast element after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });

            // Auto-close flash message toasts after 5 seconds
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.classList.add('closing');
                    setTimeout(() => {
                        toast.remove();
                    }, 300);
                }
            }, 5000);
        },

        /**
         * Get or create toast container
         * @returns {HTMLElement} Toast container element
         */
        getToastContainer() {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'toast-container position-fixed top-0 end-0 p-3';
                container.style.zIndex = '1060';
                document.body.appendChild(container);
            }
            return container;
        },

        /**
         * Format date to human readable string
         * @param {Date|string} date - Date to format
         * @returns {string} Formatted date string
         */
        formatDate(date) {
            if (!date) return '';
            
            const d = new Date(date);
            const now = new Date();
            const diff = now - d;
            
            // Less than 1 minute
            if (diff < 60000) {
                return 'Just now';
            }
            
            // Less than 1 hour
            if (diff < 3600000) {
                const minutes = Math.floor(diff / 60000);
                return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
            }
            
            // Less than 1 day
            if (diff < 86400000) {
                const hours = Math.floor(diff / 3600000);
                return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
            }
            
            // Less than 1 week
            if (diff < 604800000) {
                const days = Math.floor(diff / 86400000);
                return `${days} day${days !== 1 ? 's' : ''} ago`;
            }
            
            // Default to formatted date
            return d.toLocaleDateString();
        },

        /**
         * Debounce function calls
         * @param {Function} func - Function to debounce
         * @param {number} wait - Wait time in milliseconds
         * @returns {Function} Debounced function
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Throttle function calls
         * @param {Function} func - Function to throttle
         * @param {number} limit - Time limit in milliseconds
         * @returns {Function} Throttled function
         */
        throttle(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        /**
         * Copy text to clipboard
         * @param {string} text - Text to copy
         * @returns {Promise<boolean>} Success status
         */
        async copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                this.showToast('Copied to clipboard!', 'success', 2000);
                return true;
            } catch (err) {
                console.error('Failed to copy to clipboard:', err);
                this.showToast('Failed to copy to clipboard', 'error', 3000);
                return false;
            }
        },

        /**
         * Validate email format
         * @param {string} email - Email to validate
         * @returns {boolean} Is valid email
         */
        isValidEmail(email) {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            return emailRegex.test(email);
        },

        /**
         * Validate URL format
         * @param {string} url - URL to validate
         * @returns {boolean} Is valid URL
         */
        isValidUrl(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        }
    };

    /**
     * Form handling utilities
     */
    Phoenix.Forms = {
        /**
         * Initialize form validation
         * @param {HTMLFormElement} form - Form element to validate
         */
        initValidation(form) {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });

            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });

                input.addEventListener('input', Phoenix.Utils.debounce(() => {
                    this.validateField(input);
                }, 300));
            });
        },

        /**
         * Validate individual form field
         * @param {HTMLElement} field - Form field to validate
         */
        validateField(field) {
            const isValid = field.checkValidity();
            
            if (isValid) {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            } else {
                field.classList.remove('is-valid');
                field.classList.add('is-invalid');
            }
        },

        /**
         * Set loading state for form
         * @param {HTMLFormElement} form - Form element
         * @param {boolean} loading - Loading state
         */
        setLoading(form, loading = true) {
            const submitButton = form.querySelector('button[type="submit"]');
            const inputs = form.querySelectorAll('input, textarea, select, button');
            
            if (loading) {
                form.classList.add('loading');
                inputs.forEach(input => input.disabled = true);
                
                if (submitButton) {
                    submitButton.dataset.originalText = submitButton.innerHTML;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                }
            } else {
                form.classList.remove('loading');
                inputs.forEach(input => input.disabled = false);
                
                if (submitButton && submitButton.dataset.originalText) {
                    submitButton.innerHTML = submitButton.dataset.originalText;
                }
            }
        }
    };

    /**
     * UI utilities
     */
    Phoenix.UI = {
        /**
         * Initialize back to top button
         */
        initBackToTop() {
            const backToTopButton = document.getElementById('backToTop');
            if (!backToTopButton) return;

            const toggleVisibility = Phoenix.Utils.throttle(() => {
                if (window.pageYOffset > 300) {
                    backToTopButton.classList.remove('d-none');
                } else {
                    backToTopButton.classList.add('d-none');
                }
            }, 100);

            window.addEventListener('scroll', toggleVisibility);

            backToTopButton.addEventListener('click', () => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        },

        /**
         * Initialize keyboard shortcuts
         */
        initKeyboardShortcuts() {
            document.addEventListener('keydown', (event) => {
                // Help modal: ?
                if (event.key === '?' && !event.ctrlKey && !event.metaKey) {
                    const helpModal = document.getElementById('helpModal');
                    if (helpModal) {
                        event.preventDefault();
                        const modal = new bootstrap.Modal(helpModal);
                        modal.show();
                    }
                }

                // Search: Ctrl+K
                if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                    event.preventDefault();
                    const searchInput = document.querySelector('input[type="search"]');
                    if (searchInput) {
                        searchInput.focus();
                    }
                }

                // Close modals: Escape
                if (event.key === 'Escape') {
                    const openModals = document.querySelectorAll('.modal.show');
                    openModals.forEach(modal => {
                        const bsModal = bootstrap.Modal.getInstance(modal);
                        if (bsModal) {
                            bsModal.hide();
                        }
                    });
                }
            });
        },

        /**
         * Initialize tooltips and popovers
         */
        initTooltips() {
            // Initialize Bootstrap tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            // Initialize Bootstrap popovers
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
        },

        /**
         * Initialize loading animations
         */
        initLoadingAnimations() {
            // Fade in elements when they come into view
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            // Observe elements with fade-in class
            document.querySelectorAll('.fade-in-on-scroll').forEach(el => {
                observer.observe(el);
            });
        }
    };

    /**
     * Initialize application when DOM is ready
     */
    function init() {
        // Ensure Phoenix object and its properties are available
        if (!Phoenix || !Phoenix.UI) {
            console.error('Phoenix object not properly initialized');
            return;
        }

        try {
            // Initialize UI components
            if (typeof Phoenix.UI.initBackToTop === 'function') {
                Phoenix.UI.initBackToTop();
            }
            if (typeof Phoenix.UI.initKeyboardShortcuts === 'function') {
                Phoenix.UI.initKeyboardShortcuts();
            }
            if (typeof Phoenix.UI.initTooltips === 'function') {
                Phoenix.UI.initTooltips();
            }
            if (typeof Phoenix.UI.initLoadingAnimations === 'function') {
                Phoenix.UI.initLoadingAnimations();
            }
        } catch (error) {
            console.error('Error initializing Phoenix UI components:', error);
        }

        // Initialize form validation for all forms
        try {
            document.querySelectorAll('form[data-validate]').forEach(form => {
                if (Phoenix.Forms && typeof Phoenix.Forms.initValidation === 'function') {
                    Phoenix.Forms.initValidation(form);
                }
            });
        } catch (error) {
            console.error('Error initializing form validation:', error);
        }

        // Debug mode indicator
        if (Phoenix.debug) {
            console.log('🔥 Phoenix application initialized in debug mode');
            
            // Add debug styles
            document.body.classList.add('debug-mode');
        }

        // Trigger custom initialization event
        document.dispatchEvent(new CustomEvent('phoenix:initialized'));
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

// Global function for closing toast notifications (used in base.html)
function closeToast(button) {
    const toast = button.closest('.phoenix-toast');
    if (toast) {
        toast.classList.add('closing');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

// Auto-close flash message toasts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const toasts = document.querySelectorAll('.phoenix-toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('closing');
                setTimeout(() => {
                    toast.remove();
                }, 300);
            }
        }, 5000);
    });
});