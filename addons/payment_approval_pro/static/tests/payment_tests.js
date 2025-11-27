/** @odoo-module **/

import { getFixture, mount } from "@web/../tests/helpers/utils";
import { PaymentWidget } from "@payment_approval_pro/js/payment_widget";
import { QRVerificationWidget } from "@payment_approval_pro/js/qr_verification";
import { PaymentApprovalDashboard } from "@payment_approval_pro/js/dashboard";

QUnit.module("Payment Approval Pro", (hooks) => {
    let target;

    hooks.beforeEach(() => {
        target = getFixture();
    });

    QUnit.module("PaymentWidget", () => {
        QUnit.test("renders payment widget correctly", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {
                        name: "VOUCHER/2024/001",
                        amount: 1000.00,
                        state: "draft",
                        payment_date: "2024-01-15",
                        reference: "Test Payment"
                    }
                },
                readonly: false
            };

            await mount(PaymentWidget, target, { props });

            assert.containsOnce(target, ".o_payment_widget");
            assert.containsOnce(target, ".payment-widget-header");
            assert.containsOnce(target, ".payment-widget-content");
            assert.strictEqual(
                target.querySelector(".payment-widget-header h4").textContent.trim(),
                "Payment Information"
            );
        });

        QUnit.test("shows correct status badge", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {
                        name: "VOUCHER/2024/001",
                        state: "approve"
                    }
                },
                readonly: true
            };

            await mount(PaymentWidget, target, { props });

            const badge = target.querySelector(".badge");
            assert.ok(badge, "Status badge should be present");
            assert.ok(badge.classList.contains("badge-approve"), "Should have approve badge class");
        });

        QUnit.test("workflow actions appear for non-readonly widget", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {
                        name: "VOUCHER/2024/001",
                        state: "draft",
                        is_creator: true
                    }
                },
                readonly: false
            };

            await mount(PaymentWidget, target, { props });

            assert.containsOnce(target, ".workflow-actions");
        });

        QUnit.test("workflow actions hidden for readonly widget", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {
                        name: "VOUCHER/2024/001",
                        state: "draft"
                    }
                },
                readonly: true
            };

            await mount(PaymentWidget, target, { props });

            assert.containsNone(target, ".workflow-actions");
        });
    });

    QUnit.module("QRVerificationWidget", () => {
        QUnit.test("renders QR widget correctly", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {
                        qr_code: "base64encodeddata"
                    }
                },
                readonly: false
            };

            await mount(QRVerificationWidget, target, { props });

            assert.containsOnce(target, ".o_qr_verification_widget");
            assert.containsOnce(target, ".qr-header");
            assert.strictEqual(
                target.querySelector(".qr-title").textContent.trim(),
                "QR Code Verification"
            );
        });

        QUnit.test("QR content hidden by default", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {}
                },
                readonly: false
            };

            await mount(QRVerificationWidget, target, { props });

            assert.containsNone(target, ".qr-content");
        });

        QUnit.test("toggle QR code display", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {}
                },
                readonly: false
            };

            const widget = await mount(QRVerificationWidget, target, { props });
            const toggleBtn = target.querySelector(".qr-toggle");

            // Initially hidden
            assert.containsNone(target, ".qr-content");

            // Click to show
            await toggleBtn.click();
            assert.containsOnce(target, ".qr-content");

            // Click to hide
            await toggleBtn.click();
            assert.containsNone(target, ".qr-content");
        });
    });

    QUnit.module("PaymentApprovalDashboard", () => {
        QUnit.test("renders dashboard correctly", async (assert) => {
            await mount(PaymentApprovalDashboard, target, {});

            assert.containsOnce(target, ".o_payment_approval_dashboard");
            assert.containsOnce(target, ".dashboard-header");
            assert.strictEqual(
                target.querySelector(".dashboard-header h1").textContent.trim(),
                "Payment Approval Dashboard"
            );
        });

        QUnit.test("shows loading state initially", async (assert) => {
            await mount(PaymentApprovalDashboard, target, {});

            assert.containsOnce(target, ".dashboard-loading");
            assert.containsOnce(target, ".spinner");
            assert.strictEqual(
                target.querySelector(".loading-text").textContent.trim(),
                "Loading dashboard data..."
            );
        });

        QUnit.test("date range buttons work correctly", async (assert) => {
            const dashboard = await mount(PaymentApprovalDashboard, target, {});
            const dateButtons = target.querySelectorAll(".date-range-buttons .btn");

            assert.strictEqual(dateButtons.length, 4, "Should have 4 date range buttons");

            // Check default selection (month)
            const monthBtn = Array.from(dateButtons).find(btn => 
                btn.textContent.trim().toLowerCase() === 'month'
            );
            assert.ok(monthBtn.classList.contains("btn-primary"), "Month button should be selected by default");
        });

        QUnit.test("refresh button works", async (assert) => {
            await mount(PaymentApprovalDashboard, target, {});
            const refreshBtn = target.querySelector(".btn-refresh");

            assert.ok(refreshBtn, "Refresh button should be present");
            assert.strictEqual(
                refreshBtn.textContent.trim(),
                "Refresh"
            );
        });
    });

    QUnit.module("Integration Tests", () => {
        QUnit.test("currency formatting works correctly", async (assert) => {
            const props = {
                record: {
                    resId: 1,
                    data: {
                        name: "VOUCHER/2024/001",
                        amount: 1234.56,
                        state: "draft"
                    }
                },
                readonly: false
            };

            const widget = await mount(PaymentWidget, target, { props });
            const amountElement = target.querySelector(".payment-summary .value");

            assert.ok(amountElement.textContent.includes("$1,234.56"), 
                     "Amount should be formatted as currency");
        });

        QUnit.test("status badge classes are correct", async (assert) => {
            const statuses = [
                { state: "draft", class: "badge-draft" },
                { state: "review", class: "badge-review" },
                { state: "approve", class: "badge-approve" },
                { state: "authorize", class: "badge-authorize" },
                { state: "paid", class: "badge-paid" },
                { state: "rejected", class: "badge-rejected" }
            ];

            for (const status of statuses) {
                const props = {
                    record: {
                        resId: 1,
                        data: {
                            name: "VOUCHER/2024/001",
                            state: status.state
                        }
                    },
                    readonly: false
                };

                await mount(PaymentWidget, target, { props });
                const badge = target.querySelector(".badge");
                
                assert.ok(badge.classList.contains(status.class), 
                         `Badge should have ${status.class} class for ${status.state} state`);
                
                // Clean up for next iteration
                target.innerHTML = "";
            }
        });
    });
});
