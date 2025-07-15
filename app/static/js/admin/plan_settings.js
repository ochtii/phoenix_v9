/**
 * Plan Settings JavaScript
 */

class PlanSettings {
    constructor() {
        this.features = [];
        this.editFeatures = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadExistingFeatures();
    }

    bindEvents() {
        // Add feature buttons
        document.getElementById('addFeatureBtn')?.addEventListener('click', () => {
            this.addFeature();
        });

        document.getElementById('editAddFeatureBtn')?.addEventListener('click', () => {
            this.addEditFeature();
        });

        // Feature input enter key
        document.getElementById('newFeature')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addFeature();
            }
        });

        document.getElementById('editNewFeature')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addEditFeature();
            }
        });

        // Create plan button
        document.getElementById('createPlanBtn')?.addEventListener('click', () => {
            this.createPlan();
        });

        // Update plan button
        document.getElementById('updatePlanBtn')?.addEventListener('click', () => {
            this.updatePlan();
        });

        // Edit plan buttons
        document.querySelectorAll('.edit-plan-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const planId = e.target.closest('.edit-plan-btn').dataset.planId;
                this.loadPlanForEdit(planId);
            });
        });

        // Delete plan buttons
        document.querySelectorAll('.delete-plan-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const planId = e.target.closest('.delete-plan-btn').dataset.planId;
                const planName = e.target.closest('.delete-plan-btn').dataset.planName;
                this.deletePlan(planId, planName);
            });
        });

        // Modal reset events
        document.getElementById('addPlanModal')?.addEventListener('hidden.bs.modal', () => {
            this.resetAddForm();
        });

        document.getElementById('editPlanModal')?.addEventListener('hidden.bs.modal', () => {
            this.resetEditForm();
        });
    }

    loadExistingFeatures() {
        // This would be called when editing an existing plan
        // Features will be loaded from the plan data
    }

    addFeature() {
        const input = document.getElementById('newFeature');
        const feature = input.value.trim();
        
        if (feature && !this.features.includes(feature)) {
            this.features.push(feature);
            this.renderFeatures();
            input.value = '';
        }
    }

    addEditFeature() {
        const input = document.getElementById('editNewFeature');
        const feature = input.value.trim();
        
        if (feature && !this.editFeatures.includes(feature)) {
            this.editFeatures.push(feature);
            this.renderEditFeatures();
            input.value = '';
        }
    }

    removeFeature(index) {
        this.features.splice(index, 1);
        this.renderFeatures();
    }

    removeEditFeature(index) {
        this.editFeatures.splice(index, 1);
        this.renderEditFeatures();
    }

    renderFeatures() {
        const container = document.getElementById('featuresList');
        container.innerHTML = '';

        this.features.forEach((feature, index) => {
            const featureElement = document.createElement('div');
            featureElement.className = 'feature-input-group';
            featureElement.innerHTML = `
                <span class="form-control">${feature}</span>
                <button type="button" class="btn btn-outline-danger" onclick="planSettings.removeFeature(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(featureElement);
        });
    }

    renderEditFeatures() {
        const container = document.getElementById('editFeaturesList');
        container.innerHTML = '';

        this.editFeatures.forEach((feature, index) => {
            const featureElement = document.createElement('div');
            featureElement.className = 'feature-input-group';
            featureElement.innerHTML = `
                <span class="form-control">${feature}</span>
                <button type="button" class="btn btn-outline-danger" onclick="planSettings.removeEditFeature(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(featureElement);
        });
    }

    async createPlan() {
        const form = document.getElementById('addPlanForm');
        const formData = new FormData(form);
        
        // Validate required fields
        if (!formData.get('name') || !formData.get('price') || !formData.get('max_projects') || !formData.get('max_storage_gb')) {
            this.showAlert('Please fill in all required fields', 'danger');
            return;
        }

        const planData = {
            name: formData.get('name'),
            description: formData.get('description'),
            price: parseFloat(formData.get('price')),
            max_projects: parseInt(formData.get('max_projects')),
            max_storage_gb: parseInt(formData.get('max_storage_gb')),
            order: parseInt(formData.get('order')) || 0,
            is_active: document.getElementById('isActive').checked,
            is_featured: document.getElementById('isFeatured').checked,
            features: this.features
        };

        try {
            const response = await fetch('/admin/api/plans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(planData)
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('Plan created successfully', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                this.showAlert(result.message || 'Error creating plan', 'danger');
            }
        } catch (error) {
            console.error('Error creating plan:', error);
            this.showAlert('Network error occurred', 'danger');
        }
    }

    async loadPlanForEdit(planId) {
        try {
            // Get plan data from the DOM
            const planCard = document.querySelector(`[data-plan-id="${planId}"]`);
            
            if (!planCard) {
                this.showAlert('Plan not found', 'danger');
                return;
            }

            // Reset edit features
            this.editFeatures = [];

            // For now, we'll extract data from the DOM
            // In a real application, you might want to fetch fresh data from the API
            const planName = planCard.querySelector('.plan-name').textContent;
            const planPrice = planCard.querySelector('.plan-price').textContent.replace('$', '');
            const planDescription = planCard.querySelector('.text-muted.small')?.textContent || '';
            
            const limitItems = planCard.querySelectorAll('.limit-item');
            const maxProjects = limitItems[0]?.querySelector('.limit-value').textContent || '1';
            const maxStorage = limitItems[1]?.querySelector('.limit-value').textContent || '1';

            // Get features
            const featureBadges = planCard.querySelectorAll('.feature-badge');
            featureBadges.forEach(badge => {
                this.editFeatures.push(badge.textContent);
            });

            // Get status
            const isActive = planCard.querySelector('.status-active') !== null;
            const isFeatured = planCard.querySelector('.status-featured') !== null;

            // Populate edit form
            document.getElementById('editPlanId').value = planId;
            document.getElementById('editPlanName').value = planName;
            document.getElementById('editPlanPrice').value = planPrice;
            document.getElementById('editPlanDescription').value = planDescription;
            document.getElementById('editMaxProjects').value = maxProjects;
            document.getElementById('editMaxStorage').value = maxStorage;
            document.getElementById('editPlanOrder').value = '0'; // Default, as we don't store this in DOM
            document.getElementById('editIsActive').checked = isActive;
            document.getElementById('editIsFeatured').checked = isFeatured;

            this.renderEditFeatures();

        } catch (error) {
            console.error('Error loading plan for edit:', error);
            this.showAlert('Error loading plan data', 'danger');
        }
    }

    async updatePlan() {
        const form = document.getElementById('editPlanForm');
        const formData = new FormData(form);
        const planId = formData.get('plan_id');
        
        if (!planId) {
            this.showAlert('Plan ID missing', 'danger');
            return;
        }

        // Validate required fields
        if (!formData.get('name') || !formData.get('price') || !formData.get('max_projects') || !formData.get('max_storage_gb')) {
            this.showAlert('Please fill in all required fields', 'danger');
            return;
        }

        const planData = {
            name: formData.get('name'),
            description: formData.get('description'),
            price: parseFloat(formData.get('price')),
            max_projects: parseInt(formData.get('max_projects')),
            max_storage_gb: parseInt(formData.get('max_storage_gb')),
            order: parseInt(formData.get('order')) || 0,
            is_active: document.getElementById('editIsActive').checked,
            is_featured: document.getElementById('editIsFeatured').checked,
            features: this.editFeatures
        };

        try {
            const response = await fetch(`/admin/api/plans/${planId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(planData)
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('Plan updated successfully', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                this.showAlert(result.message || 'Error updating plan', 'danger');
            }
        } catch (error) {
            console.error('Error updating plan:', error);
            this.showAlert('Network error occurred', 'danger');
        }
    }

    async deletePlan(planId, planName) {
        if (!confirm(`Are you sure you want to delete the plan "${planName}"? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(`/admin/api/plans/${planId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('Plan deleted successfully', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                this.showAlert(result.message || 'Error deleting plan', 'danger');
            }
        } catch (error) {
            console.error('Error deleting plan:', error);
            this.showAlert('Network error occurred', 'danger');
        }
    }

    resetAddForm() {
        document.getElementById('addPlanForm').reset();
        this.features = [];
        this.renderFeatures();
    }

    resetEditForm() {
        document.getElementById('editPlanForm').reset();
        this.editFeatures = [];
        this.renderEditFeatures();
    }

    getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.planSettings = new PlanSettings();
});
