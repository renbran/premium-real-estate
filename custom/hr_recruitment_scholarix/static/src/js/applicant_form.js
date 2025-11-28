/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

export class HrApplicantFormController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    /**
     * Override to show notification when contract email is sent
     */
    async executeButtonAction(name, record) {
        const result = await super.executeButtonAction(name, record);
        
        if (name === "action_send_contract_email") {
            this.notification.add(
                "Training period offer email composer opened. Review and send the professional SCHOLARIX-branded email to the candidate.",
                {
                    title: "Contract Email Ready",
                    type: "info",
                    sticky: false,
                }
            );
        } else if (name === "action_preview_contract_email") {
            this.notification.add(
                "Email preview opened in a new window. Check the responsive design and SCHOLARIX branding.",
                {
                    title: "Email Preview",
                    type: "info",
                    sticky: false,
                }
            );
        }
        
        return result;
    }
}

registry.category("views").add("hr_applicant_form", {
    ...registry.category("views").get("form"),
    Controller: HrApplicantFormController,
});