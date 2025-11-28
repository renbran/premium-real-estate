/** @odoo-module **/

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { _t } from "@web/core/l10n/translation";

/**
 * QR Code Field Widget
 * Modern implementation for displaying payment QR codes
 */
export class QRCodeField extends Component {
  static template = "account_payment_final.QRCodeField";
  static props = {
    ...standardFieldProps,
    readonly: { type: Boolean, optional: true },
  };

  setup() {
    this.orm = useService("orm");
    this.http = useService("http");
    this.notification = useService("notification");

    this.state = useState({
      qrCode: null,
      isLoading: false,
      error: null,
    });

    onWillStart(async () => {
      await this.loadQRCode();
    });

    onWillUpdateProps(async (nextProps) => {
      if (nextProps.record.data.id !== this.props.record.data.id) {
        await this.loadQRCode();
      }
    });
  }

  /**
   * Load QR code from backend
   */
  async loadQRCode() {
    if (!this.props.record.resId || this.props.record.data.state === "draft") {
      this.state.qrCode = null;
      return;
    }

    this.state.isLoading = true;
    this.state.error = null;

    try {
      const result = await this.orm.call(
        "account.payment",
        "get_qr_code_data",
        [this.props.record.resId]
      );

      if (result && result.qr_code) {
        this.state.qrCode = `data:image/png;base64,${result.qr_code}`;
      } else {
        this.state.qrCode = null;
      }
    } catch (error) {
      console.error("Error loading QR code:", error);
      this.state.error = _t("Failed to load QR code");
      this.state.qrCode = null;
    } finally {
      this.state.isLoading = false;
    }
  }

  /**
   * Download QR code as image
   */
  onDownload() {
    if (!this.state.qrCode) return;

    try {
      const link = document.createElement("a");
      link.href = this.state.qrCode;
      link.download = `payment_qr_${this.props.record.data.name || "code"}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      this.notification.add(_t("QR code downloaded successfully"), {
        type: "success",
      });
    } catch (error) {
      this.notification.add(_t("Failed to download QR code"), {
        type: "danger",
      });
    }
  }

  /**
   * Open verification URL
   */
  onVerify() {
    if (!this.props.record.resId) return;

    const baseUrl = window.location.origin;
    const verifyUrl = `${baseUrl}/payment/verify/${this.props.record.resId}`;
    window.open(verifyUrl, "_blank");
  }

  /**
   * Print QR code
   */
  onPrint() {
    if (!this.state.qrCode) return;

    const printWindow = window.open("", "_blank");
    const paymentName = this.props.record.data.name || "Payment";
    const paymentAmount = this.props.record.data.amount || "";

    printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Payment QR Code - ${paymentName}</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 20px; 
                    }
                    .qr-container { 
                        border: 2px solid #722f37; 
                        padding: 20px; 
                        border-radius: 8px; 
                        display: inline-block; 
                    }
                    .payment-info { 
                        margin-bottom: 20px; 
                        color: #722f37; 
                    }
                    img { 
                        max-width: 300px; 
                        height: auto; 
                    }
                </style>
            </head>
            <body>
                <div class="qr-container">
                    <div class="payment-info">
                        <h2>OSUS Properties</h2>
                        <h3>Payment Verification</h3>
                        <p><strong>Reference:</strong> ${paymentName}</p>
                        ${
                          paymentAmount
                            ? `<p><strong>Amount:</strong> ${paymentAmount}</p>`
                            : ""
                        }
                    </div>
                    <img src="${this.state.qrCode}" alt="Payment QR Code" />
                    <p style="margin-top: 15px; font-size: 12px; color: #666;">
                        Scan this QR code to verify payment details
                    </p>
                </div>
            </body>
            </html>
        `);

    printWindow.document.close();
    printWindow.print();
  }
}

// Register the field widget
registry.category("fields").add("qr_code_field", QRCodeField);
