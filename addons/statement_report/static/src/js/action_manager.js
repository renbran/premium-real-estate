/** @odoo-module*/
import {registry} from "@web/core/registry";
import {download} from "@web/core/network/download";
import { BlockUI, unblockUI } from "@web/core/ui/block_ui";

//Action manager for xlsx report
registry.category('ir.actions.report handlers').add('xlsx', async (action) => {
    if (action.report_type === 'xlsx'){
        BlockUI();
        try {
            await download({
                url : '/xlsx_report',
                data : action.data,
                error : (error) => {
                    console.error('XLSX Report Error:', error);
                    // Handle error properly
                },
            });
        } catch (error) {
            console.error('Download failed:', error);
        } finally {
            unblockUI();
        }
    }
});
