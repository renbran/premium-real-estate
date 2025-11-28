/**
 * Scholarix AI Theme - Particle System
 * Creates dynamic particle effects for enhanced visual appeal
 */

class ScholarixParticles {
    constructor(options = {}) {
        this.options = {
            container: options.container || document.body,
            particleCount: options.particleCount || 100,
            particleSize: options.particleSize || 2,
            particleColor: options.particleColor || '#00E5FF',
            animationSpeed: options.animationSpeed || 1,
            interactionRadius: options.interactionRadius || 100,
            enableInteraction: options.enableInteraction !== false,
            particleTypes: options.particleTypes || ['dot', 'line', 'glow'],
            ...options
        };
        
        this.particles = [];
        this.mouse = { x: 0, y: 0 };
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
        
        this.init();
    }
    
    /**
     * Initialize the particle system
     */
    init() {
        this.createCanvas();
        this.createParticles();
        this.setupEventListeners();
        this.animate();
    }
    
    /**
     * Create canvas element for particle rendering
     */
    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'scholarix-particles-canvas';
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.7;
        `;
        
        this.ctx = this.canvas.getContext('2d');
        this.options.container.appendChild(this.canvas);
        
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    /**
     * Resize canvas to match window size
     */
    resizeCanvas() {
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = window.innerWidth * dpr;
        this.canvas.height = window.innerHeight * dpr;
        this.canvas.style.width = window.innerWidth + 'px';
        this.canvas.style.height = window.innerHeight + 'px';
        this.ctx.scale(dpr, dpr);
    }
    
    /**
     * Create individual particles
     */
    createParticles() {
        this.particles = [];
        
        for (let i = 0; i < this.options.particleCount; i++) {
            const particle = {
                id: i,
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                vx: (Math.random() - 0.5) * this.options.animationSpeed,
                vy: (Math.random() - 0.5) * this.options.animationSpeed,
                size: Math.random() * this.options.particleSize + 1,
                opacity: Math.random() * 0.5 + 0.2,
                color: this.getParticleColor(),
                type: this.getRandomParticleType(),
                originalSize: 0,
                connections: [],
                phase: Math.random() * Math.PI * 2,
                frequency: Math.random() * 0.02 + 0.01
            };
            
            particle.originalSize = particle.size;
            this.particles.push(particle);
        }
    }
    
    /**
     * Get random particle color from theme palette
     */
    getParticleColor() {
        const colors = [
            '#00E5FF', // Electric Blue
            '#40C4FF', // Neon Blue
            '#00BCD4', // Tech Teal
            '#7C4DFF', // Holographic Purple
            '#E0E0E0'  // Silver
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    /**
     * Get random particle type
     */
    getRandomParticleType() {
        return this.options.particleTypes[
            Math.floor(Math.random() * this.options.particleTypes.length)
        ];
    }
    
    /**
     * Setup event listeners for interaction
     */
    setupEventListeners() {
        if (this.options.enableInteraction) {
            window.addEventListener('mousemove', (e) => {
                this.mouse.x = e.clientX;
                this.mouse.y = e.clientY;
            });
            
            window.addEventListener('click', (e) => {
                this.createExplosion(e.clientX, e.clientY);
            });
        }
    }
    
    /**
     * Update particle positions and behavior
     */
    updateParticles() {
        this.particles.forEach((particle, i) => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around screen edges
            if (particle.x < 0) particle.x = window.innerWidth;
            if (particle.x > window.innerWidth) particle.x = 0;
            if (particle.y < 0) particle.y = window.innerHeight;
            if (particle.y > window.innerHeight) particle.y = 0;
            
            // Update phase for floating animation
            particle.phase += particle.frequency;
            
            // Apply floating motion
            particle.y += Math.sin(particle.phase) * 0.5;
            
            // Mouse interaction
            if (this.options.enableInteraction) {
                const dx = this.mouse.x - particle.x;
                const dy = this.mouse.y - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.options.interactionRadius) {
                    const force = (this.options.interactionRadius - distance) / this.options.interactionRadius;
                    const angle = Math.atan2(dy, dx);
                    
                    particle.vx -= Math.cos(angle) * force * 0.1;
                    particle.vy -= Math.sin(angle) * force * 0.1;
                    particle.size = particle.originalSize * (1 + force);
                    particle.opacity = Math.min(1, particle.opacity + force * 0.3);
                } else {
                    // Return to original state
                    particle.size += (particle.originalSize - particle.size) * 0.1;
                    particle.opacity += (0.5 - particle.opacity) * 0.05;
                }
            }
            
            // Apply velocity damping
            particle.vx *= 0.999;
            particle.vy *= 0.999;
            
            // Find nearby particles for connections
            particle.connections = [];
            for (let j = i + 1; j < this.particles.length; j++) {
                const other = this.particles[j];
                const dx = particle.x - other.x;
                const dy = particle.y - other.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    particle.connections.push({
                        particle: other,
                        distance: distance,
                        opacity: (150 - distance) / 150
                    });
                }
            }
        });
    }
    
    /**
     * Render particles on canvas
     */
    renderParticles() {
        this.ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        
        // Render connections first (behind particles)
        this.particles.forEach(particle => {
            particle.connections.forEach(connection => {
                this.ctx.beginPath();
                this.ctx.moveTo(particle.x, particle.y);
                this.ctx.lineTo(connection.particle.x, connection.particle.y);
                this.ctx.strokeStyle = `rgba(0, 229, 255, ${connection.opacity * 0.3})`;
                this.ctx.lineWidth = 0.5;
                this.ctx.stroke();
            });
        });
        
        // Render particles
        this.particles.forEach(particle => {
            this.ctx.save();
            this.ctx.globalAlpha = particle.opacity;
            
            switch (particle.type) {
                case 'dot':
                    this.renderDotParticle(particle);
                    break;
                case 'glow':
                    this.renderGlowParticle(particle);
                    break;
                case 'line':
                    this.renderLineParticle(particle);
                    break;
            }
            
            this.ctx.restore();
        });
    }
    
    /**
     * Render dot particle
     */
    renderDotParticle(particle) {
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        this.ctx.fillStyle = particle.color;
        this.ctx.fill();
    }
    
    /**
     * Render glow particle
     */
    renderGlowParticle(particle) {
        const gradient = this.ctx.createRadialGradient(
            particle.x, particle.y, 0,
            particle.x, particle.y, particle.size * 3
        );
        gradient.addColorStop(0, particle.color);
        gradient.addColorStop(1, 'transparent');
        
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.size * 3, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        
        // Inner bright core
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.size * 0.5, 0, Math.PI * 2);
        this.ctx.fillStyle = particle.color;
        this.ctx.fill();
    }
    
    /**
     * Render line particle
     */
    renderLineParticle(particle) {
        this.ctx.beginPath();
        this.ctx.moveTo(particle.x - particle.size, particle.y);
        this.ctx.lineTo(particle.x + particle.size, particle.y);
        this.ctx.strokeStyle = particle.color;
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.moveTo(particle.x, particle.y - particle.size);
        this.ctx.lineTo(particle.x, particle.y + particle.size);
        this.ctx.stroke();
    }
    
    /**
     * Create explosion effect at given coordinates
     */
    createExplosion(x, y) {
        for (let i = 0; i < 20; i++) {
            const angle = (Math.PI * 2 * i) / 20;
            const velocity = Math.random() * 5 + 2;
            
            const explosionParticle = {
                x: x,
                y: y,
                vx: Math.cos(angle) * velocity,
                vy: Math.sin(angle) * velocity,
                size: Math.random() * 3 + 1,
                opacity: 1,
                color: '#00E5FF',
                type: 'glow',
                life: 60,
                decay: 0.02
            };
            
            this.particles.push(explosionParticle);
        }
        
        // Remove explosion particles after animation
        setTimeout(() => {
            this.particles = this.particles.filter(p => p.life === undefined || p.life > 0);
        }, 2000);
    }
    
    /**
     * Animation loop
     */
    animate() {
        this.updateParticles();
        this.renderParticles();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    /**
     * Stop particle system
     */
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
    
    /**
     * Update particle count
     */
    setParticleCount(count) {
        this.options.particleCount = count;
        this.createParticles();
    }
    
    /**
     * Toggle interaction
     */
    toggleInteraction(enable) {
        this.options.enableInteraction = enable;
    }
}

/**
 * Matrix Rain Effect (inspired by The Matrix)
 */
class ScholarixMatrixRain {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.ctx = null;
        this.columns = [];
        this.fontSize = 14;
        this.chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
        
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.setupColumns();
        this.animate();
    }
    
    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'scholarix-matrix-canvas';
        this.canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.1;
        `;
        
        this.ctx = this.canvas.getContext('2d');
        this.container.appendChild(this.canvas);
        this.resizeCanvas();
        
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    resizeCanvas() {
        this.canvas.width = this.container.offsetWidth;
        this.canvas.height = this.container.offsetHeight;
        this.setupColumns();
    }
    
    setupColumns() {
        const columnCount = Math.floor(this.canvas.width / this.fontSize);
        this.columns = [];
        
        for (let i = 0; i < columnCount; i++) {
            this.columns[i] = this.canvas.height;
        }
    }
    
    animate() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#00E5FF';
        this.ctx.font = `${this.fontSize}px monospace`;
        
        for (let i = 0; i < this.columns.length; i++) {
            const char = this.chars[Math.floor(Math.random() * this.chars.length)];
            this.ctx.fillText(char, i * this.fontSize, this.columns[i]);
            
            if (this.columns[i] * this.fontSize > this.canvas.height && Math.random() > 0.975) {
                this.columns[i] = 0;
            }
            
            this.columns[i] += this.fontSize;
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize particle system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main particle system
    const particleSystem = new ScholarixParticles({
        particleCount: 80,
        animationSpeed: 0.5,
        enableInteraction: true,
        particleTypes: ['dot', 'glow']
    });
    
    // Initialize matrix rain on hero sections
    const heroSections = document.querySelectorAll('.scholarix-hero');
    heroSections.forEach(section => {
        new ScholarixMatrixRain(section);
    });
    
    // Store reference globally for other scripts
    window.ScholarixParticles = particleSystem;
});

// Export classes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ScholarixParticles, ScholarixMatrixRain };
}
