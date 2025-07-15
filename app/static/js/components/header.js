/**
 * Phoenix Header Component JavaScript
 * Handles navigation and header functionality
 */

(function() {
    'use strict';

    let navbar;
    let navbarToggler;
    let searchInput;
    let userDropdown;
    let notificationsDropdown;

    /**
     * Initialize header functionality
     */
    function init() {
        navbar = document.querySelector('.navbar');
        navbarToggler = document.querySelector('.navbar-toggler');
        searchInput = document.querySelector('input[type="search"]');
        userDropdown = document.getElementById('userDropdown');
        notificationsDropdown = document.getElementById('notificationsDropdown');

        if (!navbar) return;

        // Initialize components
        initScrollBehavior();
        initMobileNavigation();
        initSearchFunctionality();
        initDropdowns();
        initKeyboardShortcuts();
    }

    /**
     * Initialize scroll behavior for navbar
     */
    function initScrollBehavior() {
        let lastScrollTop = 0;
        const scrollThreshold = 100;

        const handleScroll = Phoenix.Utils.throttle(() => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Add/remove scrolled class
            if (scrollTop > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }

            // Hide/show navbar on scroll (optional behavior)
            if (Math.abs(lastScrollTop - scrollTop) > scrollThreshold) {
                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    // Scrolling down
                    navbar.classList.add('navbar-hidden');
                } else {
                    // Scrolling up
                    navbar.classList.remove('navbar-hidden');
                }
                lastScrollTop = scrollTop;
            }
        }, 100);

        window.addEventListener('scroll', handleScroll);
    }

    /**
     * Initialize mobile navigation
     */
    function initMobileNavigation() {
        if (!navbarToggler) return;

        // Close mobile menu when clicking on a link
        const navLinks = navbar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                const navbarCollapse = navbar.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (event) => {
            const navbarCollapse = navbar.querySelector('.navbar-collapse');
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                if (!navbar.contains(event.target)) {
                    navbarToggler.click();
                }
            }
        });
    }

    /**
     * Initialize search functionality
     */
    function initSearchFunctionality() {
        if (!searchInput) return;

        // Search suggestions (if implemented)
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    // Implement search suggestions here
                    fetchSearchSuggestions(query);
                }, 300);
            }
        });

        // Search form submission
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = `/discover/search?q=${encodeURIComponent(query)}`;
                }
            });
        }
    }

    /**
     * Fetch search suggestions
     * @param {string} query - Search query
     */
    async function fetchSearchSuggestions(query) {
        try {
            const response = await Phoenix.Utils.ajax('/api/search/suggestions', {
                method: 'GET',
                data: { q: query }
            });

            if (response.suggestions) {
                displaySearchSuggestions(response.suggestions);
            }
        } catch (error) {
            console.log('Search suggestions not available:', error);
        }
    }

    /**
     * Display search suggestions
     * @param {Array} suggestions - Array of suggestion objects
     */
    function displaySearchSuggestions(suggestions) {
        // Remove existing suggestions
        const existingSuggestions = document.querySelector('.search-suggestions');
        if (existingSuggestions) {
            existingSuggestions.remove();
        }

        if (!suggestions.length) return;

        // Create suggestions dropdown
        const suggestionsDropdown = document.createElement('div');
        suggestionsDropdown.className = 'search-suggestions';
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('a');
            item.className = 'search-suggestion-item';
            item.href = suggestion.url;
            item.innerHTML = `
                <i class="${suggestion.icon || 'fas fa-search'}"></i>
                <span>${suggestion.title}</span>
                <small>${suggestion.type}</small>
            `;
            suggestionsDropdown.appendChild(item);
        });

        // Position and show suggestions
        const searchContainer = searchInput.parentElement;
        searchContainer.style.position = 'relative';
        searchContainer.appendChild(suggestionsDropdown);

        // Hide suggestions when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function hideSuggestions(event) {
                if (!searchContainer.contains(event.target)) {
                    suggestionsDropdown.remove();
                    document.removeEventListener('click', hideSuggestions);
                }
            });
        }, 100);
    }

    /**
     * Initialize dropdown functionality
     */
    function initDropdowns() {
        // Mark notifications as read when dropdown is opened
        if (notificationsDropdown) {
            notificationsDropdown.addEventListener('shown.bs.dropdown', () => {
                markNotificationsAsRead();
            });
        }

        // Load more notifications when scrolling in dropdown
        const notificationsMenu = document.querySelector('#notificationsDropdown + .dropdown-menu');
        if (notificationsMenu) {
            notificationsMenu.addEventListener('scroll', (event) => {
                const menu = event.target;
                if (menu.scrollTop + menu.clientHeight >= menu.scrollHeight - 10) {
                    loadMoreNotifications();
                }
            });
        }
    }

    /**
     * Mark notifications as read
     */
    async function markNotificationsAsRead() {
        try {
            await Phoenix.Utils.ajax('/api/notifications/mark-read', {
                method: 'POST'
            });
            
            // Update notification badge
            const badge = document.querySelector('#notificationsDropdown .badge');
            if (badge) {
                badge.style.display = 'none';
            }
        } catch (error) {
            console.log('Failed to mark notifications as read:', error);
        }
    }

    /**
     * Load more notifications
     */
    async function loadMoreNotifications() {
        try {
            const currentCount = document.querySelectorAll('.notification-item').length;
            const response = await Phoenix.Utils.ajax(`/api/notifications?offset=${currentCount}`, {
                method: 'GET'
            });

            if (response.notifications && response.notifications.length > 0) {
                const notificationsContainer = document.querySelector('.dropdown-menu .notifications-container');
                if (notificationsContainer) {
                    response.notifications.forEach(notification => {
                        const notificationHtml = createNotificationHTML(notification);
                        notificationsContainer.insertAdjacentHTML('beforeend', notificationHtml);
                    });
                }
            }
        } catch (error) {
            console.log('Failed to load more notifications:', error);
        }
    }

    /**
     * Create HTML for notification item
     * @param {Object} notification - Notification data
     * @returns {string} HTML string
     */
    function createNotificationHTML(notification) {
        return `
            <li>
                <a class="dropdown-item" href="${notification.link}">
                    <div class="notification-item">
                        <div class="notification-title">${notification.title}</div>
                        <div class="notification-time">${notification.time}</div>
                    </div>
                </a>
            </li>
        `;
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Focus search with Ctrl+K
            if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                event.preventDefault();
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Open user menu with Alt+U
            if (event.altKey && event.key === 'u') {
                event.preventDefault();
                if (userDropdown) {
                    userDropdown.click();
                }
            }

            // Open notifications with Alt+N
            if (event.altKey && event.key === 'n') {
                event.preventDefault();
                if (notificationsDropdown) {
                    notificationsDropdown.click();
                }
            }
        });
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