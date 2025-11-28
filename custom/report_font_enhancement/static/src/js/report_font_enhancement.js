/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Report Font Enhancement Service
 * Dynamically adjusts font contrast and transparency based on background
 * IMPORTANT: This is a SERVICE, not a Component - prevents OWL lifecycle issues
 */
class ReportFontEnhancementService {
  constructor() {
    this.isInitialized = false;
    this.observer = null;
    this.isProcessing = false;
  }

  /**
   * Start the service (called by service registry)
   */
  start() {
    if (this.isInitialized) {
      console.log("Report Font Enhancement: Already initialized, skipping");
      return;
    }

    console.log("🛡️ Report Font Enhancement: Starting with global protection");

    // Add delay to ensure global protection is loaded
    setTimeout(() => {
      this.initializeEnhancements();
    }, 100);
  }

  /**
   * Initialize font enhancements for all reports
   */
  async initializeEnhancements() {
    try {
      console.log("Report Font Enhancement: Initializing...");

      // Add enhancement classes to existing reports
      this.enhanceExistingReports();

      // Setup mutation observer for dynamically loaded content
      this.setupMutationObserver();

      // Apply adaptive contrast
      this.applyAdaptiveContrast();

      // Setup event listeners
      this.setupEventListeners();

      this.isInitialized = true;
      console.log("✅ Report Font Enhancement: Successfully initialized");
    } catch (error) {
      console.error("❌ Report Font Enhancement: Initialization failed", error);
    }
  }

  /**
   * Enhance existing reports on the page
   */
  enhanceExistingReports() {
    const reportSelectors = [
      ".o_report_layout_standard",
      ".o_report_layout_boxed",
      ".o_report_layout_clean",
      ".o_content[data-report-margin-top]",
      ".invoice-report",
      ".financial-report",
    ];

    reportSelectors.forEach((selector) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach((element) => {
        this.enhanceReportElement(element);
      });
    });
  }

  /**
   * Enhance a single report element
   */
  enhanceReportElement(element) {
    if (!element || element.classList.contains("font-enhanced")) {
      return;
    }

    // Temporarily pause the observer while making changes
    const wasObserving = this.observer && this.observer.disconnect;
    if (wasObserving) {
      this.observer.disconnect();
    }

    try {
      // Add enhancement class
      element.classList.add("font-enhanced", "report-enhanced");

      // Calculate and apply optimal contrast
      this.calculateOptimalContrast(element);

      // Enhance tables within the report
      this.enhanceTablesInReport(element);

      // Apply transparency based on background
      this.applyAdaptiveTransparency(element);
    } catch (error) {
      console.error("Error enhancing report element:", error);
    } finally {
      // Restart the observer after changes are complete
      if (wasObserving && this.observer) {
        setTimeout(() => {
          this.observer.observe(document.body, {
            childList: true,
            subtree: true,
          });
        }, 50);
      }
    }
  }

  /**
   * Calculate optimal contrast for text based on background
   */
  calculateOptimalContrast(element) {
    const computedStyle = window.getComputedStyle(element);
    const backgroundColor = computedStyle.backgroundColor;

    // Convert background color to luminance
    const luminance = this.calculateLuminance(backgroundColor);

    // Set text color based on luminance
    const textColor = luminance > 0.5 ? "#212529" : "#f8f9fa";
    const shadowColor =
      luminance > 0.5 ? "rgba(255, 255, 255, 0.8)" : "rgba(0, 0, 0, 0.8)";

    // Apply calculated colors
    element.style.setProperty("--dynamic-text-color", textColor);
    element.style.setProperty("--dynamic-shadow-color", shadowColor);
    element.style.color = textColor;
    element.style.textShadow = `0 1px 2px ${shadowColor}`;
  }

  /**
   * Calculate luminance from color string
   */
  calculateLuminance(colorStr) {
    // Handle rgb/rgba values
    const rgbMatch = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!rgbMatch) {
      // Default to medium luminance if can't parse
      return 0.5;
    }

    const [, r, g, b] = rgbMatch.map(Number);

    // Normalize and calculate relative luminance
    const [rNorm, gNorm, bNorm] = [r, g, b].map((val) => {
      const normalized = val / 255;
      return normalized <= 0.03928
        ? normalized / 12.92
        : Math.pow((normalized + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * rNorm + 0.7152 * gNorm + 0.0722 * bNorm;
  }

  /**
   * Enhance tables within reports
   */
  enhanceTablesInReport(reportElement) {
    const tables = reportElement.querySelectorAll("table");

    tables.forEach((table) => {
      if (table.classList.contains("table-enhanced")) {
        return;
      }

      table.classList.add("table-enhanced", "report-table-enhanced");

      // Enhance headers
      const headers = table.querySelectorAll("th");
      headers.forEach((th) => {
        th.style.fontWeight = "600";
        th.style.textShadow = "0 1px 2px rgba(0,0,0,0.3)";
      });

      // Enhance amount columns
      const amountCells = table.querySelectorAll(
        ".amount, .monetary, .text-right"
      );
      amountCells.forEach((cell) => {
        cell.classList.add("report-amount-enhanced");
        cell.style.fontVariantNumeric = "tabular-nums";
        cell.style.fontWeight = "500";
      });
    });
  }

  /**
   * Apply adaptive transparency based on content and background
   */
  applyAdaptiveTransparency(element) {
    const hasBackgroundImage =
      window.getComputedStyle(element).backgroundImage !== "none";

    if (hasBackgroundImage) {
      // Increase opacity for better readability over images
      element.style.backgroundColor = "rgba(255, 255, 255, 0.95)";
    } else {
      // Use lighter transparency for solid backgrounds
      element.style.backgroundColor = "rgba(255, 255, 255, 0.9)";
    }
  }

  /**
   * Apply adaptive contrast to all report elements
   */
  applyAdaptiveContrast() {
    // Check system preference for dark mode
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    const prefersHighContrast = window.matchMedia(
      "(prefers-contrast: high)"
    ).matches;

    if (prefersDark) {
      document.documentElement.style.setProperty(
        "--report-text-color",
        "#f8f9fa"
      );
      document.documentElement.style.setProperty(
        "--report-background-color",
        "#212529"
      );
    }

    if (prefersHighContrast) {
      document.documentElement.style.setProperty(
        "--report-text-color",
        "#000000"
      );
      document.documentElement.style.setProperty(
        "--report-background-color",
        "#ffffff"
      );
      document.documentElement.style.setProperty(
        "--report-border-color",
        "#000000"
      );
    }
  }

  /**
   * Setup mutation observer for dynamic content
   */
  setupMutationObserver() {
    this.isProcessing = false; // Flag to prevent infinite recursion

    this.observer = new MutationObserver((mutations) => {
      // Prevent infinite recursion
      if (this.isProcessing) {
        return;
      }

      this.isProcessing = true;

      try {
        mutations.forEach((mutation) => {
          if (mutation.type === "childList") {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === Node.ELEMENT_NODE) {
                // Check if new node is a report or contains reports
                if (this.isReportElement(node)) {
                  this.enhanceReportElement(node);
                } else {
                  // Check for report elements within the new node
                  const reportElements = node.querySelectorAll?.(
                    ".o_report_layout_standard, .o_report_layout_boxed, .o_report_layout_clean"
                  );
                  reportElements?.forEach((element) => {
                    this.enhanceReportElement(element);
                  });
                }
              }
            });
          }
        });
      } catch (error) {
        console.error("Error in MutationObserver:", error);
      } finally {
        // Reset processing flag after a brief delay to allow DOM to settle
        setTimeout(() => {
          this.isProcessing = false;
        }, 10);
      }
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  /**
   * Check if element is a report element
   */
  isReportElement(element) {
    const reportClasses = [
      "o_report_layout_standard",
      "o_report_layout_boxed",
      "o_report_layout_clean",
      "invoice-report",
      "financial-report",
    ];

    return reportClasses.some((className) =>
      element.classList?.contains(className)
    );
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Listen for color scheme changes
    this.colorSchemeQuery = window.matchMedia("(prefers-color-scheme: dark)");
    this.colorSchemeHandler = () => this.applyAdaptiveContrast();
    this.colorSchemeQuery.addEventListener("change", this.colorSchemeHandler);

    // Listen for high contrast changes
    this.contrastQuery = window.matchMedia("(prefers-contrast: high)");
    this.contrastHandler = () => this.applyAdaptiveContrast();
    this.contrastQuery.addEventListener("change", this.contrastHandler);

    // Listen for print events
    this.beforePrintHandler = () => this.preparePrintMode();
    this.afterPrintHandler = () => this.restoreNormalMode();
    window.addEventListener("beforeprint", this.beforePrintHandler);
    window.addEventListener("afterprint", this.afterPrintHandler);
  }

  /**
   * Remove event listeners
   */
  removeEventListeners() {
    if (this.observer) {
      this.observer.disconnect();
    }

    if (this.colorSchemeQuery && this.colorSchemeHandler) {
      this.colorSchemeQuery.removeEventListener(
        "change",
        this.colorSchemeHandler
      );
    }

    if (this.contrastQuery && this.contrastHandler) {
      this.contrastQuery.removeEventListener("change", this.contrastHandler);
    }

    window.removeEventListener("beforeprint", this.beforePrintHandler);
    window.removeEventListener("afterprint", this.afterPrintHandler);
  }

  /**
   * Prepare for print mode
   */
  preparePrintMode() {
    document.body.classList.add("print-mode-font-enhanced");

    // Force high contrast for printing
    const reportElements = document.querySelectorAll(".font-enhanced");
    reportElements.forEach((element) => {
      element.style.color = "#000000";
      element.style.backgroundColor = "#ffffff";
      element.style.textShadow = "none";
    });
  }

  /**
   * Restore normal mode after printing
   */
  restoreNormalMode() {
    document.body.classList.remove("print-mode-font-enhanced");

    // Restore original styling
    setTimeout(() => {
      this.applyAdaptiveContrast();
      this.enhanceExistingReports();
    }, 100);
  }
}

// EMERGENCY DISABLE - COMPLETELY DISABLE THIS SERVICE TO STOP INFINITE RECURSION
// Register the service properly (not as a Component)
// IMPORTANT: Global protection should be loaded first via cloudpepper_global_protection.js
/*
registry.category("services").add("reportFontEnhancement", {
  dependencies: [],
  start(env, deps) {
    console.log("🛡️ Starting Report Font Enhancement with global protection");
    const service = new ReportFontEnhancementService();
    
    // Add extra delay to ensure global protection is active
    setTimeout(() => {
      service.start();
    }, 200);
    
    return service;
  },
});
*/

console.log(
  "⚠️ Report Font Enhancement Service: DISABLED FOR EMERGENCY CLOUDPEPPER FIX"
);

// Export for use in other modules
export { ReportFontEnhancementService };
