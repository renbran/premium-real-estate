from odoo import api, models

class PropertySaleReport(models.AbstractModel):
    """Fetch PDF report values for Property Sale"""
    _name = 'report.property_management.property_sale_report_template'

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        # Fetch the Property Sale record using the doc_ids
        sale_id = self.env['property.sale'].browse(doc_ids)
        
        # Prepare the data dictionary to be passed to the report template
        report_data = {
            'SaleName': sale_id.name,
            'SaleReference': sale_id.name,
            'CustomerName': sale_id.partner_id.name,
            'CustomerAddress': f"{sale_id.partner_id.street} {sale_id.partner_id.city}" if sale_id.partner_id.city else '',
            'CustomerAddress2': f"{sale_id.partner_id.city}, {sale_id.partner_id.state_id.name}" if sale_id.partner_id.city and sale_id.partner_id.state_id else '',
            'CustomerContact': sale_id.partner_id.phone,
            'PropertyName': sale_id.property_id.name,
            'SalePrice': sale_id.sale_price,
            'DownPayment': sale_id.down_payment,
            'RemainingBalance': sale_id.remaining_balance,
            'DLD_Fee': sale_id.dld_fee,
            'NoOfInstallments': sale_id.no_of_installments,
            'AmountPerInstallment': sale_id.amount_per_installment,
            'StartDate': sale_id.start_date,
        }

        # Fetching the installment lines (EMI, Downpayment, DLD fee) for the sale
        sale_lines = self.env['property.sale.line'].search([('property_sale_id', '=', sale_id.id)])
        
        # Organize the data to pass to the report template
        record_sort = []
        for line in sale_lines:
            record_sort.append({
                'serial_number': line.serial_number,
                'collection_date': line.collection_date,
                'capital_repayment': line.capital_repayment,
                'remaining_capital': line.remaining_capital,
                'collection_status': line.collection_status,
                'line_type': line.line_type,
            })

        # Sort the records by collection date
        record_sort = sorted(record_sort, key=lambda x: x['collection_date'])
        
        return {
            'docs': record_sort,
            'doc_ids': doc_ids,
            'data': report_data,
        }


class PropertySalesOfferReport(models.AbstractModel):
    """Report controller for Property Sales Offer from Property model"""
    _name = 'report.property_management.property_sales_offer_template'
    _description = 'Property Sales Offer Report'

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        """Generate report values for property sales offer"""
        properties = self.env['property.property'].browse(doc_ids)
        
        return {
            'docs': properties,
            'doc_ids': doc_ids,
            'data': data,
        }