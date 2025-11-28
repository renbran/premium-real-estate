// White Label Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Apply white label branding to frontend/website
    applyFrontendBranding();
});

async function applyFrontendBranding() {
    try {
        // Get white label settings
        const settings = await getWhiteLabelSettings();
        
        if (settings && settings.replace_odoo_branding) {
            // Replace page title
            document.title = document.title.replace(/Odoo/g, settings.white_label_name);
            
            // Replace logos
            if (settings.custom_logo_url) {
                replaceFrontendLogos(settings.custom_logo_url);
            }
            
            // Replace favicon
            if (settings.custom_favicon_url) {
                replaceFavicon(settings.custom_favicon_url);
            }
            
            // Replace footer
            if (settings.custom_footer_text) {
                replaceFrontendFooter(settings.custom_footer_text);
            }
            
            // Hide Odoo branding elements
            hideOdooBranding();
        }
    } catch (error) {
        console.warn('Could not apply frontend white label branding:', error);
    }
}

async function getWhiteLabelSettings() {
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
        return result.result;
    } catch (error) {
        console.warn('Could not fetch white label settings:', error);
        return null;
    }
}

function replaceFrontendLogos(logoUrl) {
    const logos = document.querySelectorAll('img[src*="logo"], .navbar-brand img, .website_brand img');
    logos.forEach(logo => {
        if (logo.src.includes('odoo') || logo.parentElement.classList.contains('navbar-brand')) {
            logo.src = logoUrl;
            logo.classList.add('o_white_label_login_logo');
        }
    });
}

function replaceFavicon(faviconUrl) {
    let favicon = document.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
    if (!favicon) {
        favicon = document.createElement('link');
        favicon.rel = 'icon';
        document.head.appendChild(favicon);
    }
    favicon.href = faviconUrl;
}

function replaceFrontendFooter(footerText) {
    const footers = document.querySelectorAll('.o_footer, .oe_login_footer, .website_footer');
    footers.forEach(footer => {
        footer.innerHTML = `<div class="o_white_label_website_footer"><p>${footerText}</p></div>`;
    });
}

function hideOdooBranding() {
    // Hide powered by Odoo elements
    const odooElements = document.querySelectorAll(
        '.powered_by_odoo, .oe_login_footer, [href*="odoo.com"], .database_list'
    );
    odooElements.forEach(element => {
        element.style.display = 'none';
    });
    
    // Hide Odoo text nodes
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    let node;
    while (node = walker.nextNode()) {
        if (node.nodeValue && node.nodeValue.includes('Odoo')) {
            // Replace Odoo text in text nodes
            node.nodeValue = node.nodeValue.replace(/Powered by Odoo/gi, '');
            node.nodeValue = node.nodeValue.replace(/Odoo/g, '');
        }
    }
}
