from odoo import models
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def birthday_reminder(self):
        month = date.today().month
        day = date.today().day
        for employee in self.search([('birthday', '!=', False)]):
            if employee.birthday.day == day and employee.birthday.month == month:
                try:
                    # Use correct template external IDs
                    self.env.ref('wt_birthday_reminder.mail_template_birthday_wish').send_mail(employee.id, force_send=True)
                    _logger.info(f"Birthday wish sent successfully to {employee.name}")
                except Exception as e:
                    _logger.error(f"Failed to send birthday wish to {employee.name}: {str(e)}")
                
                # Send reminder to all other employees
                all_email = self.search([('id', '!=', employee.id), ('work_email', '!=', False)]).mapped('work_email')
                if all_email:
                    email_values = {'email_to': ','.join(all_email)}
                    try:
                        self.env.ref('wt_birthday_reminder.mail_template_birthday_reminder').send_mail(employee.id, email_values=email_values, force_send=True)
                        _logger.info(f"Birthday reminder sent successfully for {employee.name} to {len(all_email)} employees")
                    except Exception as e:
                        _logger.error(f"Failed to send birthday reminder for {employee.name}: {str(e)}")
