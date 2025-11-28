/** @odoo-module **/
// AI Tech Theme - Theme Configuration
// Dynamic theme management and settings
// ==========================================

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class AIThemeConfig extends Component {
    setup() {
        this.orm = useService("orm");
        this.user = useService("user");
        
        // Load theme settings on initialization
        this.loadThemeSettings();
    }
    
    async loadThemeSettings() {
        try {
            const company = await this.orm.call(
                "res.company",
                "search_read",
                [[["id", "=", this.user.context.allowed_company_ids[0]]]],
                {
                    fields: [
                        "ai_theme_primary_color",
                        "ai_theme_secondary_color",
                        "ai_theme_accent_color",
                        "ai_theme_dark_bg",
                        "ai_theme_sidebar_bg",
                        "ai_theme_font_family",
                        "ai_theme_app_name",
                        "ai_theme_enable_glassmorphism",
                        "ai_theme_enable_animations",
                        "ai_theme_enable_gradients",
                    ],
                }
            );
            
            if (company && company.length > 0) {
                this.applyThemeSettings(company[0]);
            }
        } catch (error) {
            console.error("Failed to load theme settings:", error);
        }
    }
    
    applyThemeSettings(settings) {
        const root = document.documentElement;
        
        // Apply color settings
        if (settings.ai_theme_primary_color) {
            root.style.setProperty("--ai-primary", settings.ai_theme_primary_color);
            
            // Calculate RGB values for alpha variants
            const rgb = this.hexToRgb(settings.ai_theme_primary_color);
            if (rgb) {
                root.style.setProperty("--ai-primary-rgb", `${rgb.r}, ${rgb.g}, ${rgb.b}`);
            }
        }
        
        if (settings.ai_theme_secondary_color) {
            root.style.setProperty("--ai-secondary", settings.ai_theme_secondary_color);
            
            const rgb = this.hexToRgb(settings.ai_theme_secondary_color);
            if (rgb) {
                root.style.setProperty("--ai-secondary-rgb", `${rgb.r}, ${rgb.g}, ${rgb.b}`);
            }
        }
        
        if (settings.ai_theme_accent_color) {
            root.style.setProperty("--ai-accent", settings.ai_theme_accent_color);
        }
        
        if (settings.ai_theme_dark_bg) {
            root.style.setProperty("--ai-dark-bg", settings.ai_theme_dark_bg);
        }
        
        if (settings.ai_theme_sidebar_bg) {
            root.style.setProperty("--ai-dark-surface", settings.ai_theme_sidebar_bg);
        }
        
        // Apply font family
        if (settings.ai_theme_font_family) {
            root.style.setProperty("--ai-font-family", `'${settings.ai_theme_font_family}', sans-serif`);
        }
        
        // Apply app name to title
        if (settings.ai_theme_app_name) {
            document.title = settings.ai_theme_app_name;
            
            // Update brand elements
            const brandElements = document.querySelectorAll(".o_menu_brand");
            brandElements.forEach(el => {
                if (el.textContent) {
                    el.textContent = settings.ai_theme_app_name;
                }
            });
        }
        
        // Toggle feature classes
        const body = document.body;
        
        if (settings.ai_theme_enable_glassmorphism) {
            body.classList.add("ai-glassmorphism-enabled");
        } else {
            body.classList.remove("ai-glassmorphism-enabled");
        }
        
        if (settings.ai_theme_enable_animations) {
            body.classList.add("ai-animations-enabled");
        } else {
            body.classList.remove("ai-animations-enabled");
        }
        
        if (settings.ai_theme_enable_gradients) {
            body.classList.add("ai-gradients-enabled");
        } else {
            body.classList.remove("ai-gradients-enabled");
        }
    }
    
    hexToRgb(hex) {
        // Remove # if present
        hex = hex.replace(/^#/, "");
        
        // Parse hex values
        const bigint = parseInt(hex, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        
        return { r, g, b };
    }
}

// Register theme config to run on web client start
registry.category("main_components").add("AIThemeConfig", {
    Component: AIThemeConfig,
});

// Export for use in other modules
export default AIThemeConfig;
