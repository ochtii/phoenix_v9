/**
 * Phoenix Login Page JavaScript
 * Handles login form functionality and validation
 */

(function() {
    'use strict';

    let loginForm;
    let usernameEmailInput;
    let passwordInput;
    let togglePasswordButton;
    let rememberMeCheckbox;

    /**
     * Initialize login page functionality
     */
    function init() {
        // Get form elements
        loginForm = document.querySelector('.login-form');
        usernameEmailInput = document.getElementById('username_or_email');
        passwordInput = document.getElementById('password');
        togglePasswordButton = document.getElementById('togglePassword');
        rememberMeCheckbox = document.getElementById('remember_me');

        if (!loginForm) return;

        // Initialize components
        initFormValidation();
        initPasswordToggle();
        initFormSubmission();
        initKeyboardShortcuts();
        initAutoFocus();
        initRememberCredentials();
    }

    /**
     * Initialize form validation
     */
    function initFormValidation() {
        // Real-time validation
        usernameEmailInput.addEventListener('input', validateUsernameOrEmail);
        usernameEmailInput.addEventListener('blur', validateUsernameOrEmail);
        
        passwordInput.addEventListener('input', validatePassword);
        passwordInput.addEventListener('blur', validatePassword);

        // Form submission validation
        loginForm.addEventListener('submit', handleFormSubmit);
    }

    /**
     * Validate username or email field
     */
    function validateUsernameOrEmail() {
        const value = usernameEmailInput.value.trim();
        const isValid = value.length >= 3;
        
        updateFieldValidation(usernameEmailInput, isValid, 
            isValid ? '' : 'Please enter a valid username or email');
    }

    /**
     * Validate password field
     */
    function validatePassword() {
        const value = passwordInput.value;
        const isValid = value.length >= 1;
        
        updateFieldValidation(passwordInput, isValid, 
            isValid ? '' : 'Please enter your password');
    }

    /**
     * Update field validation state
     * @param {HTMLElement} field - Form field element
     * @param {boolean} isValid - Validation state
     * @param {string} errorMessage - Error message to display
     */
    function updateFieldValidation(field, isValid, errorMessage = '') {
        const feedback = field.parentElement.querySelector('.invalid-feedback');
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else if (field.value.length > 0 || field.classList.contains('was-validated')) {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (feedback && errorMessage) {
                feedback.textContent = errorMessage;
            }
        }
    }

    /**
     * Initialize form submission handling
     */
    function initFormSubmission() {
        if (!loginForm) return;
        
        // Handle form submission
        loginForm.addEventListener('submit', handleFormSubmit);
        
        // Prevent double submission
        loginForm.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                setTimeout(() => {
                    submitButton.disabled = false;
                }, 2000); // Re-enable after 2 seconds
            }
        });
    }

    /**
     * Initialize password toggle functionality
     */
    function initPasswordToggle() {
        if (!togglePasswordButton) return;

        togglePasswordButton.addEventListener('click', function() {
            const isPassword = passwordInput.type === 'password';
            const icon = this.querySelector('i');
            
            // Toggle password visibility
            passwordInput.type = isPassword ? 'text' : 'password';
            
            // Update icon
            icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
            
            // Update button title
            this.title = isPassword ? 'Hide password' : 'Show password';
            
            // Brief focus on password field
            passwordInput.focus();
            
            // Add visual feedback
            this.classList.add('active');
            setTimeout(() => this.classList.remove('active'), 150);
        });
    }

    /**
     * Handle form submission
     * @param {Event} event - Submit event
     */
    function handleFormSubmit(event) {
        event.preventDefault();
        
        console.log('Login form submission started');
        console.log('Form elements at submission:');
        console.log('usernameEmailInput:', usernameEmailInput);
        console.log('passwordInput:', passwordInput);
        console.log('Username/Email value:', usernameEmailInput ? usernameEmailInput.value : 'null');
        console.log('Password value:', passwordInput ? passwordInput.value : 'null');
        
        // Validate all fields
        validateUsernameOrEmail();
        validatePassword();
        
        // Check if form is valid
        const isFormValid = loginForm.checkValidity();
        loginForm.classList.add('was-validated');
        
        if (!isFormValid) {
            // Focus on first invalid field
            const firstInvalidField = loginForm.querySelector('.is-invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
                // Shake animation for visual feedback
                firstInvalidField.classList.add('animate__animated', 'animate__shakeX');
                setTimeout(() => {
                    firstInvalidField.classList.remove('animate__animated', 'animate__shakeX');
                }, 1000);
            }
            return;
        }

        // Set loading state
        Phoenix.Forms.setLoading(loginForm, true);

        // Prepare form data
        const formData = new FormData(loginForm);
        
        console.log('Creating FormData from form:', loginForm);
        console.log('FormData contents:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // If FormData is empty, create it manually
        if (Array.from(formData.entries()).length === 0) {
            console.log('FormData is empty, creating manually...');
            formData.append('username_or_email', usernameEmailInput ? usernameEmailInput.value : '');
            formData.append('password', passwordInput ? passwordInput.value : '');
            formData.append('remember_me', rememberMeCheckbox && rememberMeCheckbox.checked ? 'on' : '');
            
            console.log('Manual FormData contents:');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
        }
        
        // Submit form via AJAX
        submitLoginForm(formData);
    }

    /**
     * Submit login form via AJAX
     * @param {FormData} formData - Form data to submit
     */
    async function submitLoginForm(formData) {
        try {
            console.log('submitLoginForm called');
            console.log('FormData object:', formData);
            
            // Get form action URL, fallback to current path
            const actionUrl = loginForm.action || `${window.location.origin}/user/login`;
            console.log('Form action URL:', actionUrl);
            
            // Debug: Check if FormData has entries
            const hasEntries = Array.from(formData.entries()).length > 0;
            console.log('FormData has entries:', hasEntries);
            
            // Get CSRF token if available
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                             document.querySelector('input[name="csrf_token"]')?.value;
            
            const headers = {
                'X-Requested-With': 'XMLHttpRequest'
            };
            
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            const response = await fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: headers,
                credentials: 'same-origin' // Include cookies for session
            });

            if (response.ok) {
                // Check if response is JSON (AJAX) or HTML (redirect)
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {
                    const result = await response.json();
                    
                    if (result.success) {
                        Phoenix.Utils.showToast('Login successful! Redirecting...', 'success');
                        
                        // Save credentials if remember me is checked
                        if (rememberMeCheckbox && rememberMeCheckbox.checked) {
                            saveCredentials();
                        }
                        
                        // Redirect after short delay
                        setTimeout(() => {
                            window.location.href = result.redirect_url || '/start';
                        }, 1000);
                    } else {
                        throw new Error(result.message || 'Login failed');
                    }
                } else {
                    // Handle HTML response (probably a redirect)
                    const text = await response.text();
                    
                    // Check if it contains error messages
                    if (text.includes('alert-danger') || text.includes('error')) {
                        // Extract error message from HTML
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(text, 'text/html');
                        const errorAlert = doc.querySelector('.alert-danger');
                        const errorMessage = errorAlert ? errorAlert.textContent.trim() : 'Login failed';
                        
                        throw new Error(errorMessage);
                    } else {
                        // Successful login, redirect
                        Phoenix.Utils.showToast('Login successful! Redirecting...', 'success');
                        
                        if (rememberMeCheckbox && rememberMeCheckbox.checked) {
                            saveCredentials();
                        }
                        
                        setTimeout(() => {
                            window.location.href = '/start';
                        }, 1000);
                    }
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Login error:', error);
            
            // Handle different types of errors
            let errorMessage = 'Login failed. Please try again.';
            let shouldFallback = false;
            
            if (error.name === 'TypeError' && error.message.includes('NetworkError')) {
                errorMessage = 'Network connection failed. Falling back to standard form submission.';
                shouldFallback = true;
            } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Unable to connect to server. Falling back to standard form submission.';
                shouldFallback = true;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            if (shouldFallback) {
                // Show toast and submit form normally
                Phoenix.Utils.showToast(errorMessage, 'warning');
                setTimeout(() => {
                    loginForm.submit();
                }, 1000);
            } else {
                Phoenix.Utils.showToast(errorMessage, 'error');
                
                // Shake the form for visual feedback
                loginForm.classList.add('animate__animated', 'animate__shakeX');
                setTimeout(() => {
                    loginForm.classList.remove('animate__animated', 'animate__shakeX');
                }, 1000);
            }
            
        } finally {
            // Remove loading state
            Phoenix.Forms.setLoading(loginForm, false);
        }
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(event) {
            // Enter key submits form when focused on any input
            if (event.key === 'Enter' && (event.target === usernameEmailInput || event.target === passwordInput)) {
                event.preventDefault();
                // Call handleFormSubmit directly instead of dispatching untrusted event
                handleFormSubmit(event);
            }
            
            // Tab between fields
            if (event.key === 'Tab' && event.target === usernameEmailInput && !event.shiftKey) {
                event.preventDefault();
                passwordInput.focus();
            }
        });
    }

    /**
     * Initialize auto-focus functionality
     */
    function initAutoFocus() {
        // Focus on username field when page loads
        if (usernameEmailInput && !usernameEmailInput.value) {
            // Delay focus to ensure page is fully loaded
            setTimeout(() => {
                usernameEmailInput.focus();
            }, 100);
        } else if (passwordInput && usernameEmailInput.value && !passwordInput.value) {
            setTimeout(() => {
                passwordInput.focus();
            }, 100);
        }
    }

    /**
     * Initialize remember credentials functionality
     */
    function initRememberCredentials() {
        // Load saved credentials if available
        loadSavedCredentials();
        
        // Clear saved credentials if remember me is unchecked
        if (rememberMeCheckbox) {
            rememberMeCheckbox.addEventListener('change', function() {
                if (!this.checked) {
                    clearSavedCredentials();
                }
            });
        }
    }

    /**
     * Save user credentials to localStorage (only username/email, not password)
     */
    function saveCredentials() {
        if (!rememberMeCheckbox || !rememberMeCheckbox.checked) return;
        
        const credentials = {
            usernameOrEmail: usernameEmailInput.value.trim(),
            rememberMe: true,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem('phoenix_login_credentials', JSON.stringify(credentials));
        } catch (error) {
            console.warn('Failed to save credentials:', error);
        }
    }

    /**
     * Load saved credentials from localStorage
     */
    function loadSavedCredentials() {
        try {
            const saved = localStorage.getItem('phoenix_login_credentials');
            if (!saved) return;
            
            const credentials = JSON.parse(saved);
            
            // Check if credentials are not too old (30 days)
            const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
            if (credentials.timestamp < thirtyDaysAgo) {
                clearSavedCredentials();
                return;
            }
            
            // Fill in saved username/email
            if (credentials.usernameOrEmail && usernameEmailInput) {
                usernameEmailInput.value = credentials.usernameOrEmail;
            }
            
            // Check remember me checkbox
            if (credentials.rememberMe && rememberMeCheckbox) {
                rememberMeCheckbox.checked = true;
            }
            
        } catch (error) {
            console.warn('Failed to load saved credentials:', error);
            clearSavedCredentials();
        }
    }

    /**
     * Clear saved credentials from localStorage
     */
    function clearSavedCredentials() {
        try {
            localStorage.removeItem('phoenix_login_credentials');
        } catch (error) {
            console.warn('Failed to clear saved credentials:', error);
        }
    }

    /**
     * Initialize when DOM is ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();