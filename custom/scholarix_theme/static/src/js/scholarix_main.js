odoo.define('scholarix_theme.main', function (require) {
'use strict';

/**
 * Scholarix AI Theme - Main JavaScript Controller
 * Coordinates all theme functionality and interactive elements
 */

class ScholarixTheme {
    constructor() {
        this.isInitialized = false;
        this.scrollPosition = 0;
        this.isScrolling = false;
        
        this.init();
    }
    
    /**
     * Initialize the theme
     */
    init() {
        if (this.isInitialized) return;
        
        this.setupNavigation();
        this.setupScrollEffects();
        this.setupForms();
        this.setupModals();
        this.setupCarousels();
        this.setupLazyLoading();
        this.setupPerformanceOptimizations();
        this.setupAccessibility();
        
        this.isInitialized = true;
        console.log('Scholarix AI Theme initialized');
    }
    
    /**
     * Setup navigation enhancements
     */
    setupNavigation() {
        const navbar = document.querySelector('.navbar');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const mobileToggle = document.querySelector('.navbar-toggler');
        
        if (!navbar) return;
        
        // Navbar scroll behavior
        let lastScrollTop = 0;
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > 100) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
            
            // Hide/show navbar on scroll
            if (scrollTop > lastScrollTop && scrollTop > 200) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = scrollTop;
        });
        
        // Smooth scrolling for navigation links
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    this.smoothScrollTo(href);
                    
                    // Close mobile menu if open
                    const navbarCollapse = document.querySelector('.navbar-collapse');
                    if (navbarCollapse.classList.contains('show')) {
                        mobileToggle?.click();
                    }
                }
            });
        });
        
        // Active section highlighting
        this.setupActiveNavigation();
    }
    
    /**
     * Setup active navigation highlighting based on scroll position
     */
    setupActiveNavigation() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link[href^="#"]');
        
        if (sections.length === 0 || navLinks.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const id = entry.target.getAttribute('id');
                const navLink = document.querySelector(`.navbar-nav .nav-link[href="#${id}"]`);
                
                if (entry.isIntersecting) {
                    navLinks.forEach(link => link.classList.remove('active'));
                    navLink?.classList.add('active');
                }
            });
        }, {
            rootMargin: '-50% 0px -50% 0px'
        });
        
        sections.forEach(section => observer.observe(section));
    }
    
    /**
     * Setup scroll-based effects
     */
    setupScrollEffects() {
        // Scroll to top button
        this.createScrollToTopButton();
        
        // Parallax effects for elements with data-parallax attribute
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        if (parallaxElements.length > 0) {
            this.setupParallaxElements(parallaxElements);
        }
        
        // Progress bar for reading
        this.setupProgressBar();
    }
    
    /**
     * Create scroll to top button
     */
    createScrollToTopButton() {
        const scrollButton = document.createElement('button');
        scrollButton.className = 'scholarix-scroll-top';
        scrollButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
        scrollButton.setAttribute('aria-label', 'Scroll to top');
        
        document.body.appendChild(scrollButton);
        
        // Show/hide button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollButton.classList.add('show');
            } else {
                scrollButton.classList.remove('show');
            }
        });
        
        // Scroll to top functionality
        scrollButton.addEventListener('click', () => {
            this.smoothScrollTo('#top', 800);
        });
    }
    
    /**
     * Setup parallax elements
     */
    setupParallaxElements(elements) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            elements.forEach(element => {
                const rate = scrolled * (element.dataset.parallax || -0.5);
                element.style.transform = `translateY(${rate}px)`;
            });
        });
    }
    
    /**
     * Setup reading progress bar
     */
    setupProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scholarix-progress-bar';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, #00E5FF, #7C4DFF);
            z-index: 9999;
            transition: width 0.1s ease-out;
        `;
        
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', () => {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrolled = (window.pageYOffset / scrollHeight) * 100;
            progressBar.style.width = Math.min(scrolled, 100) + '%';
        });
    }
    
    /**
     * Setup form enhancements
     */
    setupForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add floating label effect
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                this.setupFloatingLabel(input);
            });
            
            // Add form validation feedback
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }
    
    /**
     * Setup floating label effect for form inputs
     */
    setupFloatingLabel(input) {
        const wrapper = document.createElement('div');
        wrapper.className = 'scholarix-input-wrapper';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        input.addEventListener('focus', () => {
            wrapper.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                wrapper.classList.remove('focused');
            }
        });
        
        if (input.value) {
            wrapper.classList.add('focused');
        }
    }
    
    /**
     * Basic form validation
     */
    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    /**
     * Setup modal enhancements
     */
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                const modalId = trigger.getAttribute('data-bs-target');
                const modal = document.querySelector(modalId);
                
                if (modal) {
                    this.enhanceModal(modal);
                }
            });
        });
    }
    
    /**
     * Enhance modal with custom animations
     */
    enhanceModal(modal) {
        const modalDialog = modal.querySelector('.modal-dialog');
        
        modal.addEventListener('show.bs.modal', () => {
            modalDialog.style.transform = 'scale(0.8) translateY(-50px)';
            modalDialog.style.opacity = '0';
        });
        
        modal.addEventListener('shown.bs.modal', () => {
            modalDialog.style.transition = 'all 0.3s ease-out';
            modalDialog.style.transform = 'scale(1) translateY(0)';
            modalDialog.style.opacity = '1';
        });
    }
    
    /**
     * Setup carousel enhancements
     */
    setupCarousels() {
        const carousels = document.querySelectorAll('.carousel');
        
        carousels.forEach(carousel => {
            // Add touch/swipe support for mobile
            let startX = 0;
            let endX = 0;
            
            carousel.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
            });
            
            carousel.addEventListener('touchend', (e) => {
                endX = e.changedTouches[0].clientX;
                const diff = startX - endX;
                
                if (Math.abs(diff) > 50) {
                    if (diff > 0) {
                        // Swipe left - next slide
                        const nextBtn = carousel.querySelector('.carousel-control-next');
                        nextBtn?.click();
                    } else {
                        // Swipe right - previous slide
                        const prevBtn = carousel.querySelector('.carousel-control-prev');
                        prevBtn?.click();
                    }
                }
            });
        });
    }
    
    /**
     * Setup lazy loading for images
     */
    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }
    
    /**
     * Setup performance optimizations
     */
    setupPerformanceOptimizations() {
        // Debounced scroll handler
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(() => {
                this.handleScroll();
            }, 16); // ~60fps
        });
        
        // Preload critical assets
        this.preloadAssets();
    }
    
    /**
     * Handle scroll events (debounced)
     */
    handleScroll() {
        this.scrollPosition = window.pageYOffset;
        
        // Update CSS custom property for scroll-based animations
        document.documentElement.style.setProperty('--scroll-y', this.scrollPosition + 'px');
    }
    
    /**
     * Preload critical assets
     */
    preloadAssets() {
        const criticalImages = [
            '/scholarix_theme/static/src/img/logo.png',
            '/scholarix_theme/static/src/img/hero-bg.jpg'
        ];
        
        criticalImages.forEach(src => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = src;
            document.head.appendChild(link);
        });
    }
    
    /**
     * Setup accessibility improvements
     */
    setupAccessibility() {
        // Skip to main content link
        this.createSkipLink();
        
        // Keyboard navigation improvements
        this.setupKeyboardNavigation();
        
        // Focus management
        this.setupFocusManagement();
    }
    
    /**
     * Create skip to main content link
     */
    createSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'scholarix-skip-link';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #000;
            color: #fff;
            padding: 8px;
            text-decoration: none;
            z-index: 10000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }
    
    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        // Handle escape key for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const closeButton = openModal.querySelector('.btn-close, [data-bs-dismiss="modal"]');
                    closeButton?.click();
                }
            }
        });
    }
    
    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Ensure focus is visible
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }
    
    /**
     * Smooth scroll to target element
     */
    smoothScrollTo(target, duration = 1000) {
        let targetElement;
        
        if (typeof target === 'string') {
            targetElement = target === '#top' ? document.body : document.querySelector(target);
        } else {
            targetElement = target;
        }
        
        if (!targetElement) return;
        
        const targetPosition = targetElement.offsetTop - (document.querySelector('.navbar')?.offsetHeight || 0);
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;
        
        const easeInOutCubic = (t) => {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        };
        
        const animation = (currentTime) => {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = easeInOutCubic(timeElapsed / duration) * distance + startPosition;
            
            window.scrollTo(0, run);
            
            if (timeElapsed < duration) {
                requestAnimationFrame(animation);
            }
        };
        
        requestAnimationFrame(animation);
    }
    
    /**
     * Utility method to show notifications
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `scholarix-notification scholarix-notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: rgba(26, 26, 26, 0.95);
            border: 1px solid var(--scholarix-electric-blue);
            border-radius: 8px;
            color: #fff;
            font-family: var(--scholarix-font-secondary);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease-out;
            backdrop-filter: blur(10px);
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    }
}

// Initialize theme when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.ScholarixTheme = new ScholarixTheme();
});

// Handle page visibility changes for performance
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause animations when tab is not visible
        document.body.classList.add('page-hidden');
    } else {
        document.body.classList.remove('page-hidden');
    }
});

// Return the theme class for Odoo
return ScholarixTheme;

});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScholarixTheme;
}
