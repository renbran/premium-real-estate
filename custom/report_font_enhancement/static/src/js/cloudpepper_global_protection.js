/** @odoo-module **/

/**
 * Global MutationObserver Protection
 * Prevents infinite recursion in setAttribute calls across ALL modules
 */
console.log("🛡️ CloudPepper Global Protection: Starting");

// Store original MutationObserver
const OriginalMutationObserver = window.MutationObserver;

// Create protected wrapper
class SafeMutationObserver {
    constructor(callback) {
        this.isProcessing = false;
        this.originalCallback = callback;
        this.observer = null;
        
        // Wrap callback with protection
        this.protectedCallback = (mutations, observer) => {
            // Prevent infinite recursion globally
            if (this.isProcessing) {
                return;
            }
            
            this.isProcessing = true;
            
            try {
                // Call original callback with a delay to prevent stack overflow
                setTimeout(() => {
                    try {
                        this.originalCallback(mutations, observer);
                    } catch (error) {
                        console.error("Protected MutationObserver callback error:", error);
                    } finally {
                        // Always reset processing flag
                        this.isProcessing = false;
                    }
                }, 10);
            } catch (error) {
                console.error("Protected MutationObserver setup error:", error);
                this.isProcessing = false;
            }
        };
        
        this.observer = new OriginalMutationObserver(this.protectedCallback);
        console.log("🛡️ SafeMutationObserver created");
    }
    
    observe(...args) {
        if (this.observer) {
            return this.observer.observe(...args);
        }
    }
    
    disconnect() {
        if (this.observer) {
            this.isProcessing = false; // Reset flag on disconnect
            return this.observer.disconnect();
        }
    }
    
    takeRecords() {
        if (this.observer) {
            return this.observer.takeRecords();
        }
        return [];
    }
}

// Protect setAttribute globally
const originalSetAttribute = Element.prototype.setAttribute;
let setAttributeCallCount = 0;
const MAX_SET_ATTRIBUTE_CALLS = 1000; // Prevent infinite loops

Element.prototype.setAttribute = function(name, value) {
    setAttributeCallCount++;
    
    // Prevent infinite recursion in setAttribute
    if (setAttributeCallCount > MAX_SET_ATTRIBUTE_CALLS) {
        console.error("🚨 setAttribute recursion limit reached, blocking call", {
            element: this,
            attribute: name,
            value: value,
            stack: new Error().stack
        });
        return;
    }
    
    try {
        const result = originalSetAttribute.call(this, name, value);
        
        // Reset counter after successful calls
        setTimeout(() => {
            setAttributeCallCount = Math.max(0, setAttributeCallCount - 1);
        }, 10);
        
        return result;
    } catch (error) {
        console.error("setAttribute error:", error);
        setAttributeCallCount = Math.max(0, setAttributeCallCount - 1);
        throw error;
    }
};

// Replace global MutationObserver
window.MutationObserver = SafeMutationObserver;

// Also protect common problematic patterns
const originalAddEventListener = Element.prototype.addEventListener;
Element.prototype.addEventListener = function(type, listener, options) {
    // Prevent duplicate event listeners that might cause recursion
    if (this._listeners && this._listeners[type] && this._listeners[type].includes(listener)) {
        console.warn("🛡️ Prevented duplicate event listener:", type);
        return;
    }
    
    if (!this._listeners) {
        this._listeners = {};
    }
    if (!this._listeners[type]) {
        this._listeners[type] = [];
    }
    this._listeners[type].push(listener);
    
    return originalAddEventListener.call(this, type, listener, options);
};

console.log("🛡️ CloudPepper Global Protection: Active");
console.log("🛡️ Protected: MutationObserver, setAttribute, addEventListener");
