/**
 * Scholarix AI Theme - Advanced Mouse Effects
 * Custom cursor and interactive mouse tracking system
 */

class ScholarixCursor {
    constructor() {
        this.cursor = null;
        this.follower = null;
        this.mouseX = 0;
        this.mouseY = 0;
        this.followerX = 0;
        this.followerY = 0;
        this.isHovering = false;
        this.isClicking = false;
        
        this.init();
    }
    
    /**
     * Initialize the custom cursor system
     */
    init() {
        this.createCursor();
        this.setupEventListeners();
        this.startAnimation();
    }
    
    /**
     * Create custom cursor elements
     */
    createCursor() {
        // Main cursor dot
        this.cursor = document.createElement('div');
        this.cursor.className = 'scholarix-cursor';
        this.cursor.innerHTML = `
            <div class="scholarix-cursor-dot"></div>
            <div class="scholarix-cursor-ring"></div>
        `;
        
        // Cursor follower/trail
        this.follower = document.createElement('div');
        this.follower.className = 'scholarix-cursor-follower';
        
        // Add to DOM
        document.body.appendChild(this.cursor);
        document.body.appendChild(this.follower);
        
        // Hide default cursor
        document.body.style.cursor = 'none';
        
        // Add cursor styles to specific elements
        this.addCursorStyles();
    }
    
    /**
     * Add cursor-specific styles
     */
    addCursorStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .scholarix-cursor {
                position: fixed;
                top: 0;
                left: 0;
                width: 20px;
                height: 20px;
                pointer-events: none;
                z-index: 10000;
                mix-blend-mode: difference;
                transition: transform 0.1s ease-out;
            }
            
            .scholarix-cursor-dot {
                width: 8px;
                height: 8px;
                background: #00E5FF;
                border-radius: 50%;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                transition: all 0.2s ease-out;
                box-shadow: 0 0 10px #00E5FF;
            }
            
            .scholarix-cursor-ring {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(0, 229, 255, 0.3);
                border-radius: 50%;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) scale(1);
                transition: all 0.3s ease-out;
                animation: scholarix-cursor-pulse 2s ease-in-out infinite;
            }
            
            .scholarix-cursor-follower {
                position: fixed;
                top: 0;
                left: 0;
                width: 40px;
                height: 40px;
                background: radial-gradient(circle, rgba(0, 229, 255, 0.1) 0%, rgba(124, 77, 255, 0.05) 50%, transparent 100%);
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                transition: transform 0.15s ease-out;
                filter: blur(2px);
            }
            
            /* Hover states */
            .scholarix-cursor.hover .scholarix-cursor-dot {
                background: #7C4DFF;
                transform: translate(-50%, -50%) scale(1.5);
                box-shadow: 0 0 20px #7C4DFF;
            }
            
            .scholarix-cursor.hover .scholarix-cursor-ring {
                transform: translate(-50%, -50%) scale(2);
                border-color: rgba(124, 77, 255, 0.6);
            }
            
            .scholarix-cursor.hover .scholarix-cursor-follower {
                transform: scale(1.5);
                background: radial-gradient(circle, rgba(124, 77, 255, 0.2) 0%, rgba(0, 229, 255, 0.1) 50%, transparent 100%);
            }
            
            /* Click states */
            .scholarix-cursor.click .scholarix-cursor-dot {
                background: #40C4FF;
                transform: translate(-50%, -50%) scale(0.8);
            }
            
            .scholarix-cursor.click .scholarix-cursor-ring {
                transform: translate(-50%, -50%) scale(0.5);
            }
            
            /* Text selection state */
            .scholarix-cursor.text .scholarix-cursor-dot {
                width: 2px;
                height: 16px;
                border-radius: 2px;
                background: linear-gradient(180deg, #00E5FF 0%, #7C4DFF 100%);
            }
            
            .scholarix-cursor.text .scholarix-cursor-ring {
                opacity: 0;
            }
            
            /* Loading state */
            .scholarix-cursor.loading .scholarix-cursor-ring {
                animation: scholarix-cursor-loading 1s linear infinite;
                border: 2px solid transparent;
                border-top: 2px solid #00E5FF;
                border-right: 2px solid #7C4DFF;
            }
            
            @keyframes scholarix-cursor-pulse {
                0%, 100% {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 1;
                }
                50% {
                    transform: translate(-50%, -50%) scale(1.2);
                    opacity: 0.7;
                }
            }
            
            @keyframes scholarix-cursor-loading {
                0% { transform: translate(-50%, -50%) rotate(0deg); }
                100% { transform: translate(-50%, -50%) rotate(360deg); }
            }
            
            /* Hide custom cursor on touch devices */
            @media (hover: none) and (pointer: coarse) {
                .scholarix-cursor,
                .scholarix-cursor-follower {
                    display: none !important;
                }
                
                body {
                    cursor: auto !important;
                }
            }
            
            /* Cursor interactions for specific elements */
            a, button, .btn, input, textarea, select, [data-bs-toggle], [role="button"] {
                cursor: none;
            }
            
            /* Trail effect for mouse movement */
            .scholarix-mouse-trail {
                position: fixed;
                width: 6px;
                height: 6px;
                background: radial-gradient(circle, #00E5FF 0%, transparent 70%);
                border-radius: 50%;
                pointer-events: none;
                z-index: 9998;
                animation: scholarix-trail-fade 0.8s ease-out forwards;
            }
            
            @keyframes scholarix-trail-fade {
                0% {
                    transform: scale(1);
                    opacity: 0.8;
                }
                100% {
                    transform: scale(0);
                    opacity: 0;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Mouse movement
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
            
            // Create trail effect
            this.createTrail(e.clientX, e.clientY);
        });
        
        // Mouse enter/leave for hover states
        document.addEventListener('mouseover', (e) => {
            this.handleHover(e.target, true);
        });
        
        document.addEventListener('mouseout', (e) => {
            this.handleHover(e.target, false);
        });
        
        // Click events
        document.addEventListener('mousedown', () => {
            this.isClicking = true;
            this.cursor.classList.add('click');
        });
        
        document.addEventListener('mouseup', () => {
            this.isClicking = false;
            this.cursor.classList.remove('click');
        });
        
        // Context menu
        document.addEventListener('contextmenu', (e) => {
            this.createRipple(e.clientX, e.clientY, '#7C4DFF');
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Page visibility
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.cursor.style.opacity = '0';
                this.follower.style.opacity = '0';
            } else {
                this.cursor.style.opacity = '1';
                this.follower.style.opacity = '1';
            }
        });
    }
    
    /**
     * Handle hover states for different elements
     */
    handleHover(element, isHovering) {
        this.isHovering = isHovering;
        
        // Remove all hover classes
        this.cursor.classList.remove('hover', 'text', 'loading');
        
        if (isHovering) {
            // Check element type and apply appropriate cursor state
            if (this.isInteractiveElement(element)) {
                this.cursor.classList.add('hover');
                
                // Special states for specific elements
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    this.cursor.classList.add('text');
                } else if (element.classList.contains('loading') || element.getAttribute('data-loading')) {
                    this.cursor.classList.add('loading');
                }
                
                // Add ripple effect on hover
                const rect = element.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                this.createRipple(centerX, centerY, '#00E5FF', 0.3);
            }
        }
    }
    
    /**
     * Check if element is interactive
     */
    isInteractiveElement(element) {
        const interactiveTags = ['A', 'BUTTON', 'INPUT', 'TEXTAREA', 'SELECT'];
        const interactiveRoles = ['button', 'link', 'menuitem', 'tab'];
        const interactiveClasses = ['btn', 'card', 'nav-link'];
        
        return interactiveTags.includes(element.tagName) ||
               interactiveRoles.includes(element.getAttribute('role')) ||
               interactiveClasses.some(cls => element.classList.contains(cls)) ||
               element.hasAttribute('data-bs-toggle') ||
               element.style.cursor === 'pointer';
    }
    
    /**
     * Create mouse trail effect
     */
    createTrail(x, y) {
        const trail = document.createElement('div');
        trail.className = 'scholarix-mouse-trail';
        trail.style.left = x + 'px';
        trail.style.top = y + 'px';
        
        document.body.appendChild(trail);
        
        // Remove trail element after animation
        setTimeout(() => {
            trail.remove();
        }, 800);
    }
    
    /**
     * Create ripple effect
     */
    createRipple(x, y, color = '#00E5FF', opacity = 0.6) {
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: radial-gradient(circle, ${color} 0%, transparent 70%);
            pointer-events: none;
            z-index: 9997;
            opacity: ${opacity};
            animation: scholarix-ripple 0.6s ease-out forwards;
        `;
        
        // Add ripple animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes scholarix-ripple {
                0% {
                    width: 0;
                    height: 0;
                    margin-left: 0;
                    margin-top: 0;
                    opacity: ${opacity};
                }
                100% {
                    width: 100px;
                    height: 100px;
                    margin-left: -50px;
                    margin-top: -50px;
                    opacity: 0;
                }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
            style.remove();
        }, 600);
    }
    
    /**
     * Animation loop for smooth cursor movement
     */
    startAnimation() {
        const animate = () => {
            // Smooth cursor movement
            this.cursor.style.transform = `translate(${this.mouseX}px, ${this.mouseY}px)`;
            
            // Smooth follower movement with easing
            this.followerX += (this.mouseX - this.followerX) * 0.1;
            this.followerY += (this.mouseY - this.followerY) * 0.1;
            
            this.follower.style.transform = `translate(${this.followerX - 20}px, ${this.followerY - 20}px)`;
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        // Adjust cursor position if needed
        const rect = document.body.getBoundingClientRect();
        if (this.mouseX > rect.width || this.mouseY > rect.height) {
            this.cursor.style.opacity = '0';
            this.follower.style.opacity = '0';
        } else {
            this.cursor.style.opacity = '1';
            this.follower.style.opacity = '1';
        }
    }
    
    /**
     * Destroy cursor system
     */
    destroy() {
        if (this.cursor) {
            this.cursor.remove();
        }
        if (this.follower) {
            this.follower.remove();
        }
        
        document.body.style.cursor = 'auto';
    }
}

// Initialize cursor system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on non-touch devices
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        window.ScholarixCursor = new ScholarixCursor();
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScholarixCursor;
}
