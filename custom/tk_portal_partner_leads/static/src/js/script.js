/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

$(document).ready(async function () {
  /*** Get state using country ***/
    $("#country").on("change", function () {
        let countryId = $("#country").val();
        jsonrpc("/get-state-data", { country_id: countryId }).then((result) => {
            if (result.status) {
                let text;
                result.state_names.map((e, i) => {
                    text += `<option value="${result.state_ids[i]}-${e}">${e}</option>`;
               });
               $("#state").empty().append(text);
            }
        });
    })
});



