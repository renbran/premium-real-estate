/** @odoo-module **/

﻿/**
 * QR Code Verification Portal Frontend JavaScript
 *
 * Handles payment verification through QR codes on public portal
 * Uses vanilla JavaScript for broader compatibility
 */

document.addEventListener("DOMContentLoaded", function () {
    const VerificationPortal = {
        // Initialize the verification portal
        init() {
            this.form = document.getElementById("verification-form");
            this.input = document.getElementById("verification-input");
            this.button = document.getElementById("verification-button");
            this.result = document.getElementById("verification-result");

            this.bindEvents();
            this.setupValidation();
        },

        // Bind event listeners
        bindEvents() {
            if (this.form) {
                this.form.addEventListener("submit", this.handleSubmit.bind(this));
            }

            if (this.input) {
                this.input.addEventListener("input", this.handleInput.bind(this));
                this.input.addEventListener("paste", this.handlePaste.bind(this));
            }

            // Auto-verify if QR code is in URL parameters
            this.autoVerifyFromURL();
        },

        // Setup input validation
        setupValidation() {
            if (!this.input) return;

            this.input.addEventListener("blur", () => {
                this.validateInput();
            });
        },

        // Handle form submission
        async handleSubmit(event) {
            event.preventDefault();

            if (!this.validateInput()) {
                return;
            }

            await this.verifyPayment();
        },

        // Handle input changes
        handleInput(event) {
            const value = event.target.value.trim();

            // Remove validation classes on input
            this.input.classList.remove("is-valid", "is-invalid");

            // Enable/disable button based on input
            if (this.button) {
                this.button.disabled = value.length === 0;
            }
        },

        // Handle paste events (for QR URLs)
        handlePaste(event) {
            setTimeout(() => {
                const value = this.input.value.trim();

                // Extract payment ID from URL if pasted
                const urlMatch = value.match(/payment_id=([a-f0-9-]+)/i);
                if (urlMatch) {
                    this.input.value = urlMatch[1];
                    this.validateInput();
                }
            }, 100);
        },

        // Validate input format
        validateInput() {
            if (!this.input) return false;

            const value = this.input.value.trim();
            const feedback = this.input.parentNode.querySelector(".o_input_feedback");

            // Reset classes
            this.input.classList.remove("is-valid", "is-invalid");

            if (value.length === 0) {
                this.showInputFeedback(feedback, "Please enter a verification code", "invalid");
                return false;
            }

            // Validate format (UUID or payment reference)
            const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
            const isReference = /^[A-Z0-9\/\-\.]+$/i.test(value) && value.length >= 3;

            if (!isUuid && !isReference) {
                this.showInputFeedback(feedback, "Invalid verification code format", "invalid");
                return false;
            }

            this.showInputFeedback(feedback, "Valid format", "valid");
            return true;
        },

        // Show input feedback
        showInputFeedback(feedbackEl, message, type) {
            if (!feedbackEl) return;

            this.input.classList.add(type === "valid" ? "is-valid" : "is-invalid");
            feedbackEl.textContent = message;
            feedbackEl.className = `o_input_feedback is-${type}`;
        },

        // Auto-verify from URL parameters
        autoVerifyFromURL() {
            const urlParams = new URLSearchParams(window.location.search);
            const paymentId = urlParams.get("payment_id");

            if (paymentId && this.input) {
                this.input.value = paymentId;
                this.validateInput();

                // Auto-verify after a short delay
                setTimeout(() => {
                    this.verifyPayment();
                }, 500);
            }
        },

        // Verify payment with backend
        async verifyPayment() {
            if (!this.input || !this.button) return;

            const verificationCode = this.input.value.trim();

            // Show loading state
            this.setLoadingState(true);
            this.hideResult();

            try {
                const response = await fetch("/payment/verify", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: JSON.stringify({
                        verification_code: verificationCode,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();
                this.showResult(result);
            } catch (error) {
                console.error("Verification failed:", error);
                this.showResult({
                    success: false,
                    message: "Network error occurred. Please try again.",
                    error: error.message,
                });
            } finally {
                this.setLoadingState(false);
            }
        },

        // Set loading state
        setLoadingState(isLoading) {
            if (!this.button) return;

            const buttonText = this.button.querySelector(".button-text");
            const buttonLoading = this.button.querySelector(".o_button_loading");

            if (isLoading) {
                this.button.disabled = true;
                if (buttonText) buttonText.style.opacity = "0";
                if (buttonLoading) buttonLoading.style.display = "block";
            } else {
                this.button.disabled = false;
                if (buttonText) buttonText.style.opacity = "1";
                if (buttonLoading) buttonLoading.style.display = "none";
            }
        },

        // Show verification result
        showResult(result) {
            if (!this.result) return;

            // Clear previous content
            this.result.className = "o_verification_result";
            this.result.innerHTML = "";
            // Determine result type
            const resultType = result.success ? "success" : "error";
            this.result.classList.add(`o_result_${resultType}`, "show");

            // Create result HTML
            const resultHTML = this.createResultHTML(result, resultType);
            this.result.innerHTML = resultHTML;

            // Scroll to result
            this.result.scrollIntoView({ behavior: "smooth", block: "nearest" });
        },

        // Create result HTML
        createResultHTML(result, type) {
            const icon = type === "success" ? "fa-check-circle" : "fa-exclamation-circle";
            const title = type === "success" ? "Payment Verified" : "Verification Failed";
            let html = `
;
                <div class="o_result_header">
;
                    <i class="fa ${icon} o_result_icon"></i>
;
                    <h3>${title}</h3>
;
                </div>
;
            `;

            if (result.message) {
                html += `<p class="o_result_message">${this.escapeHtml(result.message)}</p>`;
            }

            if (result.success && result.payment_data) {
                html += this.createPaymentDetailsHTML(result.payment_data);
            }

            return html;
        },

        // Create payment details HTML
        createPaymentDetailsHTML(paymentData) {
            let html = '<div class="o_result_details">';
            const details = [
                { label: "Payment Reference", value: paymentData.name },
                { label: "Amount", value: this.formatCurrency(paymentData.amount, paymentData.currency) },
                { label: "Partner", value: paymentData.partner_name },
                { label: "Date", value: this.formatDate(paymentData.date) },
                { label: "State", value: this.formatState(paymentData.state) },
                { label: "Journal", value: paymentData.journal_name },
            ];

            details.forEach((detail) => {
                if (detail.value) {
                    html += `
;
                        <div class="o_detail_row">
;
                            <span class="o_detail_label">${detail.label}:</span>
;
                            <span class="o_detail_value">${this.escapeHtml(detail.value)}</span>
;
                        </div>
;
                    `;
                }
            });

            html += "</div>";
            return html;
        },

        // Hide result
        hideResult() {
            if (this.result) {
                this.result.classList.remove("show");
            }
        },

        // Utility: Escape HTML
        escapeHtml(text) {
            const div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        },

        // Utility: Format currency
        formatCurrency(amount, currency) {
            try {
                return new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: currency || "USD",
                }).format(amount);
            } catch (error) {
                return `${amount} ${currency || ""}`;
            }
        },

        // Utility: Format date
        formatDate(dateString) {
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                });
            } catch (error) {
                return dateString;
            }
        },

        // Utility: Format state
        formatState(state) {
            const stateLabels = {
                draft: "Draft",
                review: "Under Review",
                approve: "Approved",
                authorize: "Authorized",
                post: "Posted",
                cancel: "Cancelled",
                reject: "Rejected",
            };

            return stateLabels[state] || state.charAt(0).toUpperCase() + state.slice(1);
        },
    };

    // Initialize the verification portal
    VerificationPortal.init();

    // Export to global scope for debugging
    window.VerificationPortal = VerificationPortal;
});
