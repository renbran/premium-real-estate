/** @odoo-module **/

/**
 * Payment Workflow Helper - CloudPepper Compatible
 * NON-MODULE VERSION to prevent import statement errors
 * Compatible with CloudPepper environment
 */

// OSUS Properties Brand Colors
const brandColors = {
  primary: "#800020",
  gold: "#FFD700",
  lightGold: "#FFF8DC",
  darkGold: "#B8860B",
  white: "#FFFFFF",
  accent: "#A0522D",

  chartColors: ["#800020", "#FFD700", "#A0522D"],

  chartBackgrounds: ["#80002020", "#FFD70020", "#A0522D20"],
};

(function () {
  "use strict";

  // Payment Workflow Helper - Global Object
  window.PaymentWorkflowHelper = {
    /**
     * Get workflow stage configuration
     */
    getStageConfig: function () {
      return {
        draft: {
          name: "Draft",
          icon: "fa-edit",
          color: "secondary",
        },
        under_review: {
          name: "Under Review",
          icon: "fa-search",
          color: "info",
        },
        for_approval: {
          name: "For Approval",
          icon: "fa-check",
          color: "warning",
        },
        for_authorization: {
          name: "For Authorization",
          icon: "fa-key",
          color: "warning",
        },
        approved: {
          name: "Approved",
          icon: "fa-check-circle",
          color: "success",
        },
        posted: {
          name: "Posted",
          icon: "fa-check-circle",
          color: "success",
        },
        cancelled: {
          name: "Cancelled",
          icon: "fa-times-circle",
          color: "danger",
        },
      };
    },

    /**
     * Get stage display information
     */
    getStageInfo: function (stage) {
      const config = this.getStageConfig();
      return (
        config[stage] || {
          name: "Unknown",
          icon: "fa-question",
          color: "secondary",
        }
      );
    },

    /**
     * Get next possible stages for a current stage
     */
    getNextStages: function (currentStage) {
      const transitions = {
        draft: ["under_review", "cancelled"],
        under_review: ["for_approval", "draft", "cancelled"],
        for_approval: ["for_authorization", "under_review", "cancelled"],
        for_authorization: ["approved", "for_approval", "cancelled"],
        approved: ["posted", "cancelled"],
        posted: [], // Final state
        cancelled: ["draft"], // Can restart
      };

      return transitions[currentStage] || [];
    },

    /**
     * Check if a stage transition is valid
     */
    isValidTransition: function (fromStage, toStage) {
      const nextStages = this.getNextStages(fromStage);
      return nextStages.includes(toStage);
    },

    /**
     * Get stage CSS class for styling
     */
    getStageClass: function (stage) {
      const info = this.getStageInfo(stage);
      return `badge badge-${info.color} payment-stage-${stage}`;
    },

    /**
     * Get stage HTML representation
     */
    getStageHTML: function (stage) {
      const info = this.getStageInfo(stage);
      return `<span class="${this.getStageClass(stage)}">
                <i class="fa ${info.icon}"></i> ${info.name}
            </span>`;
    },

    /**
     * Initialize workflow UI enhancements
     */
    initWorkflowUI: function () {
      console.log("[Payment Workflow] Initializing UI enhancements...");

      // Add workflow styling
      this.addWorkflowStyles();

      // Initialize workflow buttons
      this.initWorkflowButtons();
    },

    /**
     * Add workflow-specific CSS styles
     */
    addWorkflowStyles: function () {
      if (document.getElementById("payment-workflow-styles")) {
        return; // Already added
      }

      const style = document.createElement("style");
      style.id = "payment-workflow-styles";
      style.textContent = `
                .payment-stage-draft { background-color: #6c757d !important; }
                .payment-stage-under_review { background-color: #17a2b8 !important; }
                .payment-stage-for_approval { background-color: #ffc107 !important; color: #212529 !important; }
                .payment-stage-for_authorization { background-color: #fd7e14 !important; }
                .payment-stage-approved { background-color: #28a745 !important; }
                .payment-stage-posted { background-color: #20c997 !important; }
                .payment-stage-cancelled { background-color: #dc3545 !important; }
                
                .payment-workflow-buttons {
                    margin-top: 10px;
                    padding: 10px;
                    border-top: 1px solid #dee2e6;
                }
                
                .payment-workflow-buttons .btn {
                    margin-right: 5px;
                    margin-bottom: 5px;
                }
            `;
      document.head.appendChild(style);
    },

    /**
     * Initialize workflow transition buttons
     */
    initWorkflowButtons: function () {
      // This would be called by form views to add workflow buttons
      console.log("[Payment Workflow] Workflow buttons initialized");
    },
  };

  // Auto-initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      window.PaymentWorkflowHelper.initWorkflowUI();
    });
  } else {
    // DOM is already ready
    window.PaymentWorkflowHelper.initWorkflowUI();
  }

  console.log(
    "[Payment Workflow] CloudPepper-compatible workflow helper loaded"
  );
})();
