/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class RestApiWidget extends Component {
    static template = "enhanced_rest_api.ApiWidget";
    static props = ["*"];
    
    setup() {
        this.http = useService("http");
        this.notification = useService("notification");
        
        this.state = useState({
            apiStatus: null,
            isConnecting: false
        });
    }
    
    async testApiConnection() {
        try {
            this.state.isConnecting = true;
            const response = await this.http.get("/api/v1/status");
            this.state.apiStatus = response.data;
            this.notification.add(_t("API connection successful"), { type: "success" });
        } catch (error) {
            console.error("API connection error:", error);
            this.notification.add(_t("API connection failed"), { type: "danger" });
        } finally {
            this.state.isConnecting = false;
        }
    }
}

registry.category("widgets").add("rest_api_widget", RestApiWidget);
