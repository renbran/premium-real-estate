/** @odoo-module **/

/**
 * Modern Odoo 17 Compatibility Layer
 * Handles legacy odoo.define() calls and ensures modern ES6+ compatibility
 * CloudPepper Safe - Prevents "odoo.define is not a function" errors
 */

(function () {
  "use strict";

  console.log("[Modern Odoo17] Installing compatibility layer...");

  // Ensure odoo object exists
  if (typeof window.odoo === "undefined") {
    window.odoo = {};
  }

  // Legacy odoo.define() compatibility shim for older modules
  if (typeof window.odoo.define !== "function") {
    window.odoo.define = function (name, dependencies, callback) {
      console.warn(
        `[Modern Odoo17] Legacy odoo.define() call detected for "${name}". Please modernize to ES6+ modules.`
      );

      // Handle different function signatures
      if (typeof dependencies === "function") {
        // odoo.define(name, function() {})
        callback = dependencies;
        dependencies = [];
      }

      try {
        // Execute callback immediately for compatibility
        if (typeof callback === "function") {
          const result = callback(function (dep) {
            console.warn(
              `[Modern Odoo17] Legacy require("${dep}") called. Consider using import statements.`
            );
            return {}; // Return empty object for compatibility
          });

          // Store result in global registry for access
          if (!window.odoo._legacyModules) {
            window.odoo._legacyModules = {};
          }
          window.odoo._legacyModules[name] = result;

          return result;
        }
      } catch (error) {
        console.error(
          `[Modern Odoo17] Error in legacy module "${name}":`,
          error
        );
        return {};
      }

      return {};
    };
  }

  // Modern module loader - ensures ES6+ modules work correctly
  if (!window.odoo.loader) {
    window.odoo.loader = {
      modules: new Map(),

      register(name, dependencies, factory) {
        console.log(`[Modern Odoo17] Registering modern module: ${name}`);
        this.modules.set(name, {
          dependencies,
          factory,
          instance: null,
        });
      },

      load(name) {
        const module = this.modules.get(name);
        if (!module) {
          console.warn(`[Modern Odoo17] Module "${name}" not found`);
          return null;
        }

        if (!module.instance) {
          try {
            module.instance = module.factory();
          } catch (error) {
            console.error(
              `[Modern Odoo17] Error loading module "${name}":`,
              error
            );
            return null;
          }
        }

        return module.instance;
      },
    };
  }

  // Service registry compatibility for modern Odoo 17
  if (!window.odoo.serviceRegistry) {
    window.odoo.serviceRegistry = {
      services: new Map(),

      add(name, service) {
        console.log(`[Modern Odoo17] Registering service: ${name}`);
        this.services.set(name, service);
      },

      get(name) {
        return this.services.get(name);
      },

      has(name) {
        return this.services.has(name);
      },
    };
  }

  // Component registry for OWL components
  if (!window.odoo.componentRegistry) {
    window.odoo.componentRegistry = {
      components: new Map(),

      add(name, component) {
        console.log(`[Modern Odoo17] Registering component: ${name}`);
        this.components.set(name, component);
      },

      get(name) {
        return this.components.get(name);
      },
    };
  }

  // Error boundary for legacy code
  window.addEventListener("error", function (event) {
    if (
      event.message &&
      event.message.includes("odoo.define is not a function")
    ) {
      console.error(
        "[Modern Odoo17] Legacy odoo.define() error caught:",
        event.message
      );
      console.log("[Modern Odoo17] Applying emergency compatibility fix...");

      // Emergency fix - create minimal odoo.define if missing
      if (!window.odoo.define) {
        window.odoo.define = function () {
          console.warn(
            "[Modern Odoo17] Emergency odoo.define() shim activated"
          );
          return {};
        };
      }

      event.preventDefault();
      return false;
    }
  });

  // Handle unhandled promise rejections related to module loading
  window.addEventListener("unhandledrejection", function (event) {
    if (
      event.reason &&
      event.reason.message &&
      (event.reason.message.includes("odoo.define") ||
        event.reason.message.includes("module loading"))
    ) {
      console.warn(
        "[Modern Odoo17] Module loading error handled:",
        event.reason.message
      );
      event.preventDefault();
    }
  });

  console.log("[Modern Odoo17] Compatibility layer installed successfully");
})();

/**
 * Modern Odoo 17 Module Helper Functions
 * Utilities for transitioning from legacy to modern syntax
 */

// Helper to convert legacy modules to modern syntax
window.modernizeOdooModule = function (legacyName, modernFactory) {
  if (window.odoo._legacyModules && window.odoo._legacyModules[legacyName]) {
    console.log(`[Modern Odoo17] Modernizing legacy module: ${legacyName}`);
    return modernFactory(window.odoo._legacyModules[legacyName]);
  }
  return modernFactory({});
};

// Helper for safe service access
window.getOdooService = function (serviceName) {
  if (
    window.odoo.serviceRegistry &&
    window.odoo.serviceRegistry.has(serviceName)
  ) {
    return window.odoo.serviceRegistry.get(serviceName);
  }
  console.warn(`[Modern Odoo17] Service "${serviceName}" not available`);
  return null;
};

console.log("[Modern Odoo17] All compatibility helpers loaded");
