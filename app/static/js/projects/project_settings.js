/**
 * Project Settings JavaScript
 * Handles project settings management, invite codes, and archive functionality
 */

// Global variables that will be set by the template
let PROJECT_UID = '';
let PROJECT_ID = '';
let PROJECTS_INDEX_URL = '';

/**
 * Initialize the project settings page
 */
function initProjectSettings(projectUid, projectId, projectsIndexUrl) {
    PROJECT_UID = projectUid;
    PROJECT_ID = projectId;
    PROJECTS_INDEX_URL = projectsIndexUrl;
}

/**
 * Copy invite code to clipboard
 */
function copyCode(code) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(code).then(() => {
            showAlert('Code in die Zwischenablage kopiert!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyTextToClipboard(code);
        });
    } else {
        fallbackCopyTextToClipboard(code);
    }
}

/**
 * Copy invite code to clipboard (alternative method)
 */
function copyInviteCode(code) {
    copyCode(code);
}

/**
 * Fallback copy method for older browsers
 */
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.opacity = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('Code in die Zwischenablage kopiert!', 'success');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
        showAlert('Fehler beim Kopieren des Codes', 'danger');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Delete an invite code
 */
async function deleteInviteCode(code) {
    if (!confirm('Möchten Sie diesen Einladungscode wirklich löschen?')) {
        return;
    }
    
    try {
        const response = await fetch(`/projects/${PROJECT_UID}/invite-codes/${code}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const codeElement = document.getElementById(`code-${code}`);
            if (codeElement) {
                codeElement.remove();
            }
            showAlert('Einladungscode wurde gelöscht', 'success');
            
            // Check if no codes left and show message
            const container = document.getElementById('invite-codes-container');
            if (container && container.children.length === 0) {
                const noCodesMessage = document.getElementById('no-codes-message');
                if (noCodesMessage) {
                    noCodesMessage.style.display = 'block';
                }
            }
        } else {
            const error = await response.json();
            showAlert(error.error || 'Fehler beim Löschen des Codes', 'danger');
        }
    } catch (error) {
        console.error('Error deleting invite code:', error);
        showAlert('Netzwerkfehler beim Löschen des Codes', 'danger');
    }
}

/**
 * Add new invite code to the list display
 */
function addInviteCodeToList(code, createdAt) {
    const container = document.getElementById('invite-codes-container');
    
    const codeElement = document.createElement('div');
    codeElement.className = 'invite-code-item';
    codeElement.id = `code-${code}`;
    codeElement.innerHTML = `
        <div class="row align-items-center">
            <div class="col-md-3">
                <div class="code-display">
                    <code class="invite-code">${code}</code>
                    <button class="btn btn-sm btn-outline-light copy-btn" onclick="copyCode('${code}')">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
            <div class="col-md-6">
                <small class="text-muted">
                    Erstellt: ${new Date(createdAt).toLocaleString('de-DE')}
                    <br><span class="text-success">Noch nicht verwendet</span>
                </small>
            </div>
            <div class="col-md-3 text-end">
                <button class="btn btn-sm btn-outline-danger" onclick="deleteInviteCode('${code}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    container.insertBefore(codeElement, container.firstChild);
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

/**
 * Save project settings
 */
async function saveProjectSettings() {
    try {
        const projectImage = document.querySelector('input[name="project_image"]:checked')?.value || '';
        const isPrivate = document.querySelector('input[name="privacy"]:checked')?.value === 'private';
        const description = document.getElementById('description').value;
        const name = document.getElementById('project_name').value;
        
        const settings = {
            name: name,
            description: description,
            is_private: isPrivate,
            project_image: projectImage
        };
        
        const response = await fetch(`/projects/${PROJECT_UID}/update-settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            const result = await response.json();
            showAlert(result.message || 'Einstellungen erfolgreich gespeichert', 'success');
        } else {
            const error = await response.json();
            showAlert(error.error || 'Fehler beim Speichern der Einstellungen', 'danger');
        }
    } catch (error) {
        console.error('Error saving project settings:', error);
        showAlert('Netzwerkfehler beim Speichern der Einstellungen', 'danger');
    }
}

/**
 * Create new invite code
 */
async function createInviteCode() {
    try {
        const response = await fetch(`/projects/${PROJECT_UID}/invite-codes/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Show success message
            showAlert(`Neuer Einladungscode erstellt: ${result.code}`, 'success');
            
            // Add new code to the list
            addInviteCodeToList(result.code, result.created_at);
            
            // Hide no-codes message if it exists
            const noCodesMessage = document.getElementById('no-codes-message');
            if (noCodesMessage) {
                noCodesMessage.style.display = 'none';
            }
        } else {
            const error = await response.json();
            showAlert(error.error || 'Fehler beim Erstellen des Einladungscodes', 'danger');
        }
    } catch (error) {
        console.error('Error creating invite code:', error);
        showAlert('Netzwerkfehler beim Erstellen des Einladungscodes', 'danger');
    }
}

/**
 * Add new invite code to simple list (alternative layout)
 */
function addInviteCodeToSimpleList(code, createdAt) {
    const codesList = document.getElementById('invite-codes-list');
    if (!codesList) return;
    
    const codeItem = document.createElement('div');
    codeItem.className = 'invite-code-item d-flex justify-content-between align-items-center p-3 mb-2 bg-secondary rounded';
    codeItem.innerHTML = `
        <div>
            <strong class="text-primary">${code}</strong>
            <small class="text-muted d-block">Erstellt: ${new Date(createdAt).toLocaleDateString('de-DE')}</small>
        </div>
        <div>
            <button type="button" class="btn btn-sm btn-outline-primary me-2" onclick="copyInviteCode('${code}')">
                <i class="fas fa-copy"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteInviteCode('${code}')">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    codesList.appendChild(codeItem);
}

/**
 * Archive project - legacy function for modal trigger
 */
function archiveProject() {
    const archiveModalBtn = document.getElementById('archiveModal');
    if (archiveModalBtn) {
        archiveModalBtn.click();
    }
}

/**
 * Confirm project archiving
 */
async function confirmArchiveProject() {
    try {
        const response = await fetch(`/projects/${PROJECT_ID}/archive`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('archiveModal'));
            if (modal) {
                modal.hide();
            }
            
            // Show success message
            showAlert('Projekt wurde erfolgreich archiviert', 'success');
            
            // Redirect to projects overview after 2 seconds
            setTimeout(() => {
                window.location.href = PROJECTS_INDEX_URL;
            }, 2000);
        } else {
            const error = await response.json();
            showAlert(error.message || 'Fehler beim Archivieren des Projekts', 'danger');
        }
    } catch (error) {
        console.error('Error archiving project:', error);
        showAlert('Netzwerkfehler beim Archivieren des Projekts', 'danger');
    }
}
