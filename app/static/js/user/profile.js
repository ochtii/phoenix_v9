/**
 * Phoenix User Profile Page JavaScript
 * Handles profile interaction functionality
 */

(function() {
    'use strict';

    let profileContainer;
    let editButtons;
    let activityItems;
    let projectCards;

    /**
     * Initialize profile page functionality
     */
    function init() {
        profileContainer = document.querySelector('.profile-container');
        editButtons = document.querySelectorAll('.edit-profile-btn');
        activityItems = document.querySelectorAll('.activity-item');
        projectCards = document.querySelectorAll('.project-card');

        if (!profileContainer) return;

        // Initialize components
        initProfileInteractions();
        initActivityAnimations();
        initProjectCardAnimations();
        initTooltips();
        initKeyboardShortcuts();
    }

    /**
     * Initialize profile interaction functionality
     */
    function initProfileInteractions() {
        // Profile avatar click to upload new image (if editing own profile)
        const profileAvatar = document.querySelector('.profile-avatar');
        if (profileAvatar && document.querySelector('.edit-profile-btn')) {
            profileAvatar.style.cursor = 'pointer';
            profileAvatar.title = 'Klicken um Profilbild zu ändern';
            
            profileAvatar.addEventListener('click', function() {
                // Redirect to edit profile page with focus on avatar
                const editUrl = this.closest('.profile-container').querySelector('.edit-profile-btn')?.href;
                if (editUrl) {
                    window.location.href = editUrl + '#avatar';
                }
            });
        }

        // Copy profile URL functionality
        const profileUsername = document.querySelector('.profile-username');
        if (profileUsername) {
            profileUsername.style.cursor = 'pointer';
            profileUsername.title = 'Klicken um Profil-URL zu kopieren';
            
            profileUsername.addEventListener('click', function() {
                const profileUrl = window.location.href;
                
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(profileUrl).then(() => {
                        Phoenix.Utils.showToast('Profil-URL kopiert!', 'success');
                    }).catch(() => {
                        fallbackCopyToClipboard(profileUrl);
                    });
                } else {
                    fallbackCopyToClipboard(profileUrl);
                }
            });
        }
    }

    /**
     * Fallback function to copy text to clipboard
     * @param {string} text - Text to copy
     */
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            Phoenix.Utils.showToast('Profil-URL kopiert!', 'success');
        } catch (err) {
            Phoenix.Utils.showToast('Fehler beim Kopieren der URL', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    /**
     * Initialize activity item animations
     */
    function initActivityAnimations() {
        if (!activityItems.length) return;

        // Stagger animation for activity items on page load
        activityItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Add click animation to activity items
        activityItems.forEach(item => {
            item.addEventListener('click', function() {
                // Add ripple effect
                createRippleEffect(this);
                
                // Check if activity has a link
                const link = this.querySelector('a') || this.dataset.href;
                if (link) {
                    setTimeout(() => {
                        window.location.href = typeof link === 'string' ? link : link.href;
                    }, 200);
                }
            });
        });
    }

    /**
     * Initialize project card animations
     */
    function initProjectCardAnimations() {
        if (!projectCards.length) return;

        // Stagger animation for project cards on page load
        projectCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateX(0)';
            }, index * 150 + 300); // Start after activity items
        });

        // Add hover sound effect (if audio is enabled)
        projectCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                // Subtle scale animation
                this.style.transform = 'translateY(-4px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    /**
     * Create ripple effect on element click
     * @param {HTMLElement} element - Element to create ripple on
     */
    function createRippleEffect(element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            pointer-events: none;
        `;
        
        // Add ripple animation CSS if not exists
        if (!document.querySelector('#ripple-style')) {
            const style = document.createElement('style');
            style.id = 'ripple-style';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Initialize tooltips for interactive elements
     */
    function initTooltips() {
        // Add tooltips to stats
        const profileStats = document.querySelectorAll('.profile-stat');
        profileStats.forEach(stat => {
            const label = stat.querySelector('.profile-stat-label').textContent;
            const number = stat.querySelector('.profile-stat-number').textContent;
            
            stat.title = `${number} ${label}`;
            stat.style.cursor = 'help';
        });

        // Add tooltips to role badges
        const roleElement = document.querySelector('.profile-role');
        if (roleElement) {
            const roleText = roleElement.textContent.trim();
            if (roleText.includes('Administrator')) {
                roleElement.title = 'Hat vollständige Berechtigung zur Verwaltung der Plattform';
            } else if (roleText.includes('Moderator')) {
                roleElement.title = 'Kann Inhalte moderieren und Benutzer verwalten';
            } else {
                roleElement.title = 'Standard-Benutzerrolle';
            }
        }

        // Add tooltips to activity icons
        const activityIcons = document.querySelectorAll('.activity-icon i');
        activityIcons.forEach(icon => {
            const activityTitle = icon.closest('.activity-item').querySelector('.activity-title').textContent;
            icon.closest('.activity-icon').title = activityTitle;
        });
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(event) {
            // Ctrl/Cmd + E to edit profile (if on own profile)
            if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
                const editButton = document.querySelector('.edit-profile-btn');
                if (editButton) {
                    event.preventDefault();
                    editButton.click();
                }
            }
            
            // Ctrl/Cmd + C to copy profile URL
            if ((event.ctrlKey || event.metaKey) && event.key === 'c' && !window.getSelection().toString()) {
                const profileUsername = document.querySelector('.profile-username');
                if (profileUsername && event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
                    event.preventDefault();
                    profileUsername.click();
                }
            }
            
            // Arrow keys to navigate through projects
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
                const focusedProject = document.activeElement;
                if (focusedProject && focusedProject.classList.contains('project-card')) {
                    event.preventDefault();
                    
                    const allProjects = Array.from(projectCards);
                    const currentIndex = allProjects.indexOf(focusedProject);
                    
                    let nextIndex;
                    if (event.key === 'ArrowDown') {
                        nextIndex = (currentIndex + 1) % allProjects.length;
                    } else {
                        nextIndex = (currentIndex - 1 + allProjects.length) % allProjects.length;
                    }
                    
                    allProjects[nextIndex].focus();
                }
            }
            
            // Enter to open focused project
            if (event.key === 'Enter') {
                const focusedProject = document.activeElement;
                if (focusedProject && focusedProject.classList.contains('project-card')) {
                    event.preventDefault();
                    focusedProject.click();
                }
            }
        });
    }

    /**
     * Load more activities (if implemented)
     */
    function loadMoreActivities() {
        const loadMoreBtn = document.querySelector('.load-more-activities');
        if (!loadMoreBtn) return;
        
        loadMoreBtn.addEventListener('click', async function() {
            const currentCount = activityItems.length;
            const userId = window.location.pathname.split('/').pop();
            
            try {
                Phoenix.Forms.setLoading(this, true);
                
                const response = await fetch(`/user/${userId}/activities?offset=${currentCount}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.activities && data.activities.length > 0) {
                        // Add new activities to the DOM
                        const activityContainer = document.querySelector('.profile-section:last-child');
                        data.activities.forEach(activity => {
                            const activityHtml = createActivityHTML(activity);
                            activityContainer.insertAdjacentHTML('beforeend', activityHtml);
                        });
                        
                        // Re-initialize for new items
                        activityItems = document.querySelectorAll('.activity-item');
                        initActivityAnimations();
                        
                        // Hide button if no more activities
                        if (data.activities.length < 10) {
                            this.style.display = 'none';
                        }
                    } else {
                        this.style.display = 'none';
                        Phoenix.Utils.showToast('Keine weiteren Aktivitäten vorhanden', 'info');
                    }
                }
                
            } catch (error) {
                console.error('Error loading more activities:', error);
                Phoenix.Utils.showToast('Fehler beim Laden der Aktivitäten', 'error');
            } finally {
                Phoenix.Forms.setLoading(this, false);
            }
        });
    }

    /**
     * Create HTML for activity item
     * @param {Object} activity - Activity data
     * @returns {string} HTML string
     */
    function createActivityHTML(activity) {
        const iconMap = {
            'project_created': 'fas fa-plus',
            'project_updated': 'fas fa-edit',
            'message_sent': 'fas fa-comment',
            'ticket_created': 'fas fa-ticket-alt'
        };
        
        const icon = iconMap[activity.type] || 'fas fa-circle';
        
        return `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">${activity.created_at}</div>
                </div>
            </div>
        `;
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
