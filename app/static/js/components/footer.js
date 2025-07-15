/**
 * Phoenix Footer Component JavaScript
 * Handles footer functionality and interactions
 */

(function() {
    'use strict';

    let footer;
    let subscribeForm;
    let socialLinks;

    /**
     * Initialize footer functionality
     */
    function init() {
        footer = document.querySelector('footer');
        subscribeForm = document.querySelector('.newsletter-form');
        socialLinks = document.querySelectorAll('.social-links a');

        if (!footer) return;

        // Initialize components
        initNewsletterSubscription();
        initSocialLinks();
        initFooterLinks();
        initScrollToTop();
        updateCopyright(); // Add copyright update here
    }

    /**
     * Initialize newsletter subscription
     */
    function initNewsletterSubscription() {
        if (!subscribeForm) return;

        subscribeForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const emailInput = subscribeForm.querySelector('input[type="email"]');
            const submitButton = subscribeForm.querySelector('button[type="submit"]');
            const email = emailInput.value.trim();

            if (!email) {
                Phoenix.Utils.showToast('Bitte geben Sie eine E-Mail-Adresse ein', 'warning');
                return;
            }

            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                Phoenix.Utils.showToast('Bitte geben Sie eine gültige E-Mail-Adresse ein', 'error');
                return;
            }

            // Set loading state
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Abonnieren...';

            try {
                const response = await Phoenix.Utils.ajax('/api/newsletter/subscribe', {
                    method: 'POST',
                    data: { email: email }
                });

                if (response.success) {
                    Phoenix.Utils.showToast('Erfolgreich abonniert! Vielen Dank.', 'success');
                    emailInput.value = '';
                } else {
                    throw new Error(response.message || 'Subscription failed');
                }

            } catch (error) {
                console.error('Newsletter subscription error:', error);
                Phoenix.Utils.showToast('Fehler beim Abonnieren. Bitte versuchen Sie es später erneut.', 'error');
            } finally {
                // Reset button state
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }

    /**
     * Initialize social links
     */
    function initSocialLinks() {
        socialLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                // Add click animation
                link.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    link.style.transform = '';
                }, 150);

                // Track social link clicks (analytics)
                trackSocialClick(link.href, link.title);
            });

            // Add hover effects
            link.addEventListener('mouseenter', () => {
                link.style.transform = 'translateY(-2px)';
            });

            link.addEventListener('mouseleave', () => {
                link.style.transform = '';
            });
        });
    }

    /**
     * Track social link clicks
     * @param {string} url - Social link URL
     * @param {string} platform - Social platform name
     */
    function trackSocialClick(url, platform) {
        // Analytics tracking (if implemented)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'social_click', {
                'social_platform': platform,
                'social_url': url
            });
        }

        console.log(`Social link clicked: ${platform} - ${url}`);
    }

    /**
     * Initialize footer links
     */
    function initFooterLinks() {
        const footerLinks = footer.querySelectorAll('a[href^="#"]');
        
        footerLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                const href = link.getAttribute('href');
                
                // Handle special footer links
                if (href === '#top') {
                    event.preventDefault();
                    scrollToTop();
                } else if (href === '#contact') {
                    event.preventDefault();
                    openContactModal();
                } else if (href === '#privacy') {
                    event.preventDefault();
                    openPrivacyModal();
                }
            });
        });

        // External links - open in new tab
        const externalLinks = footer.querySelectorAll('a[href^="http"]:not([href*="' + window.location.hostname + '"])');
        externalLinks.forEach(link => {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
            
            // Add external link icon
            if (!link.querySelector('.fa-external-link-alt')) {
                link.innerHTML += ' <i class="fas fa-external-link-alt fa-sm"></i>';
            }
        });
    }

    /**
     * Initialize scroll to top functionality
     */
    function initScrollToTop() {
        const scrollTopLinks = footer.querySelectorAll('a[href="#top"], .scroll-to-top');
        
        scrollTopLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                event.preventDefault();
                scrollToTop();
            });
        });
    }

    /**
     * Scroll to top of page
     */
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    /**
     * Open contact modal
     */
    function openContactModal() {
        // Check if contact modal exists
        let contactModal = document.getElementById('contactModal');
        
        if (!contactModal) {
            // Create contact modal if it doesn't exist
            contactModal = createContactModal();
            document.body.appendChild(contactModal);
        }

        const modal = new bootstrap.Modal(contactModal);
        modal.show();
    }

    /**
     * Create contact modal
     * @returns {HTMLElement} Contact modal element
     */
    function createContactModal() {
        const modal = document.createElement('div');
        modal.id = 'contactModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-envelope me-2"></i>
                            Kontakt
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-envelope me-2"></i>E-Mail</h6>
                                <p><a href="mailto:contact@phoenix.app">contact@phoenix.app</a></p>
                                
                                <h6><i class="fas fa-life-ring me-2"></i>Support</h6>
                                <p><a href="mailto:support@phoenix.app">support@phoenix.app</a></p>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-bug me-2"></i>Bug Report</h6>
                                <p><a href="/support/new-ticket" class="btn btn-outline-primary btn-sm">Ticket erstellen</a></p>
                                
                                <h6><i class="fas fa-comments me-2"></i>Community</h6>
                                <div class="d-flex gap-2">
                                    <a href="#" class="btn btn-outline-secondary btn-sm"><i class="fab fa-discord"></i></a>
                                    <a href="#" class="btn btn-outline-secondary btn-sm"><i class="fab fa-twitter"></i></a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Open privacy modal
     */
    function openPrivacyModal() {
        // Redirect to privacy page or open modal
        window.location.href = '/privacy';
    }

    /**
     * Add dynamic year to copyright
     */
    function updateCopyright() {
        // footer is guaranteed to exist when this is called from init()
        if (!footer) return;
        
        const copyrightElements = footer.querySelectorAll('.copyright-year');
        const currentYear = new Date().getFullYear();
        
        copyrightElements.forEach(element => {
            element.textContent = currentYear;
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