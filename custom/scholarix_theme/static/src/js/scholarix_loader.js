/**
 * Scholarix AI Theme - Advanced Loading Effects
 * Comprehensive loading system with logo animation and progress tracking
 */

class ScholarixLoader {
    constructor() {
        this.isLoaded = false;
        this.loadProgress = 0;
        this.loadingElements = [];
        this.criticalAssets = [
            '/scholarix_theme/static/src/img/logo.png',
            '/scholarix_theme/static/src/css/scholarix_main.css',
            '/scholarix_theme/static/src/js/scholarix_animations.js'
        ];
        
        this.init();
    }
    
    /**
     * Initialize the loading system
     */
    init() {
        this.createLoadingScreen();
        this.preloadAssets();
        this.setupProgressTracking();
        this.setupLoadingAnimations();
    }
    
    /**
     * Create the advanced loading screen
     */
    createLoadingScreen() {
        const loadingHTML = `
            <div id="scholarix-loading-screen" class="scholarix-loading-screen active">
                <!-- Background Effects -->
                <div class="scholarix-loading-bg">
                    <canvas id="scholarix-loading-particles" class="scholarix-loading-canvas"></canvas>
                    <div class="scholarix-loading-grid"></div>
                    <div class="scholarix-loading-waves"></div>
                </div>
                
                <!-- Main Loading Content -->
                <div class="scholarix-loading-content">
                    <!-- Animated Logo -->
                    <div class="scholarix-loading-logo">
                        <div class="scholarix-logo-container">
                            <img src="/scholarix_theme/static/src/img/logo.png" alt="Scholarix" class="scholarix-logo-image" />
                            <div class="scholarix-logo-glow"></div>
                            <div class="scholarix-logo-ring"></div>
                            <div class="scholarix-logo-particles"></div>
                        </div>
                    </div>
                    
                    <!-- Loading Text -->
                    <div class="scholarix-loading-text">
                        <h2 class="scholarix-loading-title">
                            <span class="scholarix-text-animate">Initializing AI Systems</span>
                        </h2>
                        <div class="scholarix-loading-subtitle">
                            <span class="scholarix-typewriter" id="loading-message">
                                Loading neural networks...
                            </span>
                        </div>
                    </div>
                    
                    <!-- Progress Bar -->
                    <div class="scholarix-loading-progress">
                        <div class="scholarix-progress-container">
                            <div class="scholarix-progress-bar">
                                <div class="scholarix-progress-fill" id="loading-progress-fill"></div>
                                <div class="scholarix-progress-glow"></div>
                            </div>
                            <div class="scholarix-progress-text">
                                <span id="loading-percentage">0%</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Loading Steps -->
                    <div class="scholarix-loading-steps">
                        <div class="scholarix-step" data-step="1">
                            <div class="scholarix-step-icon">
                                <i class="fas fa-brain"></i>
                            </div>
                            <span>Neural Network</span>
                        </div>
                        <div class="scholarix-step" data-step="2">
                            <div class="scholarix-step-icon">
                                <i class="fas fa-database"></i>
                            </div>
                            <span>Data Processing</span>
                        </div>
                        <div class="scholarix-step" data-step="3">
                            <div class="scholarix-step-icon">
                                <i class="fas fa-cogs"></i>
                            </div>
                            <span>System Optimization</span>
                        </div>
                        <div class="scholarix-step" data-step="4">
                            <div class="scholarix-step-icon">
                                <i class="fas fa-rocket"></i>
                            </div>
                            <span>Launch Sequence</span>
                        </div>
                    </div>
                </div>
                
                <!-- Skip Button (appears after 3 seconds) -->
                <button class="scholarix-skip-loading" id="skip-loading" style="opacity: 0;">
                    <span>Skip Intro</span>
                    <i class="fas fa-forward"></i>
                </button>
            </div>
        `;
        
        // Insert at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', loadingHTML);
        
        // Show skip button after 3 seconds
        setTimeout(() => {
            const skipBtn = document.getElementById('skip-loading');
            if (skipBtn) {
                skipBtn.style.opacity = '1';
                skipBtn.addEventListener('click', () => this.completeLoading());
            }
        }, 3000);
    }
    
    /**
     * Setup loading progress tracking
     */
    setupProgressTracking() {
        const steps = [
            { message: "Loading neural networks...", duration: 800 },
            { message: "Initializing AI algorithms...", duration: 1200 },
            { message: "Processing quantum data...", duration: 900 },
            { message: "Optimizing machine learning models...", duration: 1100 },
            { message: "Calibrating holographic interface...", duration: 700 },
            { message: "Synchronizing blockchain protocols...", duration: 600 },
            { message: "Activating cybernetic systems...", duration: 500 },
            { message: "Loading complete. Welcome to the future.", duration: 800 }
        ];
        
        let currentStep = 0;
        let currentProgress = 0;
        const progressFill = document.getElementById('loading-progress-fill');
        const progressText = document.getElementById('loading-percentage');
        const loadingMessage = document.getElementById('loading-message');
        const loadingSteps = document.querySelectorAll('.scholarix-step');
        
        const updateProgress = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                const targetProgress = ((currentStep + 1) / steps.length) * 100;
                
                // Update message
                if (loadingMessage) {
                    loadingMessage.textContent = step.message;
                }
                
                // Animate progress bar
                const progressInterval = setInterval(() => {
                    currentProgress += 2;
                    if (currentProgress >= targetProgress) {
                        currentProgress = targetProgress;
                        clearInterval(progressInterval);
                        
                        // Activate corresponding step
                        if (loadingSteps[currentStep]) {
                            loadingSteps[currentStep].classList.add('active');
                        }
                        
                        currentStep++;
                        setTimeout(updateProgress, step.duration);
                    }
                    
                    if (progressFill) progressFill.style.width = currentProgress + '%';
                    if (progressText) progressText.textContent = Math.round(currentProgress) + '%';
                }, 50);
                
                if (currentStep === steps.length - 1) {
                    setTimeout(() => this.completeLoading(), step.duration + 500);
                }
            }
        };
        
        // Start progress after initial delay
        setTimeout(updateProgress, 1000);
    }
    
    /**
     * Setup loading animations
     */
    setupLoadingAnimations() {
        this.initLoadingParticles();
        this.animateLoadingElements();
    }
    
    /**
     * Initialize loading screen particle effects
     */
    initLoadingParticles() {
        const canvas = document.getElementById('scholarix-loading-particles');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const particles = [];
        const particleCount = 50;
        
        class LoadingParticle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 3 + 1;
                this.speedX = Math.random() * 2 - 1;
                this.speedY = Math.random() * 2 - 1;
                this.opacity = Math.random() * 0.8 + 0.2;
                this.color = this.getRandomColor();
            }
            
            getRandomColor() {
                const colors = ['#00E5FF', '#40C4FF', '#7C4DFF', '#00BCD4'];
                return colors[Math.floor(Math.random() * colors.length)];
            }
            
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                
                if (this.x > canvas.width) this.x = 0;
                if (this.x < 0) this.x = canvas.width;
                if (this.y > canvas.height) this.y = 0;
                if (this.y < 0) this.y = canvas.height;
            }
            
            draw() {
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                
                // Add glow effect
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }
        
        // Create particles
        for (let i = 0; i < particleCount; i++) {
            particles.push(new LoadingParticle());
        }
        
        // Animation loop
        const animateLoadingParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                particle.update();
                particle.draw();
            });
            
            if (!this.isLoaded) {
                requestAnimationFrame(animateLoadingParticles);
            }
        };
        
        animateLoadingParticles();
    }
    
    /**
     * Animate loading screen elements
     */
    animateLoadingElements() {
        // Logo animation
        const logoContainer = document.querySelector('.scholarix-logo-container');
        if (logoContainer) {
            logoContainer.style.transform = 'scale(0) rotate(180deg)';
            logoContainer.style.opacity = '0';
            
            setTimeout(() => {
                logoContainer.style.transition = 'all 1s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                logoContainer.style.transform = 'scale(1) rotate(0deg)';
                logoContainer.style.opacity = '1';
            }, 500);
        }
        
        // Text animations
        const titleElement = document.querySelector('.scholarix-loading-title');
        if (titleElement) {
            const text = titleElement.textContent;
            titleElement.innerHTML = '';
            
            text.split('').forEach((char, index) => {
                const span = document.createElement('span');
                span.textContent = char === ' ' ? '\u00A0' : char;
                span.style.animationDelay = `${index * 0.1}s`;
                span.classList.add('scholarix-char-animate');
                titleElement.appendChild(span);
            });
        }
    }
    
    /**
     * Preload critical assets
     */
    preloadAssets() {
        const promises = this.criticalAssets.map(asset => {
            return new Promise((resolve) => {
                if (asset.endsWith('.png') || asset.endsWith('.jpg') || asset.endsWith('.svg')) {
                    const img = new Image();
                    img.onload = () => resolve();
                    img.onerror = () => resolve(); // Continue even if image fails
                    img.src = asset;
                } else {
                    // For CSS/JS files, create link/script tags
                    const element = asset.endsWith('.css') ? 
                        document.createElement('link') : 
                        document.createElement('script');
                    
                    element.onload = () => resolve();
                    element.onerror = () => resolve();
                    
                    if (asset.endsWith('.css')) {
                        element.rel = 'stylesheet';
                        element.href = asset;
                    } else {
                        element.src = asset;
                    }
                    
                    document.head.appendChild(element);
                }
            });
        });
        
        Promise.all(promises).then(() => {
            console.log('Critical assets preloaded');
        });
    }
    
    /**
     * Complete the loading process
     */
    completeLoading() {
        if (this.isLoaded) return;
        
        this.isLoaded = true;
        const loadingScreen = document.getElementById('scholarix-loading-screen');
        
        if (loadingScreen) {
            // Final animation sequence
            loadingScreen.classList.add('scholarix-loading-complete');
            
            setTimeout(() => {
                loadingScreen.style.opacity = '0';
                loadingScreen.style.pointerEvents = 'none';
                
                setTimeout(() => {
                    loadingScreen.remove();
                    this.initializeMainTheme();
                }, 500);
            }, 1000);
        }
    }
    
    /**
     * Initialize main theme after loading
     */
    initializeMainTheme() {
        // Trigger main theme initialization
        if (window.ScholarixTheme) {
            console.log('Main theme initialized after loading');
        }
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('scholarixLoaded', {
            detail: { timestamp: Date.now() }
        }));
        
        // Start main animations
        if (window.ScholarixAnimations) {
            window.ScholarixAnimations.startAnimations();
        }
        
        if (window.ScholarixParticles) {
            window.ScholarixParticles.init();
        }
    }
}

// Auto-initialize loading system
document.addEventListener('DOMContentLoaded', () => {
    window.ScholarixLoader = new ScholarixLoader();
});

// Handle page visibility for performance
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.ScholarixLoader && !window.ScholarixLoader.isLoaded) {
        // Pause loading animations when tab is not visible
        document.body.classList.add('loading-paused');
    } else {
        document.body.classList.remove('loading-paused');
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScholarixLoader;
}
