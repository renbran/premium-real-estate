from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
from io import BytesIO

# Only import reportlab if available
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class CommissionReportGenerator(models.Model):
    _name = 'commission.report.generator'
    _description = 'Commission Report Generator'

    def generate_commission_report(self, sale_order_id):
        """Generate enhanced commission report with complete structure and details"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            raise UserError("ReportLab library is not installed. Please install it with: pip install reportlab")
            
        sale_order = self.env['sale.order'].browse(sale_order_id)
        if not sale_order.exists():
            raise UserError("Sale order not found")
        
        logger.info(f"Generating enhanced commission report for order: {sale_order.name}")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=15*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Define colors matching template
        burgundy_color = colors.HexColor("#800020")
        light_gray = colors.HexColor("#f8f9fa")
        medium_gray = colors.HexColor("#6c757d")
        border_color = colors.HexColor("#e9ecef")
        green_color = colors.HexColor("#28a745")
        
        # Page width calculation
        page_width = A4[0] - 30*mm
        
        # Enhanced styles matching template - use Helvetica for better compatibility
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=burgundy_color,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=medium_gray,
            alignment=TA_CENTER,
            spaceAfter=16
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeaderStyle',
            parent=styles['Normal'],
            fontSize=15,
            textColor=burgundy_color,
            fontName='Helvetica-Bold',
            spaceBefore=18,
            spaceAfter=10,
            borderWidth=0,
            borderColor=burgundy_color,
            borderPadding=0
        )
        
        # Report Header
        story.append(Paragraph("Commission Report", title_style))
        story.append(Paragraph(
            f"Order: <b>{sale_order.name}</b> | Date: <b>{sale_order.date_order.strftime('%m/%d/%Y') if sale_order.date_order else 'N/A'}</b>", 
            subtitle_style
        ))
        
        # Add border under header
        header_line = Table([[""]], colWidths=[page_width])
            header_line.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, -1), 2, burgundy_color),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(header_line)
            
            # Order Information Grid (Enhanced with more details)
            info_data = [
                ["Customer:", sale_order.partner_id.name or "N/A", "Project:", getattr(sale_order, 'project_id', False) and sale_order.project_id.name or "N/A"],
                ["Unit:", getattr(sale_order, 'unit_id', False) and sale_order.unit_id.name or "N/A", "Sales Value:", f"AED {sale_order.amount_total or 0:,.2f}"],
                ["Salesperson:", sale_order.user_id.name or "N/A", "Commission Status:", self._get_status_display(getattr(sale_order, 'commission_status', 'draft'))]
            ]
            
            # Calculate column widths for info grid
            col_width = page_width / 4
            info_table = Table(info_data, colWidths=[col_width * 0.7, col_width * 1.3, col_width * 0.7, col_width * 1.3])
            
            info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 13),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 13),  # Left labels
                ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 13),  # Right labels
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333")),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#495057")),  # Left labels
                ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor("#495057")),  # Right labels
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), light_gray),
                ('GRID', (0, 0), (-1, -1), 1, border_color),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 16))
            
            # Calculate all commission amounts from actual fields
            # Get unit price from order lines (sales value)
            unit_price = 0
            if sale_order.order_line:
                unit_price = sum(line.price_unit * line.product_uom_qty for line in sale_order.order_line)
            
            base_amount = unit_price or sale_order.amount_total or 0
            
            # External Commissions
            broker_amount = getattr(sale_order, 'broker_amount', 0) or 0
            referrer_amount = getattr(sale_order, 'referrer_amount', 0) or 0
            cashback_amount = getattr(sale_order, 'cashback_amount', 0) or 0
            other_external_amount = getattr(sale_order, 'other_external_amount', 0) or 0
            
            total_external = broker_amount + referrer_amount + cashback_amount + other_external_amount
            
            # Internal Commissions  
            agent1_amount = getattr(sale_order, 'agent1_amount', 0) or 0
            agent2_amount = getattr(sale_order, 'agent2_amount', 0) or 0
            manager_amount = getattr(sale_order, 'manager_amount', 0) or 0
            director_amount = getattr(sale_order, 'director_amount', 0) or 0
            
            total_internal = agent1_amount + agent2_amount + manager_amount + director_amount
            
            # Legacy Commissions
            consultant_amount = getattr(sale_order, 'salesperson_commission', 0) or 0
            manager_legacy_amount = getattr(sale_order, 'manager_commission', 0) or 0
            second_agent_amount = getattr(sale_order, 'second_agent_commission', 0) or 0
            director_legacy_amount = getattr(sale_order, 'director_commission', 0) or 0
            
            total_legacy = consultant_amount + manager_legacy_amount + second_agent_amount + director_legacy_amount
            
            # Commission Details Section
            story.append(Paragraph("COMMISSION DETAILS", section_header_style))
            
            # Add border under section header
            section_line = Table([[""]], colWidths=[page_width])
            section_line.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, -1), 2, burgundy_color),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(section_line)
            
            # Commission table data with enhanced structure
            commission_data = [
                ['Recipient', 'Type', 'Base Amount (AED)', 'Rate (%)', 'Commission (AED)', 'Status']
            ]
            
            # Build comprehensive commission rows with proper field handling
            commission_rows = []
            
            # EXTERNAL COMMISSIONS
            # Broker
            if hasattr(sale_order, 'broker_partner_id') and sale_order.broker_partner_id and broker_amount > 0:
                commission_type = getattr(sale_order, 'broker_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'broker_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.broker_partner_id.name or "N/A"),
                    f"Broker ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{broker_amount:,.2f}",
                    "PAID"
                ])
                
            # Referrer
            if hasattr(sale_order, 'referrer_partner_id') and sale_order.referrer_partner_id and referrer_amount > 0:
                commission_type = getattr(sale_order, 'referrer_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'referrer_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.referrer_partner_id.name or "N/A"),
                    f"Referrer ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{referrer_amount:,.2f}",
                    "DRAFT"
                ])
                
            # Cashback
            if hasattr(sale_order, 'cashback_partner_id') and sale_order.cashback_partner_id and cashback_amount > 0:
                commission_type = getattr(sale_order, 'cashback_commission_type', '') or 'Cashback'
                rate = getattr(sale_order, 'cashback_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.cashback_partner_id.name or "N/A"),
                    f"Cashback ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{cashback_amount:,.2f}",
                    "PAID"
                ])
                
            # Other External
            if hasattr(sale_order, 'other_external_partner_id') and sale_order.other_external_partner_id and other_external_amount > 0:
                commission_type = getattr(sale_order, 'other_external_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'other_external_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.other_external_partner_id.name or "N/A"),
                    f"Other External ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{other_external_amount:,.2f}",
                    "PENDING"
                ])
            
            # INTERNAL COMMISSIONS
            # Agent 1
            if hasattr(sale_order, 'agent1_partner_id') and sale_order.agent1_partner_id and agent1_amount > 0:
                commission_type = getattr(sale_order, 'agent1_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'agent1_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.agent1_partner_id.name or "N/A"),
                    f"Agent 1 ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{agent1_amount:,.2f}",
                    "PENDING"
                ])
                
            # Agent 2
            if hasattr(sale_order, 'agent2_partner_id') and sale_order.agent2_partner_id and agent2_amount > 0:
                commission_type = getattr(sale_order, 'agent2_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'agent2_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.agent2_partner_id.name or "N/A"),
                    f"Agent 2 ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{agent2_amount:,.2f}",
                    "APPROVED"
                ])
                
            # Manager
            if hasattr(sale_order, 'manager_partner_id') and sale_order.manager_partner_id and manager_amount > 0:
                commission_type = getattr(sale_order, 'manager_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'manager_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.manager_partner_id.name or "N/A"),
                    f"Manager ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{manager_amount:,.2f}",
                    "APPROVED"
                ])
                
            # Director
            if hasattr(sale_order, 'director_partner_id') and sale_order.director_partner_id and director_amount > 0:
                commission_type = getattr(sale_order, 'director_commission_type', '') or 'Commission'
                rate = getattr(sale_order, 'director_rate', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.director_partner_id.name or "N/A"),
                    f"Director ({commission_type})",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{director_amount:,.2f}",
                    "APPROVED"
                ])
            
            # LEGACY COMMISSIONS
            # Consultant (Legacy)
            if hasattr(sale_order, 'consultant_id') and sale_order.consultant_id and consultant_amount > 0:
                rate = getattr(sale_order, 'consultant_comm_percentage', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.consultant_id.name or "N/A"),
                    "Consultant (Legacy)",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{consultant_amount:,.2f}",
                    "LEGACY"
                ])
                
            # Manager (Legacy)
            if hasattr(sale_order, 'manager_id') and sale_order.manager_id and manager_legacy_amount > 0:
                rate = getattr(sale_order, 'manager_comm_percentage', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.manager_id.name or "N/A"),
                    "Manager (Legacy)",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{manager_legacy_amount:,.2f}",
                    "LEGACY"
                ])
                
            # Second Agent (Legacy)
            if hasattr(sale_order, 'second_agent_id') and sale_order.second_agent_id and second_agent_amount > 0:
                rate = getattr(sale_order, 'second_agent_comm_percentage', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.second_agent_id.name or "N/A"),
                    "Second Agent (Legacy)",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{second_agent_amount:,.2f}",
                    "LEGACY"
                ])
                
            # Director (Legacy)
            if hasattr(sale_order, 'director_id') and sale_order.director_id and director_legacy_amount > 0:
                rate = getattr(sale_order, 'director_comm_percentage', 0) or 0
                commission_rows.append([
                    self._truncate_name(sale_order.director_id.name or "N/A"),
                    "Director (Legacy)",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{director_legacy_amount:,.2f}",
                    "LEGACY"
                ])
            
            # Add all commission rows
            commission_data.extend(commission_rows)
            
            # Add subtotal rows
            commission_data.extend([
                ["", "", "", "Total External Commissions:", f"{total_external:,.2f}", ""],
                ["", "", "", "Total Internal Commissions:", f"{total_internal:,.2f}", ""],
                ["", "", "", "Total Legacy Commissions:", f"{total_legacy:,.2f}", ""],
                ["", "", "", "TOTAL COMMISSION:", f"{total_external + total_internal + total_legacy:,.2f}", ""]
            ])
            
            # Create commission table
            commission_table = Table(commission_data, colWidths=[
                page_width * 0.25,   # Recipient
                page_width * 0.12,   # Type
                page_width * 0.18,   # Base Amount
                page_width * 0.18,   # Rate/Label
                page_width * 0.17,   # Commission
                page_width * 0.10    # Status
            ])
            
            num_data_rows = len(commission_rows)
            
            commission_table.setStyle(TableStyle([
                # Header row styling (matches template)
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), burgundy_color),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
                
                # Data rows styling
                ('FONT', (0, 1), (-1, num_data_rows), 'Helvetica', 12),
                ('TEXTCOLOR', (0, 1), (-1, num_data_rows), colors.black),
                ('ALIGN', (0, 1), (1, num_data_rows), 'LEFT'),
                ('ALIGN', (2, 1), (4, num_data_rows), 'RIGHT'),
                ('ALIGN', (3, 1), (3, num_data_rows), 'CENTER'),  # Rate column center
                # Status column styling - enhanced for different status types
                ('ALIGN', (5, 1), (5, num_data_rows), 'CENTER'),  # Status column center
                
                # Highlight commission amounts in green
                ('TEXTCOLOR', (4, 1), (4, num_data_rows), green_color),
                ('FONT', (4, 1), (4, num_data_rows), 'Helvetica-Bold', 12),
                
                # Alternating row backgrounds for better readability
                ('BACKGROUND', (0, 1), (-1, num_data_rows), light_gray),
                
                # Subtotal rows styling  
                ('FONT', (0, num_data_rows+1), (-1, -2), 'Helvetica-Bold', 12),
                ('TEXTCOLOR', (0, num_data_rows+1), (-1, -2), colors.black),
                ('BACKGROUND', (0, num_data_rows+1), (-1, -2), colors.HexColor("#f1f3f4")),
                ('ALIGN', (0, num_data_rows+1), (-1, -2), 'RIGHT'),
                
                # Grand total row styling
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 12),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('BACKGROUND', (0, -1), (-1, -1), burgundy_color),
                ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
                
                # Spans for subtotal labels
                ('SPAN', (0, num_data_rows+1), (3, num_data_rows+1)),  # External
                ('SPAN', (0, num_data_rows+2), (3, num_data_rows+2)),  # Internal
                ('SPAN', (0, num_data_rows+3), (3, num_data_rows+3)),  # Legacy
                ('SPAN', (0, -1), (3, -1)),  # Grand total
                ('SPAN', (5, num_data_rows+1), (5, -1)),  # Status column
                
                # General formatting
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1.5, border_color),
            ]))
            
            story.append(commission_table)
            story.append(Spacer(1, 20))
            
            # Commission Summary Section (Two columns like template)
            story.append(Paragraph("COMMISSION SUMMARY", section_header_style))
            
            # Add border under section header
            section_line2 = Table([[""]], colWidths=[page_width])
            section_line2.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, -1), 2, burgundy_color),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(section_line2)
            
            # Calculate values
            total_commission = total_external + total_internal + total_legacy
            company_share = (sale_order.amount_total or 0) - total_commission
            vat_amount = getattr(sale_order, 'amount_tax', 0) or 0
            net_company_share = company_share - vat_amount
            payment_amount = getattr(sale_order, 'amount_paid', 0) or 0
            
            col_width = page_width / 2 - 5*mm
            
            # Left column data - Enhanced breakdown
            left_col_data = [
                ["COMMISSION BREAKDOWN", ""],
                ["Total Sales Value:", f"AED {sale_order.amount_total or 0:,.2f}"],
                ["", ""],
                ["EXTERNAL COMMISSIONS:", ""],
                ["• Broker Commission:", f"AED {broker_amount:,.2f}"],
                ["• Referrer Commission:", f"AED {referrer_amount:,.2f}"],
                ["• Cashback Commission:", f"AED {cashback_amount:,.2f}"],
                ["• Other External:", f"AED {other_external_amount:,.2f}"],
                ["External Subtotal:", f"AED {total_external:,.2f}"],
                ["", ""],
                ["INTERNAL COMMISSIONS:", ""],
                ["• Agent 1 Commission:", f"AED {agent1_amount:,.2f}"],
                ["• Agent 2 Commission:", f"AED {agent2_amount:,.2f}"],
                ["• Manager Commission:", f"AED {manager_amount:,.2f}"],
                ["• Director Commission:", f"AED {director_amount:,.2f}"],
                ["Internal Subtotal:", f"AED {total_internal:,.2f}"],
                ["", ""],
                ["LEGACY COMMISSIONS:", ""],
                ["• Consultant (Legacy):", f"AED {consultant_amount:,.2f}"],
                ["• Manager (Legacy):", f"AED {manager_legacy_amount:,.2f}"],
                ["• Second Agent (Legacy):", f"AED {second_agent_amount:,.2f}"],
                ["• Director (Legacy):", f"AED {director_legacy_amount:,.2f}"],
                ["Legacy Subtotal:", f"AED {total_legacy:,.2f}"],
            ]
            
            # Right column data - Financial summary
            right_col_data = [
                ["FINANCIAL SUMMARY", ""],
                ["Total Commission:", f"AED {total_commission:,.2f}"],
                ["Company Share:", f"AED {company_share:,.2f}"],
                ["VAT Amount:", f"AED {vat_amount:,.2f}"],
                ["Net Company Share:", f"AED {net_company_share:,.2f}"],
                ["", ""],
                ["PAYMENT TRACKING:", ""],
                ["Total Invoiced:", f"AED {getattr(sale_order, 'amount_invoiced', 0) or 0:,.2f}"],
                ["Amount Paid:", f"AED {payment_amount:,.2f}"],
                ["Amount Due:", f"AED {(sale_order.amount_total or 0) - payment_amount:,.2f}"],
                ["", ""],
                ["STATUS INFORMATION:", ""],
                ["Commission Status:", self._get_status_display(getattr(sale_order, 'commission_status', 'draft'))],
                ["Commission Processed:", "Yes" if getattr(sale_order, 'commission_processed', False) else "No"],
                ["", ""],
                ["COMMISSION PERCENTAGES:", ""],
                ["External %:", f"{(total_external / total_commission * 100) if total_commission > 0 else 0:.1f}%"],
                ["Internal %:", f"{(total_internal / total_commission * 100) if total_commission > 0 else 0:.1f}%"],
                ["Legacy %:", f"{(total_legacy / total_commission * 100) if total_commission > 0 else 0:.1f}%"],
                ["", ""],
                ["Commission Rate:", f"{(total_commission / (sale_order.amount_total or 1) * 100):.2f}%"],
                ["Company Rate:", f"{(company_share / (sale_order.amount_total or 1) * 100):.2f}%"]
            ]
            
            # Create two separate tables side by side
            left_table = Table(left_col_data, colWidths=[col_width * 0.6, col_width * 0.4])
            left_table.setStyle(self._get_summary_table_style(burgundy_color, light_gray, border_color, green_color))
            
            right_table = Table(right_col_data, colWidths=[col_width * 0.6, col_width * 0.4])
            right_table.setStyle(self._get_summary_table_style_right(burgundy_color, light_gray, border_color, green_color))
            
            # Combine both tables in one row
            combined_table = Table([[left_table, right_table]], colWidths=[col_width, col_width])
            combined_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            story.append(combined_table)
            
            # Notes Section (if applicable)
            if hasattr(sale_order, 'commission_blocked_reason') and getattr(sale_order, 'commission_blocked_reason', False):
                story.append(Spacer(1, 10))
                
                notes_title = Paragraph("Commission Notes:", ParagraphStyle(
                    'NotesTitle',
                    parent=styles['Normal'],
                    fontSize=12,
                    textColor=colors.HexColor("#856404"),
                    fontName='Helvetica-Bold',
                    spaceBefore=0,
                    spaceAfter=10
                ))
                
                notes_content = Paragraph(str(sale_order.commission_blocked_reason), ParagraphStyle(
                    'NotesContent',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor("#856404"),
                    spaceBefore=0
                ))
                
                notes_table = Table([[notes_title], [notes_content]], colWidths=[page_width])
                notes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fff3cd")),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#ffeaa7")),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                
                story.append(notes_table)
            
            # Footer
            story.append(Spacer(1, 15))
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=medium_gray,
                alignment=TA_CENTER
            )
            
            story.append(Paragraph(
                f"Generated on {fields.Datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Report ID: {sale_order.name}-COMM-{fields.Datetime.now().strftime('%Y%m%d')}", 
                footer_style
            ))
            
            # Build PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Commission report generated successfully for order: {sale_order.name}")
            return pdf_data
        
        def _truncate_name(self, name, max_length=25):
            """Truncate long names for better table formatting"""
            if not name:
                return "N/A"
            return name[:max_length] + "..." if len(name) > max_length else name
        
        def _get_status_display(self, status):
            """Get formatted status display"""
            if not status:
                return "N/A"
            status_map = {
                'draft': 'Draft',
                'pending': 'Pending Approval',
                'approved': 'Approved',
                'paid': 'Paid',
                'legacy': 'Legacy System'
            }
            return status_map.get(status, status.replace('_', ' ').title())
        
        def _get_summary_table_style_right(self, burgundy_color, light_gray, border_color, green_color):
            """Get styling for right column summary table"""
            return TableStyle([
                # Header row (first row)
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 13),
                ('TEXTCOLOR', (0, 0), (-1, 0), burgundy_color),
                ('SPAN', (0, 0), (-1, 0)),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0), (-1, 0), light_gray),
                
                # Section headers
                ('FONT', (0, 6), (0, 6), 'Helvetica-Bold', 10),   # PAYMENT TRACKING
                ('FONT', (0, 11), (0, 11), 'Helvetica-Bold', 10), # STATUS INFORMATION
                ('FONT', (0, 15), (0, 15), 'Helvetica-Bold', 10), # COMMISSION PERCENTAGES
                ('TEXTCOLOR', (0, 6), (0, 6), burgundy_color),
                ('TEXTCOLOR', (0, 11), (0, 11), burgundy_color),
                ('TEXTCOLOR', (0, 15), (0, 15), burgundy_color),
                
                # Key metrics highlighting
                ('FONT', (0, 1), (-1, 4), 'Helvetica-Bold', 10),  # Financial summary items
                ('TEXTCOLOR', (1, 1), (1, 4), green_color),       # Financial amounts
                
                # General data rows
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#212529")),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Labels left
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Values right
                
                # General formatting
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('BOX', (0, 0), (-1, -1), 1, border_color),
            ])
        
        def _get_summary_table_style(self, burgundy_color, light_gray, border_color, green_color):
            """Get consistent styling for summary tables with enhanced breakdown"""
            return TableStyle([
                # Header row (first row)
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 13),
                ('TEXTCOLOR', (0, 0), (-1, 0), burgundy_color),
                ('SPAN', (0, 0), (-1, 0)),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0), (-1, 0), light_gray),
                
                # Section headers (EXTERNAL COMMISSIONS, INTERNAL COMMISSIONS, etc.)
                ('FONT', (0, 3), (0, 3), 'Helvetica-Bold', 10),  # EXTERNAL COMMISSIONS
                ('FONT', (0, 10), (0, 10), 'Helvetica-Bold', 10), # INTERNAL COMMISSIONS  
                ('FONT', (0, 17), (0, 17), 'Helvetica-Bold', 10), # LEGACY COMMISSIONS
                ('TEXTCOLOR', (0, 3), (0, 3), burgundy_color),
                ('TEXTCOLOR', (0, 10), (0, 10), burgundy_color),
                ('TEXTCOLOR', (0, 17), (0, 17), burgundy_color),
                
                # Subtotal rows
                ('FONT', (0, 8), (-1, 8), 'Helvetica-Bold', 10),   # External Subtotal
                ('FONT', (0, 15), (-1, 15), 'Helvetica-Bold', 10), # Internal Subtotal
                ('FONT', (0, 22), (-1, 22), 'Helvetica-Bold', 10), # Legacy Subtotal
                ('TEXTCOLOR', (0, 8), (-1, 8), burgundy_color),
                ('TEXTCOLOR', (0, 15), (-1, 15), burgundy_color),
                ('TEXTCOLOR', (0, 22), (-1, 22), burgundy_color),
                ('LINEABOVE', (0, 8), (-1, 8), 1, burgundy_color),
                ('LINEABOVE', (0, 15), (-1, 15), 1, burgundy_color),
                ('LINEABOVE', (0, 22), (-1, 22), 1, burgundy_color),
                
                # Individual commission items (with bullet points)
                ('FONT', (0, 4), (0, 7), 'Helvetica', 9),     # External items
                ('FONT', (0, 11), (0, 14), 'Helvetica', 9),   # Internal items
                ('FONT', (0, 18), (0, 21), 'Helvetica', 9),   # Legacy items
                ('TEXTCOLOR', (0, 4), (0, 7), colors.HexColor("#666")),
                ('TEXTCOLOR', (0, 11), (0, 14), colors.HexColor("#666")),
                ('TEXTCOLOR', (0, 18), (0, 21), colors.HexColor("#666")),
                ('LEFTPADDING', (0, 4), (0, 7), 15),         # Indent external items
                ('LEFTPADDING', (0, 11), (0, 14), 15),       # Indent internal items
                ('LEFTPADDING', (0, 18), (0, 21), 15),       # Indent legacy items
                
                # Amount values
                ('TEXTCOLOR', (1, 4), (1, 7), green_color),   # External amounts
                ('TEXTCOLOR', (1, 11), (1, 14), green_color), # Internal amounts
                ('TEXTCOLOR', (1, 18), (1, 21), green_color), # Legacy amounts
                ('FONT', (1, 4), (1, 22), 'Helvetica', 9),   # All amount values
                
                # General data rows
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#212529")),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Labels left
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Values right
                
                # General formatting
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('BOX', (0, 0), (-1, -1), 1, border_color),
            ])

    # ==========================================
    # models/commission_report_wizard.py
    # ==========================================

    class CommissionReportWizard(models.TransientModel):
        _name = 'commission.report.wizard'
        _description = 'Commission Report Generation Wizard'

        sale_order_id = fields.Many2one(
            'sale.order', 
            string='Sale Order',
            required=True,
            default=lambda self: self._get_default_sale_order()
        )
        
        report_type = fields.Selection([
            ('detailed', 'Detailed Commission Report'),
            ('summary', 'Summary Report')
        ], default='detailed', string='Report Type', required=True)
        
        include_notes = fields.Boolean(
            'Include Commission Notes',
            default=True,
            help="Include commission notes and blocked reasons if any"
        )
        
        def _get_default_sale_order(self):
            """Get sale order from context"""
            return self.env.context.get('active_id', False)
        
        def action_generate_report(self):
            """Generate and download the commission report"""
            if not self.sale_order_id:
                raise UserError("Please select a sale order")
                
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Generating enhanced commission report for order: {self.sale_order_id.name}")
                
                # Use the enhanced commission report generator
                report_generator = self.env['commission.report.generator'].sudo()
                
                # Generate the enhanced PDF report
                # Use the enhanced commission report generator
                report_generator = self.env['commission.report.generator'].sudo()
                
                # Generate the enhanced PDF report
                pdf_data = report_generator.generate_commission_report(self.sale_order_id.id)
                
                if not pdf_data:
                    raise UserError("Failed to generate PDF data")
                
                # Create temporary attachment for preview
                filename = f"Commission_Report_Preview_{self.sale_order_id.name.replace('/', '_')}.pdf"
                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary', 
                    'datas': base64.b64encode(pdf_data).decode(),
                    'res_model': 'commission.report.wizard',
                    'res_id': self.id,
                    'mimetype': 'application/pdf'
                })
                
                # Return preview action
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}',
                    'target': 'new',
                }
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error previewing commission report: {str(e)}", exc_info=True)
                raise UserError(f"Error previewing commission report: {str(e)}")
        
        def action_debug_fields(self):
            """Debug method to check available fields on sale order"""
            if not self.sale_order_id:
                raise UserError("Please select a sale order")
            
            order = self.sale_order_id
            debug_info = []
            
            # Check all commission fields
            fields_to_check = [
                # External Commission Fields
                'broker_partner_id', 'broker_commission_type', 'broker_rate', 'broker_amount',
                'referrer_partner_id', 'referrer_commission_type', 'referrer_rate', 'referrer_amount',
                'cashback_partner_id', 'cashback_commission_type', 'cashback_rate', 'cashback_amount',
                'other_external_partner_id', 'other_external_commission_type', 'other_external_rate', 'other_external_amount',
                
                # Internal Commission Fields
                'agent1_partner_id', 'agent1_commission_type', 'agent1_rate', 'agent1_amount',
                'agent2_partner_id', 'agent2_commission_type', 'agent2_rate', 'agent2_amount',
                'manager_partner_id', 'manager_commission_type', 'manager_rate', 'manager_amount',
                'director_partner_id', 'director_commission_type', 'director_rate', 'director_amount',
                
                # Legacy Commission Fields
                'consultant_id', 'consultant_comm_percentage', 'salesperson_commission',
                'manager_id', 'manager_comm_percentage', 'manager_commission',
                'second_agent_id', 'second_agent_comm_percentage', 'second_agent_commission',
                'director_id', 'director_comm_percentage', 'director_commission',
                
                # General Fields
                'amount_total', 'amount_invoiced', 'amount_paid', 'amount_tax',
                'commission_status', 'commission_processed', 'commission_blocked_reason'
            ]
            
            debug_info.append("=== EXTERNAL COMMISSIONS ===")
            for field in fields_to_check[:16]:  # External fields
                if hasattr(order, field):
                    value = getattr(order, field)
                    if value:
                        debug_info.append(f"✓ {field}: {value}")
                    else:
                        debug_info.append(f"○ {field}: Empty/False")
                else:
                    debug_info.append(f"✗ {field}: FIELD NOT FOUND")
            
            debug_info.append("\n=== INTERNAL COMMISSIONS ===")
            for field in fields_to_check[16:32]:  # Internal fields
                if hasattr(order, field):
                    value = getattr(order, field)
                    if value:
                        debug_info.append(f"✓ {field}: {value}")
                    else:
                        debug_info.append(f"○ {field}: Empty/False")
                else:
                    debug_info.append(f"✗ {field}: FIELD NOT FOUND")
            
            debug_info.append("\n=== LEGACY COMMISSIONS ===")
            for field in fields_to_check[32:44]:  # Legacy fields
                if hasattr(order, field):
                    value = getattr(order, field)
                    if value:
                        debug_info.append(f"✓ {field}: {value}")
                    else:
                        debug_info.append(f"○ {field}: Empty/False")
                else:
                    debug_info.append(f"✗ {field}: FIELD NOT FOUND")
            
            debug_info.append("\n=== GENERAL FIELDS ===")
            for field in fields_to_check[44:]:  # General fields
                if hasattr(order, field):
                    value = getattr(order, field)
                    debug_info.append(f"✓ {field}: {value}")
                else:
                    debug_info.append(f"✗ {field}: FIELD NOT FOUND")
            
            # Log order lines
            if order.order_line:
                debug_info.append(f"\n=== ORDER LINES ({len(order.order_line)} lines) ===")
                for line in order.order_line[:5]:  # Show first 5 lines only
                    debug_info.append(f"  - {line.product_id.name}: {line.product_uom_qty} x {line.price_unit} = {line.price_subtotal}")
                if len(order.order_line) > 5:
                    debug_info.append(f"  ... and {len(order.order_line) - 5} more lines")
            
            message = "\n".join(debug_info)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Field Debug for {order.name}:\n{message}")
            
            # Show summary in user message
            summary_lines = []
            total_external = sum(getattr(order, field, 0) or 0 for field in ['broker_amount', 'referrer_amount', 'cashback_amount', 'other_external_amount'])
            total_internal = sum(getattr(order, field, 0) or 0 for field in ['agent1_amount', 'agent2_amount', 'manager_amount', 'director_amount'])
            total_legacy = sum(getattr(order, field, 0) or 0 for field in ['salesperson_commission', 'manager_commission', 'second_agent_commission', 'director_commission'])
            
            summary_lines.append(f"Order: {order.name}")
            summary_lines.append(f"Total Amount: AED {order.amount_total or 0:,.2f}")
            summary_lines.append(f"External Commissions: AED {total_external:,.2f}")
            summary_lines.append(f"Internal Commissions: AED {total_internal:,.2f}")
            summary_lines.append(f"Legacy Commissions: AED {total_legacy:,.2f}")
            summary_lines.append(f"Total Commission: AED {total_external + total_internal + total_legacy:,.2f}")
            
            summary = "\n".join(summary_lines)
            raise UserError(f"Commission Debug Summary:\n\n{summary}\n\n(Check server logs for detailed field information)")
