/**
 * Scholarix AI Theme - Animation Controller
 * Handles advanced animations and interactive effects
 */

class ScholarixAnimations {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupParallax();
        this.setupTextAnimations();
        this.setupGlowEffects();
        this.setupLoadingAnimations();
    }
    
    /**
     * Setup scroll-triggered animations using Intersection Observer
     */
    setupScrollAnimations() {
        // Scroll reveal animation
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('scholarix-revealed');
                }
            });
        }, observerOptions);
        
        // Observe all elements with scroll reveal class
        document.querySelectorAll('.scholarix-scroll-reveal').forEach(el => {
            observer.observe(el);
        });
        
        // Animate counters when they come into view
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                }
            });
        }, observerOptions);
        
        document.querySelectorAll('.scholarix-stat-number').forEach(el => {
            counterObserver.observe(el);
        });
    }
    
    /**
     * Animate number counters
     */
    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target')) || parseInt(element.textContent);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString();
        }, 16);
    }
    
    /**
     * Setup advanced hover effects
     */
    setupHoverEffects() {
        // Service cards with magnetic hover effect
        document.querySelectorAll('.scholarix-service-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
            });
        });
        
        // Portfolio items with tilt effect
        document.querySelectorAll('.scholarix-portfolio-item').forEach(item => {
            item.addEventListener('mouseenter', (e) => {
                this.createRippleEffect(e.target, e);
            });
        });
    }
    
    /**
     * Create ripple effect on click/hover
     */
    createRippleEffect(element, event) {
        const ripple = document.createElement('div');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: radial-gradient(circle, rgba(0, 229, 255, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            transform: scale(0);
            animation: scholarixRipple 0.8s ease-out forwards;
        `;
        
        if (element.style.position !== 'relative') {
            element.style.position = 'relative';
        }
        
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 800);
    }
    
    /**
     * Setup parallax scrolling effects
     */
    setupParallax() {
        const parallaxElements = document.querySelectorAll('.scholarix-parallax');
        
        if (parallaxElements.length === 0) return;
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }
    
    /**
     * Setup text animations (typing effect)
     */
    setupTextAnimations() {
        const typingElements = document.querySelectorAll('.scholarix-text-typing');
        
        typingElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.style.borderRight = '2px solid var(--scholarix-electric-blue)';
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                } else {
                    // Blinking cursor effect
                    setInterval(() => {
                        element.style.borderRightColor = 
                            element.style.borderRightColor === 'transparent' 
                                ? 'var(--scholarix-electric-blue)' 
                                : 'transparent';
                    }, 750);
                }
            };
            
            // Start typing animation when element comes into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        setTimeout(typeWriter, 500);
                        observer.unobserve(element);
                    }
                });
            });
            
            observer.observe(element);
        });
    }
    
    /**
     * Setup dynamic glow effects
     */
    setupGlowEffects() {
        // Dynamic glow based on scroll position
        window.addEventListener('scroll', () => {
            const scrollPercentage = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
            const glowIntensity = Math.sin((scrollPercentage / 100) * Math.PI) * 0.5 + 0.5;
            
            document.documentElement.style.setProperty('--glow-intensity', glowIntensity);
        });
        
        // Interactive glow on mouse movement
        document.addEventListener('mousemove', (e) => {
            const glowElements = document.querySelectorAll('.scholarix-interactive-glow');
            
            glowElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                element.style.setProperty('--mouse-x', `${x}px`);
                element.style.setProperty('--mouse-y', `${y}px`);
            });
        });
    }
    
    /**
     * Setup loading animations
     */
    setupLoadingAnimations() {
        // Simulate loading for demonstration
        const loadingElements = document.querySelectorAll('.scholarix-loading');
        
        loadingElements.forEach(element => {
            setTimeout(() => {
                element.classList.remove('scholarix-loading');
                element.classList.add('scholarix-loaded');
            }, 2000);
        });
    }
    
    /**
     * Create floating particles effect
     */
    createFloatingParticles(container) {
        const particleCount = 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'scholarix-particle';
            
            particle.style.cssText = `
                position: absolute;
                width: 2px;
                height: 2px;
                background: rgba(0, 229, 255, ${Math.random() * 0.5 + 0.2});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: scholarixParticleFloat ${Math.random() * 10 + 10}s linear infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            
            container.appendChild(particle);
        }
    }
    
    /**
     * Smooth scroll to element
     */
    smoothScrollTo(target, duration = 1000) {
        const targetElement = document.querySelector(target);
        if (!targetElement) return;
        
        const targetPosition = targetElement.offsetTop;
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
}

// CSS for ripple animation (to be added dynamically)
const style = document.createElement('style');
style.textContent = `
    @keyframes scholarixRipple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    @keyframes scholarixParticleFloat {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 0.7;
        }
        50% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScholarixAnimations();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScholarixAnimations;
}
