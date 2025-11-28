/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// White Label Branding Service
class WhiteLabelService {
    constructor(env, services) {
        this.env = env;
        this.orm = services.orm;
        this.settings = null;
    }

    async loadSettings() {
        if (!this.settings) {
            try {
                this.settings = await this.orm.call(
                    'res.company',
                    'get_white_label_settings',
                    []
                );
            } catch (error) {
                console.warn('Could not load white label settings:', error);
                this.settings = {
                    replace_odoo_branding: false,
                    white_label_name: 'Odoo'
                };
            }
        }
        return this.settings;
    }

    async applyBranding() {
        const settings = await this.loadSettings();
        
        if (settings.replace_odoo_branding) {
            // Add data attribute to body
            document.body.setAttribute('data-replace-odoo-branding', 'true');
            
            // Replace title
            document.title = document.title.replace(/Odoo/g, settings.white_label_name);
            
            // Replace logo if custom logo URL is provided
            if (settings.custom_logo_url) {
                this.replaceLogos(settings.custom_logo_url);
            }
            
            // Replace favicon if custom favicon URL is provided
            if (settings.custom_favicon_url) {
                this.replaceFavicon(settings.custom_favicon_url);
            }
            
            // Update navbar brand
            this.updateNavbarBrand(settings.white_label_name);
            
            // Hide documentation/support links
            if (settings.hide_odoo_documentation || settings.hide_odoo_support) {
                this.hideOdooLinks(settings);
            }
            
            // Replace footer
            if (settings.custom_footer_text) {
                this.replaceFooter(settings.custom_footer_text);
            }
        }
    }

    replaceLogos(logoUrl) {
        const logos = document.querySelectorAll('img[src*="logo"], .navbar-brand img');
        logos.forEach(logo => {
            if (logo.src.includes('odoo') || logo.classList.contains('o_logo')) {
                logo.src = logoUrl;
                logo.classList.add('o_white_label_logo');
            }
        });
    }

    replaceFavicon(faviconUrl) {
        let favicon = document.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
        if (!favicon) {
            favicon = document.createElement('link');
            favicon.rel = 'icon';
            document.head.appendChild(favicon);
        }
        favicon.href = faviconUrl;
    }

    updateNavbarBrand(brandName) {
        const navbarBrand = document.querySelector('.navbar-brand');
        if (navbarBrand) {
            navbarBrand.setAttribute('data-white-label-name', brandName);
            navbarBrand.textContent = brandName;
        }
    }

    hideOdooLinks(settings) {
        if (settings.hide_odoo_documentation) {
            const docLinks = document.querySelectorAll('a[href*="odoo.com/documentation"], a[data-menu="documentation"]');
            docLinks.forEach(link => link.style.display = 'none');
        }
        
        if (settings.hide_odoo_support) {
            const supportLinks = document.querySelectorAll('a[href*="odoo.com/help"], a[data-menu="support"]');
            supportLinks.forEach(link => link.style.display = 'none');
        }
    }

    replaceFooter(footerText) {
        const footers = document.querySelectorAll('.o_footer, .powered_by_odoo, .o_powered_by');
        footers.forEach(footer => {
            footer.innerHTML = `<div class="o_white_label_footer">${footerText}</div>`;
        });
    }
}

// Register the service
registry.category("services").add("whiteLabelService", {
    dependencies: ["orm"],
    start(env, services) {
        return new WhiteLabelService(env, services);
    },
});

// White Label Component to initialize branding
class WhiteLabelBranding extends Component {
    setup() {
        this.whiteLabelService = useService("whiteLabelService");
        
        onMounted(async () => {
            await this.whiteLabelService.applyBranding();
            
            // Set up mutation observer to reapply branding when DOM changes
            const observer = new MutationObserver(() => {
                this.whiteLabelService.applyBranding();
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }
}

WhiteLabelBranding.template = "white_label_branding.WhiteLabelTemplate";

// Register the component
registry.category("main_components").add("WhiteLabelBranding", {
    Component: WhiteLabelBranding,
});

// Simple template
registry.category("web.templates").add("white_label_branding.WhiteLabelTemplate", {
    template: '<div class="o_white_label_container"></div>'
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    // Quick application of branding for immediate effect
    const body = document.body;
    
    // Check if we should apply branding (basic check)
    try {
        const response = await fetch('/web/dataset/call_kw/res.company/get_white_label_settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: 'res.company',
                    method: 'get_white_label_settings',
                    args: [],
                    kwargs: {}
                }
            })
        });
        
        const result = await response.json();
        if (result.result && result.result.replace_odoo_branding) {
            body.setAttribute('data-replace-odoo-branding', 'true');
            
            // Quick title replacement
            document.title = document.title.replace(/Odoo/g, result.result.white_label_name);
        }
    } catch (error) {
        console.warn('Could not apply quick white label branding:', error);
    }
});
