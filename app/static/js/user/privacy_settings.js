/**
 * Privacy Settings JavaScript
 * Handles privacy and notification settings
 */

document.addEventListener('DOMContentLoaded', function() {
    initPrivacySettings();
});

/**
 * Initialize privacy settings page
 */
function initPrivacySettings() {
    // Setup form handlers
    setupPrivacyFormHandlers();
    
    // Setup browser notification permission
    setupNotificationPermission();
}

/**
 * Setup form handlers
 */
function setupPrivacyFormHandlers() {
    const privacyForm = document.getElementById('privacy-form');
    if (privacyForm) {
        privacyForm.addEventListener('submit', handlePrivacyUpdate);
    }
}

/**
 * Setup notification permission
 */
function setupNotificationPermission() {
    const browserNotifications = document.getElementById('browser_notifications');
    if (browserNotifications) {
        browserNotifications.addEventListener('change', function() {
            if (this.checked && 'Notification' in window) {
                if (Notification.permission === 'default') {
                    Notification.requestPermission().then(permission => {
                        if (permission !== 'granted') {
                            this.checked = false;
                            showAlert('Browser-Benachrichtigungen wurden nicht erlaubt', 'warning');
                        }
                    });
                } else if (Notification.permission === 'denied') {
                    this.checked = false;
                    showAlert('Browser-Benachrichtigungen sind blockiert. Bitte in den Browser-Einstellungen aktivieren.', 'warning');
                }
            }
        });
    }
}

/**
 * Handle privacy settings update
 */
async function handlePrivacyUpdate(event) {
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
            showAlert('Datenschutz-Einstellungen erfolgreich gespeichert', 'success');
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Speichern der Einstellungen', 'danger');
        }
    } catch (error) {
        console.error('Error updating privacy settings:', error);
        showAlert('Netzwerkfehler beim Speichern der Einstellungen', 'danger');
    }
}

/**
 * Download user data
 */
async function downloadData() {
    try {
        showAlert('Daten werden vorbereitet...', 'info');
        
        const response = await fetch('/user/download-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'meine-daten.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('Daten erfolgreich heruntergeladen', 'success');
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Herunterladen der Daten', 'danger');
        }
    } catch (error) {
        console.error('Error downloading data:', error);
        showAlert('Netzwerkfehler beim Herunterladen der Daten', 'danger');
    }
}

/**
 * Clear activity data
 */
async function clearActivityData() {
    try {
        const response = await fetch('/user/clear-activity-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('clearDataModal'));
            if (modal) {
                modal.hide();
            }
            
            showAlert('Aktivitätsdaten erfolgreich gelöscht', 'success');
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Löschen der Daten', 'danger');
        }
    } catch (error) {
        console.error('Error clearing activity data:', error);
        showAlert('Netzwerkfehler beim Löschen der Daten', 'danger');
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
