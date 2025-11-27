/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class QRCodeWidgetEnhanced extends Component {
    static template = "account_payment_approval.QRCodeWidget";
    static props = { ...standardFieldProps };

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            qrCode: null,
            verificationUrl: null,
            loading: false;
});

        onMounted(() => {
            this.loadQRData();
        });
    }

    loadQRData() {
        const record = this.props.record;
        this.state.qrCode = record.data.qr_code;
        this.state.verificationUrl = record.data.verification_url;
    }

    async copyUrl() {
        if (!this.state.verificationUrl) {
            this.notification.add(_t("No URL to copy"), { type: "warning" });
            return;
        }

        try {
            await navigator.clipboard.writeText(this.state.verificationUrl);
            this.notification.add(_t("URL copied to clipboard"), { type: "success" });
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement("textarea");
            textArea.value = this.state.verificationUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);

            this.notification.add(_t("URL copied to clipboard"), { type: "success" });
        }
    }

    openVerificationUrl() {
        if (this.state.verificationUrl) {
            window.open(this.state.verificationUrl, "_blank");
        }
    }
}

registry.category("fields").add("qr_code_widget_enhanced", QRCodeWidgetEnhanced);

