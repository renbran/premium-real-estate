/** @odoo-module **/

/**
 * Emergency Odoo.define Global Fix
 * Include this script FIRST if you encounter "odoo.define is not a function" errors
 * 
 * This creates a global compatibility layer for legacy Odoo modules
 */

console.log("🚑 Emergency Odoo.define Global Fix Loading...");

// Ensure window.odoo exists
/** @odoo-module **/
// Emergency Odoo.define Global Fix for CloudPepper/Odoo 17
// Loads FIRST to patch asset loading issues and legacy JS errors

console.log("🚑 Emergency Odoo.define Global Fix Loading...");

(() => {
    'use strict';
    if (typeof window !== 'undefined') {
        window.odoo = window.odoo || {};
        // Patch odoo.define if missing or not a function
        if (typeof window.odoo.define !== 'function') {
            window.odoo.define = (name, dependencies, callback) => {
                console.warn(`🚨 Emergency Fix: Legacy odoo.define() call for "${name}"`);
                // Provide a dummy require function
                const requireShim = moduleName => {
                    console.warn(`🚨 Emergency Fix: require('${moduleName}') called - returning empty object`);
                    return {};
                };
                if (typeof callback === 'function') {
                    return callback(requireShim);
                }
                return {};
            };
            console.log("✅ Emergency odoo.define() shim activated");
        }
        // Patch loader
        window.odoo.loader = window.odoo.loader || {
            bus: {
                addEventListener: (event, callback) => {
                    console.log(`🚨 Emergency Fix: loader.bus.addEventListener('${event}') shimmed`);
                }
            }
        };
        // Global error handler for odoo.define errors
        window.addEventListener('error', event => {
            if (event.message && event.message.includes('odoo.define is not a function')) {
                console.error('🚨 Emergency Fix: Caught odoo.define error:', event.message);
                event.preventDefault();
                return true;
            }
        });
    }
    console.log("🚑 Emergency Odoo.define Global Fix Ready!");
})();
// Global error handler specifically for odoo.define errors
window.addEventListener('error', function(event) {
    if (event.message && event.message.includes('odoo.define is not a function')) {
        console.error('🚨 Emergency Fix: Caught odoo.define error:', event.message);
        event.preventDefault();
        return true;
    }
});

console.log("🚑 Emergency Odoo.define Global Fix Ready!");
