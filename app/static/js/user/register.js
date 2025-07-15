/**
 * Phoenix Registration Page JavaScript
 * Handles registration form functionality and validation
 */

(function() {
    'use strict';

    let registerForm;
    let usernameInput;
    let emailInput;
    let passwordInput;
    let confirmPasswordInput;
    let togglePasswordButtons;
    let strengthMeter;
    let strengthText;

    /**
     * Initialize registration page functionality
     */
    function init() {
        // Get form elements
        registerForm = document.querySelector('.register-form');
        usernameInput = document.getElementById('username');
        emailInput = document.getElementById('email');
        passwordInput = document.getElementById('password');
        confirmPasswordInput = document.getElementById('confirm_password');
        togglePasswordButtons = document.querySelectorAll('.toggle-password');
        strengthMeter = document.querySelector('.password-strength-meter');
        strengthText = document.querySelector('.password-strength-text');

        if (!registerForm) {
            return;
        }

        // Initialize components
        initFormValidation();
        initPasswordToggle();
        initPasswordStrength();
        initFormSubmission();
        initKeyboardShortcuts();
        initAutoFocus();
        initUsernameAvailability();
        initEmailAvailability();
    }

    /**
     * Initialize form validation
     */
    function initFormValidation() {
        // Real-time validation with null checks
        if (usernameInput) {
            usernameInput.addEventListener('input', validateUsername);
            usernameInput.addEventListener('blur', validateUsername);
        }
        
        if (emailInput) {
            emailInput.addEventListener('input', validateEmail);
            emailInput.addEventListener('blur', validateEmail);
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('input', validatePassword);
            passwordInput.addEventListener('blur', validatePassword);
        }
        
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', validateConfirmPassword);
            confirmPasswordInput.addEventListener('blur', validateConfirmPassword);
        }
    }

    /**
     * Validate username field
     */
    function validateUsername() {
        console.log('validateUsername called');
        console.log('usernameInput:', usernameInput);
        console.log('usernameInput exists:', !!usernameInput);
        
        const value = usernameInput ? usernameInput.value.trim() : '';
        console.log('Username value:', value, 'Length:', value.length);
        
        const usernameRegex = /^[a-zA-Z0-9_-]{3,20}$/;
        
        let isValid = true;
        let errorMessage = '';
        
        if (value.length === 0) {
            errorMessage = 'Username is required';
            isValid = false;
        } else if (value.length < 3) {
            errorMessage = 'Username must be at least 3 characters';
            isValid = false;
        } else if (value.length > 20) {
            errorMessage = 'Username must be less than 20 characters';
            isValid = false;
        } else if (!usernameRegex.test(value)) {
            errorMessage = 'Username can only contain letters, numbers, hyphens, and underscores';
            isValid = false;
        }
        
        console.log('Validation result:', { isValid, errorMessage });
        
        updateFieldValidation(usernameInput, isValid, errorMessage);
        
        // Check availability if valid format
        if (isValid && value.length >= 3) {
            checkUsernameAvailability(value);
        }
    }

    /**
     * Validate email field
     */
    function validateEmail() {
        const value = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        let isValid = true;
        let errorMessage = '';
        
        if (value.length === 0) {
            errorMessage = 'E-Mail ist erforderlich';
            isValid = false;
        } else if (!emailRegex.test(value)) {
            errorMessage = 'Bitte geben Sie eine gültige E-Mail-Adresse ein';
            isValid = false;
        }
        
        updateFieldValidation(emailInput, isValid, errorMessage);
        
        // Check availability if valid format
        if (isValid) {
            checkEmailAvailability(value);
        }
    }

    /**
     * Validate password field
     */
    function validatePassword() {
        const value = passwordInput.value;
        const strength = checkPasswordStrength(value);
        
        let isValid = true;
        let errorMessage = '';
        
        if (value.length === 0) {
            errorMessage = 'Password is required';
            isValid = false;
        } else if (value.length < 8) {
            errorMessage = 'Password must be at least 8 characters';
            isValid = false;
        } else if (strength.score < 2) {
            errorMessage = 'Password is too weak';
            isValid = false;
        }
        
        updateFieldValidation(passwordInput, isValid, errorMessage);
        updatePasswordStrength(strength);
        
        // Re-validate confirm password if it has a value
        if (confirmPasswordInput.value) {
            validateConfirmPassword();
        }
    }

    /**
     * Validate confirm password field
     */
    function validateConfirmPassword() {
        const value = confirmPasswordInput.value;
        const passwordValue = passwordInput.value;
        
        let isValid = true;
        let errorMessage = '';
        
        if (value.length === 0) {
            errorMessage = 'Please confirm your password';
            isValid = false;
        } else if (value !== passwordValue) {
            errorMessage = 'Passwords do not match';
            isValid = false;
        }
        
        updateFieldValidation(confirmPasswordInput, isValid, errorMessage);
    }

    /**
     * Update field validation state
     * @param {HTMLElement} field - Form field element
     * @param {boolean} isValid - Validation state
     * @param {string} errorMessage - Error message to display
     */
    function updateFieldValidation(field, isValid, errorMessage = '') {
        if (!field) {
            console.warn('updateFieldValidation called with null field');
            return;
        }
        
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
        if (!registerForm) return;
        
        // Handle form submission
        registerForm.addEventListener('submit', handleFormSubmit);
        
        // Prevent double submission
        registerForm.addEventListener('submit', function() {
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
        togglePasswordButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const targetInput = document.getElementById(targetId);
                if (!targetInput) return;
                
                const isPassword = targetInput.type === 'password';
                const icon = this.querySelector('i');
                
                // Toggle password visibility
                targetInput.type = isPassword ? 'text' : 'password';
                
                // Update icon
                icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
                
                // Update button title
                this.title = isPassword ? 'Hide password' : 'Show password';
                
                // Brief focus on password field
                targetInput.focus();
                
                // Add visual feedback
                this.classList.add('active');
                setTimeout(() => this.classList.remove('active'), 150);
            });
        });
    }

    /**
     * Initialize password strength meter
     */
    function initPasswordStrength() {
        if (!strengthMeter) return;
        
        // Initial state
        updatePasswordStrength({ score: 0, feedback: '' });
    }

    /**
     * Check password strength
     * @param {string} password - Password to check
     * @returns {Object} Strength score and feedback
     */
    function checkPasswordStrength(password) {
        let score = 0;
        let feedback = [];
        
        if (password.length === 0) {
            return { score: 0, feedback: 'Enter a password' };
        }
        
        // Length check
        if (password.length >= 8) score++;
        else feedback.push('at least 8 characters');
        
        if (password.length >= 10) score++; // Changed from 12 to 10
        
        // Character variety checks
        if (/[a-z]/.test(password)) score++;
        else feedback.push('lowercase letters');
        
        if (/[A-Z]/.test(password)) score++;
        else feedback.push('uppercase letters');
        
        if (/[0-9]/.test(password)) score++;
        else feedback.push('numbers');
        
        if (/[^A-Za-z0-9]/.test(password)) score++;
        else feedback.push('special characters');
        
        // Common patterns (reduce score)
        if (/(.)\1{2,}/.test(password)) score--; // Repeated characters
        if (/123|abc|qwe/i.test(password)) score--; // Sequential characters
        
        score = Math.max(0, Math.min(5, score));
        
        let strengthText = '';
        switch (score) {
            case 0:
            case 1:
                strengthText = 'Very Weak';
                break;
            case 2:
                strengthText = 'Weak';
                break;
            case 3:
                strengthText = 'Fair';
                break;
            case 4:
                strengthText = 'Good';
                break;
            case 5:
                strengthText = 'Strong';
                break;
        }
        
        const feedbackText = feedback.length > 0 ? 
            `Add ${feedback.slice(0, 2).join(' and ')}` : 
            'Great password!';
        
        return {
            score: score,
            text: strengthText,
            feedback: feedbackText
        };
    }

    /**
     * Update password strength display
     * @param {Object} strength - Strength object with score and feedback
     */
    function updatePasswordStrength(strength) {
        if (!strengthMeter) return;
        
        const strengthClasses = ['very-weak', 'weak', 'fair', 'good', 'strong'];
        
        // Remove all strength classes
        strengthMeter.classList.remove(...strengthClasses);
        
        // Add current strength class
        if (strength.score > 0) {
            strengthMeter.classList.add(strengthClasses[strength.score - 1]);
        }
        
        // Update meter width
        const percentage = (strength.score / 5) * 100;
        const meterBar = strengthMeter.querySelector('.strength-bar');
        if (meterBar) {
            meterBar.style.width = `${percentage}%`;
        }
        
        // Update text
        if (strengthText) {
            strengthText.textContent = strength.feedback || strength.text || '';
        }
    }

    /**
     * Handle form submission
     * @param {Event} event - Submit event
     */
    function handleFormSubmit(event) {
        event.preventDefault();
        
        console.log('Form submission started');
        console.log('Form elements at submission:');
        console.log('usernameInput:', usernameInput);
        console.log('Username value:', usernameInput ? usernameInput.value : 'null');
        
        // Validate all fields
        validateUsername();
        validateEmail();
        validatePassword();
        validateConfirmPassword();
        
        // Check if form is valid
        const invalidFields = document.querySelectorAll('.is-invalid');
        console.log('Invalid fields found:', invalidFields.length);
        invalidFields.forEach(field => {
            console.log('Invalid field:', field.name || field.id, 'Value:', field.value);
        });
        
        const isFormValid = registerForm.checkValidity() && 
                           !document.querySelector('.is-invalid');
        
        console.log('Form valid:', isFormValid);
        
        registerForm.classList.add('was-validated');
        
        if (!isFormValid) {
            // Focus on first invalid field
            const firstInvalidField = registerForm.querySelector('.is-invalid');
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
        Phoenix.Forms.setLoading(registerForm, true);

        // Prepare form data
        const formData = new FormData(registerForm);
        
        console.log('Creating FormData from form:', registerForm);
        console.log('Form element tagName:', registerForm.tagName);
        console.log('Form element action:', registerForm.action);
        console.log('Form element method:', registerForm.method);
        
        // Debug: Log form data contents
        console.log('FormData contents:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // Debug: Check form fields directly
        console.log('Direct field values:');
        console.log('Username input exists:', !!usernameInput);
        console.log('Username value:', usernameInput ? usernameInput.value : 'null');
        console.log('Email value:', emailInput ? emailInput.value : 'null');
        console.log('Password value length:', passwordInput ? passwordInput.value.length : 'null');
        
        // If FormData is empty, create it manually
        if (Array.from(formData.entries()).length === 0) {
            console.log('FormData is empty, creating manually...');
            formData.append('username', usernameInput ? usernameInput.value : '');
            formData.append('email', emailInput ? emailInput.value : '');
            formData.append('password', passwordInput ? passwordInput.value : '');
            formData.append('confirm_password', confirmPasswordInput ? confirmPasswordInput.value : '');
            
            console.log('Manual FormData contents:');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
        }
        
        // Submit form via AJAX
        submitRegisterForm(formData);
    }

    /**
     * Submit registration form via AJAX
     * @param {FormData} formData - Form data to submit
     */
    async function submitRegisterForm(formData) {
        try {
            console.log('submitRegisterForm called');
            console.log('FormData object:', formData);
            console.log('Form action:', registerForm.action || window.location.pathname);
            
            // Debug: Check if FormData has entries
            const hasEntries = Array.from(formData.entries()).length > 0;
            console.log('FormData has entries:', hasEntries);
            
            const response = await fetch(registerForm.action || window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {
                    const result = await response.json();
                    
                    if (result.success) {
                        Phoenix.Utils.showToast('Registration successful! Please log in.', 'success');
                        
                        // Redirect to login page after short delay
                        setTimeout(() => {
                            window.location.href = result.redirect_url || '/user/login';
                        }, 1500);
                    } else {
                        throw new Error(result.message || 'Registration failed');
                    }
                } else {
                    // Handle HTML response
                    const text = await response.text();
                    
                    if (text.includes('alert-danger') || text.includes('error')) {
                        // Extract error message from HTML
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(text, 'text/html');
                        const errorAlert = doc.querySelector('.alert-danger');
                        const errorMessage = errorAlert ? errorAlert.textContent.trim() : 'Registration failed';
                        
                        throw new Error(errorMessage);
                    } else {
                        // Successful registration
                        Phoenix.Utils.showToast('Registration successful! Please log in.', 'success');
                        
                        setTimeout(() => {
                            window.location.href = '/user/login';
                        }, 1500);
                    }
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Registration error:', error);
            Phoenix.Utils.showToast(error.message || 'Registration failed. Please try again.', 'error');
            
            // Shake the form for visual feedback
            registerForm.classList.add('animate__animated', 'animate__shakeX');
            setTimeout(() => {
                registerForm.classList.remove('animate__animated', 'animate__shakeX');
            }, 1000);
            
        } finally {
            // Remove loading state
            Phoenix.Forms.setLoading(registerForm, false);
        }
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        const inputs = [usernameInput, emailInput, passwordInput, confirmPasswordInput];
        
        inputs.forEach((input, index) => {
            input.addEventListener('keydown', function(event) {
                // Enter key moves to next field or submits
                if (event.key === 'Enter') {
                    event.preventDefault();
                    if (index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    } else {
                        registerForm.dispatchEvent(new Event('submit'));
                    }
                }
            });
        });
    }

    /**
     * Initialize auto-focus functionality
     */
    function initAutoFocus() {
        // Focus on username field when page loads
        if (usernameInput) {
            setTimeout(() => {
                usernameInput.focus();
            }, 100);
        }
    }

    /**
     * Initialize username availability checking
     */
    function initUsernameAvailability() {
        let timeoutId;
        
        usernameInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            
            const value = this.value.trim();
            if (value.length >= 3) {
                // Debounce API calls
                timeoutId = setTimeout(() => {
                    checkUsernameAvailability(value);
                }, 500);
            }
        });
    }

    /**
     * Initialize email availability checking
     */
    function initEmailAvailability() {
        let timeoutId;
        
        emailInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            
            const value = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value.length > 0 && emailRegex.test(value)) {
                // Debounce API calls
                timeoutId = setTimeout(() => {
                    checkEmailAvailability(value);
                }, 500);
            }
        });
    }

    /**
     * Check email availability via AJAX
     * @param {string} email - Email to check
     */
    async function checkEmailAvailability(email) {
        try {
            const response = await fetch('/user/check-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ email: email })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (!result.available) {
                    updateFieldValidation(emailInput, false, 'Diese E-Mail-Adresse wird bereits verwendet');
                } else if (emailInput.classList.contains('is-invalid')) {
                    // Re-validate to clear the "taken" error if email format is valid
                    validateEmail();
                }
            }
        } catch (error) {
            console.warn('Failed to check email availability:', error);
        }
    }

    /**
     * Check username availability via AJAX
     * @param {string} username - Username to check
     */
    async function checkUsernameAvailability(username) {
        try {
            const response = await fetch('/user/check-username', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ username: username })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (!result.available) {
                    updateFieldValidation(usernameInput, false, 'Username is already taken');
                } else if (usernameInput.classList.contains('is-invalid')) {
                    // Re-validate to clear the "taken" error if username format is valid
                    validateUsername();
                }
            }
        } catch (error) {
            console.warn('Failed to check username availability:', error);
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
