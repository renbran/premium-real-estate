/**
 * Scholarix AI Theme - 3D Hero Section Effects
 * Advanced 3D transformations and interactive hero elements
 */

class Scholarix3DHero {
    constructor() {
        this.isInitialized = false;
        this.mouseX = 0;
        this.mouseY = 0;
        this.windowWidth = window.innerWidth;
        this.windowHeight = window.innerHeight;
        this.elements = {};
        
        this.init();
    }
    
    /**
     * Initialize 3D hero effects
     */
    init() {
        if (this.isInitialized) return;
        
        this.setupElements();
        this.create3DEnvironment();
        this.setupParallaxEffects();
        this.setupInteractiveElements();
        this.setupEventListeners();
        this.startAnimationLoop();
        
        this.isInitialized = true;
        console.log('Scholarix 3D Hero initialized');
    }
    
    /**
     * Setup hero elements
     */
    setupElements() {
        this.elements = {
            hero: document.querySelector('.scholarix-hero'),
            heroContent: document.querySelector('.scholarix-hero-content'),
            heroVisual: document.querySelector('.scholarix-hero-visual'),
            heroTitle: document.querySelector('.scholarix-hero-title'),
            heroSubtitle: document.querySelector('.scholarix-hero-subtitle'),
            logoImage: document.querySelector('.scholarix-brain-image'),
            particleContainer: document.querySelector('.scholarix-hero-particles'),
            background: document.querySelector('.scholarix-hero-bg')
        };
        
        // Create 3D elements if they don't exist
        if (!this.elements.heroVisual) {
            this.createHeroVisual();
        }
    }
    
    /**
     * Create 3D hero visual elements
     */
    createHeroVisual() {
        const heroSection = this.elements.hero;
        if (!heroSection) return;
        
        // Create 3D visual container
        const visualHTML = `
            <div class="scholarix-hero-3d-container">
                <!-- 3D Logo/Brain Element -->
                <div class="scholarix-3d-logo-wrapper">
                    <div class="scholarix-3d-logo">
                        <div class="scholarix-logo-front">
                            <img src="/scholarix_theme/static/src/img/logo.png" alt="Scholarix AI" class="scholarix-3d-logo-image" />
                        </div>
                        <div class="scholarix-logo-back">
                            <div class="scholarix-neural-pattern"></div>
                        </div>
                        <div class="scholarix-logo-glow-sphere"></div>
                    </div>
                </div>
                
                <!-- Floating 3D Elements -->
                <div class="scholarix-floating-elements">
                    <div class="scholarix-float-cube" data-speed="0.5" data-axis="x">
                        <div class="scholarix-cube-face front"></div>
                        <div class="scholarix-cube-face back"></div>
                        <div class="scholarix-cube-face right"></div>
                        <div class="scholarix-cube-face left"></div>
                        <div class="scholarix-cube-face top"></div>
                        <div class="scholarix-cube-face bottom"></div>
                    </div>
                    
                    <div class="scholarix-float-sphere" data-speed="0.3" data-axis="y">
                        <div class="scholarix-sphere-glow"></div>
                    </div>
                    
                    <div class="scholarix-float-pyramid" data-speed="0.7" data-axis="z">
                        <div class="scholarix-pyramid-face face1"></div>
                        <div class="scholarix-pyramid-face face2"></div>
                        <div class="scholarix-pyramid-face face3"></div>
                        <div class="scholarix-pyramid-face face4"></div>
                    </div>
                </div>
                
                <!-- 3D Grid Background -->
                <div class="scholarix-3d-grid">
                    <div class="scholarix-grid-lines horizontal"></div>
                    <div class="scholarix-grid-lines vertical"></div>
                    <div class="scholarix-grid-plane"></div>
                </div>
                
                <!-- Holographic Interface -->
                <div class="scholarix-holo-interface">
                    <div class="scholarix-holo-circle" data-delay="0"></div>
                    <div class="scholarix-holo-circle" data-delay="0.5"></div>
                    <div class="scholarix-holo-circle" data-delay="1"></div>
                    <div class="scholarix-holo-data-stream"></div>
                </div>
            </div>
        `;
        
        // Insert 3D elements
        const heroRow = heroSection.querySelector('.row');
        if (heroRow) {
            heroRow.insertAdjacentHTML('beforeend', `
                <div class="col-lg-6 scholarix-hero-3d-col">
                    ${visualHTML}
                </div>
            `);
        }
        
        // Update elements reference
        this.elements.heroVisual = document.querySelector('.scholarix-hero-3d-container');
    }
    
    /**
     * Create 3D environment and perspective
     */
    create3DEnvironment() {
        const hero = this.elements.hero;
        if (!hero) return;
        
        // Add 3D perspective to hero section
        hero.style.perspective = '1000px';
        hero.style.perspectiveOrigin = '50% 50%';
        hero.style.transformStyle = 'preserve-3d';
        
        // Add 3D styles
        const style3D = document.createElement('style');
        style3D.textContent = `
            .scholarix-hero-3d-container {
                position: relative;
                width: 100%;
                height: 600px;
                transform-style: preserve-3d;
                perspective: 1200px;
                overflow: visible;
            }
            
            .scholarix-3d-logo-wrapper {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotateX(0deg) rotateY(0deg);
                transition: transform 0.1s ease-out;
            }
            
            .scholarix-3d-logo {
                position: relative;
                width: 200px;
                height: 200px;
                transform-style: preserve-3d;
                animation: scholarix-logo-float 4s ease-in-out infinite;
            }
            
            .scholarix-logo-front,
            .scholarix-logo-back {
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                backface-visibility: hidden;
            }
            
            .scholarix-logo-front {
                transform: translateZ(20px);
                background: radial-gradient(circle, rgba(0, 229, 255, 0.1) 0%, transparent 70%);
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid rgba(0, 229, 255, 0.3);
            }
            
            .scholarix-3d-logo-image {
                width: 150px;
                height: 150px;
                filter: drop-shadow(0 0 20px #00E5FF);
                animation: scholarix-logo-glow 2s ease-in-out infinite alternate;
            }
            
            .scholarix-logo-back {
                transform: translateZ(-20px) rotateY(180deg);
                background: radial-gradient(circle, rgba(124, 77, 255, 0.1) 0%, transparent 70%);
                border: 2px solid rgba(124, 77, 255, 0.3);
            }
            
            .scholarix-neural-pattern {
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 20% 80%, #7C4DFF 2px, transparent 2px),
                    radial-gradient(circle at 80% 20%, #00E5FF 1px, transparent 1px),
                    radial-gradient(circle at 40% 40%, #40C4FF 1.5px, transparent 1.5px);
                background-size: 50px 50px, 30px 30px, 70px 70px;
                opacity: 0.6;
                animation: scholarix-neural-flow 8s linear infinite;
            }
            
            .scholarix-logo-glow-sphere {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 300px;
                height: 300px;
                transform: translate(-50%, -50%);
                background: radial-gradient(circle, rgba(0, 229, 255, 0.1) 0%, transparent 70%);
                border-radius: 50%;
                animation: scholarix-glow-pulse 3s ease-in-out infinite;
            }
            
            /* Floating 3D Elements */
            .scholarix-floating-elements {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }
            
            .scholarix-float-cube {
                position: absolute;
                width: 60px;
                height: 60px;
                top: 20%;
                right: 20%;
                transform-style: preserve-3d;
                animation: scholarix-cube-rotate 10s linear infinite;
            }
            
            .scholarix-cube-face {
                position: absolute;
                width: 60px;
                height: 60px;
                background: rgba(0, 229, 255, 0.1);
                border: 1px solid rgba(0, 229, 255, 0.3);
            }
            
            .scholarix-cube-face.front { transform: rotateY(0deg) translateZ(30px); }
            .scholarix-cube-face.back { transform: rotateY(180deg) translateZ(30px); }
            .scholarix-cube-face.right { transform: rotateY(90deg) translateZ(30px); }
            .scholarix-cube-face.left { transform: rotateY(-90deg) translateZ(30px); }
            .scholarix-cube-face.top { transform: rotateX(90deg) translateZ(30px); }
            .scholarix-cube-face.bottom { transform: rotateX(-90deg) translateZ(30px); }
            
            .scholarix-float-sphere {
                position: absolute;
                width: 80px;
                height: 80px;
                top: 70%;
                left: 10%;
                background: radial-gradient(circle, rgba(124, 77, 255, 0.2) 0%, transparent 70%);
                border-radius: 50%;
                animation: scholarix-sphere-float 6s ease-in-out infinite;
            }
            
            .scholarix-float-pyramid {
                position: absolute;
                width: 50px;
                height: 50px;
                top: 30%;
                left: 80%;
                transform-style: preserve-3d;
                animation: scholarix-pyramid-spin 8s linear infinite;
            }
            
            .scholarix-pyramid-face {
                position: absolute;
                width: 0;
                height: 0;
                border-left: 25px solid transparent;
                border-right: 25px solid transparent;
            }
            
            .scholarix-pyramid-face.face1 {
                border-bottom: 43px solid rgba(64, 196, 255, 0.2);
                transform: rotateX(0deg) translateZ(14px);
            }
            .scholarix-pyramid-face.face2 {
                border-bottom: 43px solid rgba(64, 196, 255, 0.15);
                transform: rotateX(120deg) translateZ(14px);
            }
            .scholarix-pyramid-face.face3 {
                border-bottom: 43px solid rgba(64, 196, 255, 0.1);
                transform: rotateX(240deg) translateZ(14px);
            }
            
            /* 3D Grid */
            .scholarix-3d-grid {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                transform: rotateX(75deg) translateZ(-100px);
                opacity: 0.3;
            }
            
            .scholarix-grid-lines {
                position: absolute;
                background: linear-gradient(90deg, transparent 0%, #00E5FF 50%, transparent 100%);
            }
            
            .scholarix-grid-lines.horizontal {
                width: 100%;
                height: 1px;
                animation: scholarix-grid-scan-h 4s ease-in-out infinite;
            }
            
            .scholarix-grid-lines.vertical {
                width: 1px;
                height: 100%;
                animation: scholarix-grid-scan-v 4s ease-in-out infinite reverse;
            }
            
            /* Holographic Interface */
            .scholarix-holo-interface {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }
            
            .scholarix-holo-circle {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 200px;
                height: 200px;
                border: 2px solid rgba(0, 229, 255, 0.4);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: scholarix-holo-expand 3s ease-out infinite;
            }
            
            .scholarix-holo-circle[data-delay="0.5"] {
                animation-delay: 0.5s;
                border-color: rgba(124, 77, 255, 0.4);
            }
            
            .scholarix-holo-circle[data-delay="1"] {
                animation-delay: 1s;
                border-color: rgba(64, 196, 255, 0.4);
            }
            
            /* Animations */
            @keyframes scholarix-logo-float {
                0%, 100% { transform: translateY(0px) rotateX(5deg); }
                50% { transform: translateY(-20px) rotateX(-5deg); }
            }
            
            @keyframes scholarix-logo-glow {
                0% { filter: drop-shadow(0 0 20px #00E5FF); }
                100% { filter: drop-shadow(0 0 40px #00E5FF) drop-shadow(0 0 60px #7C4DFF); }
            }
            
            @keyframes scholarix-neural-flow {
                0% { background-position: 0% 0%, 0% 0%, 0% 0%; }
                100% { background-position: 100% 100%, -100% -100%, 50% 50%; }
            }
            
            @keyframes scholarix-glow-pulse {
                0%, 100% { 
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 0.3;
                }
                50% { 
                    transform: translate(-50%, -50%) scale(1.2);
                    opacity: 0.6;
                }
            }
            
            @keyframes scholarix-cube-rotate {
                0% { transform: rotateX(0deg) rotateY(0deg); }
                100% { transform: rotateX(360deg) rotateY(360deg); }
            }
            
            @keyframes scholarix-sphere-float {
                0%, 100% { transform: translateY(0px) scale(1); }
                50% { transform: translateY(-30px) scale(1.1); }
            }
            
            @keyframes scholarix-pyramid-spin {
                0% { transform: rotateY(0deg) rotateZ(0deg); }
                100% { transform: rotateY(360deg) rotateZ(180deg); }
            }
            
            @keyframes scholarix-grid-scan-h {
                0%, 100% { transform: translateY(0); opacity: 0.3; }
                50% { transform: translateY(300px); opacity: 1; }
            }
            
            @keyframes scholarix-grid-scan-v {
                0%, 100% { transform: translateX(0); opacity: 0.3; }
                50% { transform: translateX(400px); opacity: 1; }
            }
            
            @keyframes scholarix-holo-expand {
                0% {
                    transform: translate(-50%, -50%) scale(0.8);
                    opacity: 1;
                }
                100% {
                    transform: translate(-50%, -50%) scale(2);
                    opacity: 0;
                }
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .scholarix-hero-3d-container {
                    height: 400px;
                }
                
                .scholarix-3d-logo {
                    width: 150px;
                    height: 150px;
                }
                
                .scholarix-3d-logo-image {
                    width: 100px;
                    height: 100px;
                }
                
                .scholarix-floating-elements {
                    display: none;
                }
            }
        `;
        
        document.head.appendChild(style3D);
    }
    
    /**
     * Setup parallax effects based on mouse movement
     */
    setupParallaxEffects() {
        this.parallaxElements = [
            { element: '.scholarix-3d-logo-wrapper', intensity: 0.2 },
            { element: '.scholarix-float-cube', intensity: 0.15 },
            { element: '.scholarix-float-sphere', intensity: 0.1 },
            { element: '.scholarix-float-pyramid', intensity: 0.25 },
            { element: '.scholarix-3d-grid', intensity: 0.05 }
        ];
    }
    
    /**
     * Setup interactive elements
     */
    setupInteractiveElements() {
        const logo = document.querySelector('.scholarix-3d-logo-wrapper');
        const floatingElements = document.querySelectorAll('.scholarix-floating-elements > *');
        
        // Logo interaction
        if (logo) {
            logo.addEventListener('mouseenter', () => {
                logo.style.transform += ' scale(1.1)';
                logo.style.filter = 'brightness(1.3)';
            });
            
            logo.addEventListener('mouseleave', () => {
                logo.style.transform = logo.style.transform.replace(' scale(1.1)', '');
                logo.style.filter = 'brightness(1)';
            });
        }
        
        // Floating elements interaction
        floatingElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.animationPlayState = 'paused';
                element.style.transform += ' scale(1.2)';
                element.style.filter = 'brightness(1.5)';
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.animationPlayState = 'running';
                element.style.transform = element.style.transform.replace(' scale(1.2)', '');
                element.style.filter = 'brightness(1)';
            });
        });
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Mouse movement for parallax
        document.addEventListener('mousemove', (e) => {
            this.mouseX = (e.clientX / this.windowWidth) * 2 - 1;
            this.mouseY = (e.clientY / this.windowHeight) * 2 - 1;
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.windowWidth = window.innerWidth;
            this.windowHeight = window.innerHeight;
        });
        
        // Scroll-based 3D effects
        window.addEventListener('scroll', () => {
            const scrollY = window.pageYOffset;
            const heroHeight = this.elements.hero?.offsetHeight || 0;
            const scrollProgress = Math.min(scrollY / heroHeight, 1);
            
            this.updateScrollEffects(scrollProgress);
        });
        
        // Device orientation for mobile 3D effects
        if (window.DeviceOrientationEvent) {
            window.addEventListener('deviceorientation', (e) => {
                this.handleDeviceOrientation(e);
            });
        }
    }
    
    /**
     * Start animation loop
     */
    startAnimationLoop() {
        const animate = () => {
            this.updateParallaxEffects();
            this.update3DTransforms();
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    /**
     * Update parallax effects based on mouse position
     */
    updateParallaxEffects() {
        this.parallaxElements.forEach(({ element, intensity }) => {
            const el = document.querySelector(element);
            if (!el) return;
            
            const moveX = this.mouseX * intensity * 50;
            const moveY = this.mouseY * intensity * 50;
            const rotateX = this.mouseY * intensity * 10;
            const rotateY = this.mouseX * intensity * 10;
            
            el.style.transform = `translate(${moveX}px, ${moveY}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
    }
    
    /**
     * Update 3D transforms
     */
    update3DTransforms() {
        const hero3D = document.querySelector('.scholarix-hero-3d-container');
        if (!hero3D) return;
        
        const tiltX = this.mouseY * 10;
        const tiltY = this.mouseX * -10;
        
        hero3D.style.transform = `rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
    }
    
    /**
     * Update scroll-based effects
     */
    updateScrollEffects(progress) {
        const elements = {
            logo: document.querySelector('.scholarix-3d-logo-wrapper'),
            floatingElements: document.querySelectorAll('.scholarix-floating-elements > *'),
            grid: document.querySelector('.scholarix-3d-grid')
        };
        
        // Logo scroll effects
        if (elements.logo) {
            const scale = 1 + (progress * 0.5);
            const rotateY = progress * 180;
            elements.logo.style.transform += ` scale(${scale}) rotateY(${rotateY}deg)`;
        }
        
        // Floating elements scroll effects
        elements.floatingElements.forEach((element, index) => {
            const moveY = progress * 100 * (index + 1);
            const rotateZ = progress * 360;
            element.style.transform += ` translateY(-${moveY}px) rotateZ(${rotateZ}deg)`;
        });
        
        // Grid scroll effects
        if (elements.grid) {
            const perspective = 1000 - (progress * 500);
            elements.grid.style.transform = `rotateX(75deg) translateZ(-100px) perspective(${perspective}px)`;
        }
    }
    
    /**
     * Handle device orientation for mobile
     */
    handleDeviceOrientation(event) {
        if (window.innerWidth <= 768) {
            const tiltX = (event.beta - 90) / 90; // -1 to 1
            const tiltY = event.gamma / 90; // -1 to 1
            
            this.mouseX = Math.max(-1, Math.min(1, tiltY));
            this.mouseY = Math.max(-1, Math.min(1, tiltX));
        }
    }
    
    /**
     * Destroy 3D hero effects
     */
    destroy() {
        const hero3DContainer = document.querySelector('.scholarix-hero-3d-container');
        if (hero3DContainer) {
            hero3DContainer.remove();
        }
        
        this.isInitialized = false;
    }
}

// Initialize when DOM is ready and hero section exists
document.addEventListener('DOMContentLoaded', () => {
    // Wait for hero section to be available
    const checkHero = () => {
        const hero = document.querySelector('.scholarix-hero');
        if (hero) {
            window.Scholarix3DHero = new Scholarix3DHero();
        } else {
            setTimeout(checkHero, 100);
        }
    };
    
    checkHero();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Scholarix3DHero;
}
