/** @odoo-module **/

import { QRCodeField } from "@account_payment_final/js/fields/qr_code_field";
import { PaymentApprovalWidget } from "@account_payment_final/js/components/payment_approval_widget";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { makeFakeModel } from "@web/../tests/helpers/mock_model";
import { patchWithCleanup } from "@web/../tests/helpers/utils";

QUnit.module("Account Payment Final", {}, function () {
    QUnit.module("QR Code Field Tests", {
        beforeEach() {
            this.serverData = {
                models: {
                    "account.payment": {
                        fields: {
                            id: { type: "integer" },
                            name: { type: "char" },
                            state: { type: "selection" },
                            qr_code_data: { type: "text" }
},
                        records: [
                            {
                                id: 1,
                                name: "PAY/001",
                                state: "approve",
                                qr_code_data: "test-qr-data";
}
]
}
}
};
        }
});

    QUnit.test("QR Code Field renders correctly", async function (assert) {
        assert.expect(2);

        const env = await makeTestEnv({
            serverData: this.serverData,
            mockRPC(route, args) {
                if (args.method === "generate_qr_code") {
                    return {
                        success: true,
                        qr_code: "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";
};
                }
            }
});

        const model = makeFakeModel(env, "account.payment", this.serverData.models["account.payment"]);
        const record = model.get(1);

        const target = document.createElement("div");
        const component = new QRCodeField(null, {
            record: record,
            name: "qr_code_data",
            readonly: false;
});

        await component.mount(target);

        assert.ok(target.querySelector(".o_qr_code_field"), "QR Code field should be rendered");
        assert.ok(target.querySelector(".o_qr_code_container"), "QR Code container should be present");

        component.destroy();
    });

    QUnit.test("QR Code download functionality", async function (assert) {
        assert.expect(1);

        // Mock document.createElement to capture download action
        const originalCreateElement = document.createElement;
        let downloadTriggered = false;

        patchWithCleanup(document, {
            createElement(tagName) {
                const element = originalCreateElement.call(this, tagName);
                if (tagName === "a") {
                    element.click = () => {
                        downloadTriggered = true;
                    };
                }
                return element;
            }
});

        const env = await makeTestEnv({
            serverData: this.serverData,
            mockRPC(route, args) {
                if (args.method === "generate_qr_code") {
                    return {
                        success: true,
                        qr_code: "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";
};
                }
            }
});

        const model = makeFakeModel(env, "account.payment", this.serverData.models["account.payment"]);
        const record = model.get(1);

        const target = document.createElement("div");
        const component = new QRCodeField(null, {
            record: record,
            name: "qr_code_data",
            readonly: false;
});

        await component.mount(target);
        
        // Wait for QR code to load
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Trigger download
        component.onDownloadQR();

        assert.ok(downloadTriggered, "Download should be triggered");

        component.destroy();
    });

    QUnit.module("Payment Approval Widget Tests", {
        beforeEach() {
            this.serverData = {
                models: {
                    "account.payment": {
                        fields: {
                            id: { type: "integer" },
                            name: { type: "char" },
                            state: { type: "selection" }
},
                        records: [
                            {
                                id: 1,
                                name: "PAY/001",
                                state: "review";
}
]
}
}
};
        }
});

    QUnit.test("Payment Approval Widget renders correctly", async function (assert) {
        assert.expect(3);

        const env = await makeTestEnv({
            serverData: this.serverData,
            mockRPC(route, args) {
                if (args.method === "get_approval_workflow_data") {
                    return {
                        stages: [
                            {
                                id: 1,
                                name: "Review",
                                icon: "fa-search",
                                is_current: true,
                                is_completed: false;
},
                            {
                                id: 2,
                                name: "Approve",
                                icon: "fa-check",
                                is_current: false,
                                is_completed: false;
}
],
                        current_stage: "review",
                        can_approve: true,
                        can_reject: true;
};
                }
            }
});

        const model = makeFakeModel(env, "account.payment", this.serverData.models["account.payment"]);
        const record = model.get(1);

        const target = document.createElement("div");
        const component = new PaymentApprovalWidget(null, {
            record: record,
            readonly: false,
            update: () => {}
});

        await component.mount(target);

        assert.ok(target.querySelector(".o_payment_approval_widget"), "Approval widget should be rendered");
        assert.ok(target.querySelector(".o_approval_stages"), "Approval stages should be present");
        assert.ok(target.querySelector(".o_approval_actions"), "Approval actions should be present");

        component.destroy();
    });

    QUnit.test("Approval action calls correct method", async function (assert) {
        assert.expect(1);

        let approveMethodCalled = false;

        const env = await makeTestEnv({
            serverData: this.serverData,
            mockRPC(route, args) {
                if (args.method === "get_approval_workflow_data") {
                    return {
                        stages: [],
                        current_stage: "review",
                        can_approve: true,
                        can_reject: false;
};
                }
                if (args.method === "approve_payment") {
                    approveMethodCalled = true;
                    return { success: true, message: "Payment approved" };
                }
            }
});

        const model = makeFakeModel(env, "account.payment", this.serverData.models["account.payment"]);
        const record = model.get(1);

        const target = document.createElement("div");
        const component = new PaymentApprovalWidget(null, {
            record: record,
            readonly: false,
            update: () => {}
});

        await component.mount(target);
        
        // Trigger approval
        await component.onApprove();

        assert.ok(approveMethodCalled, "Approve method should be called");

        component.destroy();
    });
});

