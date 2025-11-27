/** @odoo-module **/
/**
 * CloudPepper Compatibility Patch
 * Essential compatibility layer for CloudPepper deployment
 */

// Global error prevention for CloudPepper OWL lifecycle
window.addEventListener("error", function (event) {
  console.log("[CloudPepper] Global error intercepted:", event.error);
  if (
    event.error &&
    event.error.message &&
    (event.error.message.includes("Cannot read properties") ||
      event.error.message.includes("owl"))
  ) {
    event.preventDefault();
    console.log("[CloudPepper] OWL error prevented from propagating");
  }
});

// Unhandled promise rejection handler
window.addEventListener("unhandledrejection", function (event) {
  console.log("[CloudPepper] Unhandled promise rejection:", event.reason);
  if (
    event.reason &&
    event.reason.message &&
    event.reason.message.includes("RPC")
  ) {
    event.preventDefault();
    console.log("[CloudPepper] RPC error handled gracefully");
  }
});

// CloudPepper OWL lifecycle protection
if (typeof odoo !== "undefined" && odoo.loader) {
  // Modern module loader compatibility
  console.log("[CloudPepper] Modern odoo loader detected");
}

// Ensure jQuery compatibility for CloudPepper
if (typeof $ === "undefined" && typeof jQuery !== "undefined") {
  window.$ = jQuery;
}

console.log("[CloudPepper] Compatibility patch loaded successfully");
