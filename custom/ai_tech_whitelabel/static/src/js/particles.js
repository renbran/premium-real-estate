/** @odoo-module **/
// AI Tech Theme - Particle Effects
// Animated background particles for login and dashboard
// ==========================================

class ParticleSystem {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            particleCount: options.particleCount || 50,
            particleColor: options.particleColor || "#0ea5e9",
            particleSize: options.particleSize || 3,
            particleSpeed: options.particleSpeed || 1,
            connectionDistance: options.connectionDistance || 150,
            enableConnections: options.enableConnections !== false,
            ...options,
        };
        
        this.particles = [];
        this.animationId = null;
        this.canvas = null;
        this.ctx = null;
        
        this.init();
    }
    
    init() {
        try {
            if (!this.container) {
                console.warn("AI Theme: Particle container not found");
                return;
            }
            
            // Create canvas
            this.canvas = document.createElement("canvas");
            this.canvas.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 0;
            `;
            
            this.container.appendChild(this.canvas);
            this.ctx = this.canvas.getContext("2d");
            
            if (!this.ctx) {
                console.error("AI Theme: Failed to get canvas context");
                return;
            }
            
            // Set canvas size
            this.resize();
            
            // Create particles
            this.createParticles();
            
            // Start animation
            this.animate();
            
            // Handle resize
            window.addEventListener("resize", () => this.resize());
        } catch (error) {
            console.error("AI Theme: Particle system initialization failed", error);
        }
    }
    
    resize() {
        this.canvas.width = this.container.offsetWidth;
        this.canvas.height = this.container.offsetHeight;
    }
    
    createParticles() {
        this.particles = [];
        
        for (let i = 0; i < this.options.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.options.particleSpeed,
                vy: (Math.random() - 0.5) * this.options.particleSpeed,
                size: Math.random() * this.options.particleSize + 1,
            });
        }
    }
    
    updateParticles() {
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
        });
    }
    
    drawParticles() {
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = this.options.particleColor;
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = this.options.particleColor;
            this.ctx.fill();
        });
    }
    
    drawConnections() {
        if (!this.options.enableConnections) return;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.options.connectionDistance) {
                    const opacity = 1 - (distance / this.options.connectionDistance);
                    
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.strokeStyle = this.hexToRgba(
                        this.options.particleColor,
                        opacity * 0.3
                    );
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                }
            }
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.updateParticles();
        this.drawConnections();
        this.drawParticles();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    hexToRgba(hex, alpha) {
        hex = hex.replace("#", "");
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
        
        window.removeEventListener("resize", () => this.resize());
    }
}

/**
 * Initialize particles on login page
 */
function initLoginParticles() {
    try {
        const loginContainer = document.querySelector(".o_login_container");
        
        if (loginContainer && document.body) {
            // Check if particles are enabled
            const particlesEnabled = document.body.classList.contains("ai-particles-enabled");
            
            if (particlesEnabled) {
                new ParticleSystem(loginContainer, {
                    particleCount: 80,
                    particleColor: "#0ea5e9",
                    particleSize: 2,
                    particleSpeed: 0.5,
                    connectionDistance: 120,
                    enableConnections: true,
                });
            }
        }
    } catch (error) {
        console.error("AI Theme: Failed to initialize login particles", error);
    }
}

/**
 * Initialize particles on dashboard
 */
function initDashboardParticles() {
    try {
        const dashboards = document.querySelectorAll(".o_dashboard, .o_kanban_view");
        
        dashboards.forEach(dashboard => {
            if (!dashboard) return;
            
            const particlesEnabled = dashboard.dataset.aiParticles === "true";
            
            if (particlesEnabled) {
                new ParticleSystem(dashboard, {
                    particleCount: 30,
                    particleColor: "#8b5cf6",
                    particleSize: 2,
                    particleSpeed: 0.3,
                    connectionDistance: 100,
                    enableConnections: false,
                });
            }
        });
    } catch (error) {
        console.error("AI Theme: Failed to initialize dashboard particles", error);
    }
}

// Auto-initialize based on page
function initParticles() {
    if (document.body && document.documentElement) {
        initLoginParticles();
        initDashboardParticles();
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initParticles);
} else {
    // Delay initialization to ensure DOM is fully ready
    setTimeout(initParticles, 100);
}

// Export for manual initialization
export { ParticleSystem, initLoginParticles, initDashboardParticles };
