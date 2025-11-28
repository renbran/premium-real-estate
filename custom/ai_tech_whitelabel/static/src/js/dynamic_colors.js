/** @odoo-module **/
// AI Tech Theme - Dynamic Color Management
// Real-time color updates and theme switching
// ==========================================

import { registry } from "@web/core/registry";

/**
 * Dynamic color manager for AI Tech theme
 * Handles real-time color updates from backend settings
 */
class DynamicColorManager {
    constructor() {
        this.root = document.documentElement;
        this.initialized = false;
    }
    
    /**
     * Initialize the color manager
     */
    async init() {
        if (this.initialized) return;
        
        // Watch for settings changes
        this.setupColorObserver();
        
        // Add color preview utilities
        this.setupColorPickers();
        
        this.initialized = true;
    }
    
    /**
     * Set up observer for color settings changes
     */
    setupColorObserver() {
        // Listen for custom theme update events
        document.addEventListener("ai_theme_updated", (event) => {
            if (event.detail) {
                this.updateColors(event.detail);
            }
        });
    }
    
    /**
     * Update CSS custom properties with new colors
     */
    updateColors(colors) {
        if (colors.primary) {
            this.setColor("--ai-primary", colors.primary);
            this.setDerivedColors("primary", colors.primary);
        }
        
        if (colors.secondary) {
            this.setColor("--ai-secondary", colors.secondary);
            this.setDerivedColors("secondary", colors.secondary);
        }
        
        if (colors.accent) {
            this.setColor("--ai-accent", colors.accent);
        }
        
        if (colors.darkBg) {
            this.setColor("--ai-dark-bg", colors.darkBg);
        }
        
        if (colors.sidebarBg) {
            this.setColor("--ai-dark-surface", colors.sidebarBg);
        }
        
        // Trigger repaint for glassmorphism effects
        this.triggerRepaint();
    }
    
    /**
     * Set a single color variable
     */
    setColor(variable, value) {
        this.root.style.setProperty(variable, value);
    }
    
    /**
     * Calculate and set derived colors (light, dark, RGB variants)
     */
    setDerivedColors(name, baseColor) {
        const rgb = this.hexToRgb(baseColor);
        
        if (rgb) {
            // Set RGB variant for alpha transparency
            this.root.style.setProperty(
                `--ai-${name}-rgb`,
                `${rgb.r}, ${rgb.g}, ${rgb.b}`
            );
            
            // Calculate lighter variant
            const lighter = this.lightenColor(baseColor, 20);
            this.root.style.setProperty(`--ai-${name}-light`, lighter);
            
            // Calculate darker variant
            const darker = this.darkenColor(baseColor, 20);
            this.root.style.setProperty(`--ai-${name}-dark`, darker);
        }
    }
    
    /**
     * Convert hex color to RGB object
     */
    hexToRgb(hex) {
        hex = hex.replace(/^#/, "");
        
        if (hex.length === 3) {
            hex = hex.split("").map(char => char + char).join("");
        }
        
        const bigint = parseInt(hex, 16);
        return {
            r: (bigint >> 16) & 255,
            g: (bigint >> 8) & 255,
            b: bigint & 255,
        };
    }
    
    /**
     * Convert RGB to hex
     */
    rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b)
            .toString(16)
            .slice(1);
    }
    
    /**
     * Lighten a hex color by percentage
     */
    lightenColor(hex, percent) {
        const rgb = this.hexToRgb(hex);
        const factor = 1 + (percent / 100);
        
        return this.rgbToHex(
            Math.min(255, Math.round(rgb.r * factor)),
            Math.min(255, Math.round(rgb.g * factor)),
            Math.min(255, Math.round(rgb.b * factor))
        );
    }
    
    /**
     * Darken a hex color by percentage
     */
    darkenColor(hex, percent) {
        const rgb = this.hexToRgb(hex);
        const factor = 1 - (percent / 100);
        
        return this.rgbToHex(
            Math.max(0, Math.round(rgb.r * factor)),
            Math.max(0, Math.round(rgb.g * factor)),
            Math.max(0, Math.round(rgb.b * factor))
        );
    }
    
    /**
     * Set up enhanced color pickers in settings
     */
    setupColorPickers() {
        // Enhance color input fields with live preview
        const colorInputs = document.querySelectorAll('input[type="color"]');
        
        colorInputs.forEach(input => {
            if (!input) return;
            
            input.addEventListener("change", (e) => {
                const fieldName = e.target.name || e.target.id;
                this.handleColorChange(fieldName, e.target.value);
            });
            
            // Add preview box next to input
            if (input.parentNode) {
                const preview = document.createElement("div");
                preview.className = "ai-color-preview";
                preview.style.cssText = `
                    display: inline-block;
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    margin-left: 8px;
                    border: 2px solid var(--ai-dark-border);
                    background: ${input.value};
                    transition: all 0.3s ease;
                `;
                
                input.parentNode.insertBefore(preview, input.nextSibling);
                
                input.addEventListener("input", (e) => {
                    if (preview && preview.style) {
                        preview.style.background = e.target.value;
                    }
                });
            }
        });
    }
    
    /**
     * Handle color change from settings
     */
    handleColorChange(fieldName, value) {
        const colorMap = {
            "ai_theme_primary_color": "primary",
            "ai_theme_secondary_color": "secondary",
            "ai_theme_accent_color": "accent",
            "ai_theme_dark_bg": "darkBg",
            "ai_theme_sidebar_bg": "sidebarBg",
        };
        
        if (colorMap[fieldName]) {
            const colors = {};
            colors[colorMap[fieldName]] = value;
            this.updateColors(colors);
        }
    }
    
    /**
     * Force browser repaint for glassmorphism effects
     */
    triggerRepaint() {
        if (document.body) {
            const currentDisplay = document.body.style.display;
            document.body.style.display = "none";
            // Trigger reflow
            void document.body.offsetHeight;
            document.body.style.display = currentDisplay || "";
        }
    }
    
    /**
     * Get current theme colors
     */
    getCurrentColors() {
        return {
            primary: this.getComputedColor("--ai-primary"),
            secondary: this.getComputedColor("--ai-secondary"),
            accent: this.getComputedColor("--ai-accent"),
            darkBg: this.getComputedColor("--ai-dark-bg"),
            sidebarBg: this.getComputedColor("--ai-dark-surface"),
        };
    }
    
    /**
     * Get computed CSS variable value
     */
    getComputedColor(variable) {
        return getComputedStyle(this.root)
            .getPropertyValue(variable)
            .trim();
    }
}

// Initialize when DOM is ready
let colorManager;

function initColorManager() {
    try {
        if (document.body && document.documentElement) {
            colorManager = new DynamicColorManager();
            colorManager.init();
        }
    } catch (error) {
        console.error("AI Theme: Failed to initialize color manager", error);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initColorManager);
} else {
    initColorManager();
}

// Export for use in other modules
export default colorManager;
