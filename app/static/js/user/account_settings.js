/**
 * Account Settings JavaScript
 * Handles account management functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initAccountSettings();
});

/**
 * Initialize account settings page
 */
function initAccountSettings() {
    // Password confirmation validation
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (newPassword && confirmPassword) {
        confirmPassword.addEventListener('input', validatePasswordMatch);
        newPassword.addEventListener('input', validatePasswordMatch);
    }
    
    // Delete account confirmation
    const deleteConfirmation = document.getElementById('delete_confirmation');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    
    if (deleteConfirmation && confirmDeleteBtn) {
        deleteConfirmation.addEventListener('input', function() {
            const expectedUsername = this.getAttribute('data-username') || 
                                   document.querySelector('[data-username]')?.getAttribute('data-username');
            confirmDeleteBtn.disabled = this.value !== expectedUsername;
        });
    }
    
    // Form submissions
    setupFormHandlers();
}

/**
 * Validate password match
 */
function validatePasswordMatch() {
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (newPassword.value && confirmPassword.value) {
        if (newPassword.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity('Passwörter stimmen nicht überein');
        } else {
            confirmPassword.setCustomValidity('');
        }
    }
}

/**
 * Setup form handlers
 */
function setupFormHandlers() {
    // Account form
    const accountForm = document.getElementById('account-form');
    if (accountForm) {
        accountForm.addEventListener('submit', handleAccountUpdate);
    }
    
    // Password form
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
    }
}

/**
 * Handle account update
 */
async function handleAccountUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    try {
        const response = await fetch(event.target.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            showAlert('Kontodaten erfolgreich aktualisiert', 'success');
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Aktualisieren der Kontodaten', 'danger');
        }
    } catch (error) {
        console.error('Error updating account:', error);
        showAlert('Netzwerkfehler beim Aktualisieren der Kontodaten', 'danger');
    }
}

/**
 * Handle password change
 */
async function handlePasswordChange(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    // Validate passwords match
    if (formData.get('new_password') !== formData.get('confirm_password')) {
        showAlert('Passwörter stimmen nicht überein', 'danger');
        return;
    }
    
    try {
        const response = await fetch(event.target.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            showAlert('Passwort erfolgreich geändert', 'success');
            event.target.reset();
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Ändern des Passworts', 'danger');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showAlert('Netzwerkfehler beim Ändern des Passworts', 'danger');
    }
}

/**
 * Delete account
 */
async function deleteAccount() {
    const confirmation = document.getElementById('delete_confirmation').value;
    const expectedUsername = document.querySelector('[data-username]')?.getAttribute('data-username');
    
    if (confirmation !== expectedUsername) {
        showAlert('Benutzername stimmt nicht überein', 'danger');
        return;
    }
    
    try {
        const response = await fetch('/user/delete-account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ confirmation: confirmation })
        });
        
        if (response.ok) {
            showAlert('Konto wird gelöscht...', 'info');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Löschen des Kontos', 'danger');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        showAlert('Netzwerkfehler beim Löschen des Kontos', 'danger');
    }
}

/**
 * Show alert message
 */
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}
