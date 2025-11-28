# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birthday = fields.Date(
        string='Date of Birth',
        help="Employee's birthday for birthday greetings"
    )

    def birthday_reminder(self):
        """
        Automated birthday reminder system for OSUS Properties
        Sends birthday wishes to employees and notifications to team
        """
        try:
            today = date.today()
            month = today.month
            day = today.day
            
            # Find employees with birthdays today
            birthday_employees = self.search([
                ('birthday', '!=', False),
                ('active', '=', True)
            ])
            
            for employee in birthday_employees:
                if (employee.birthday and 
                    employee.birthday.day == day and 
                    employee.birthday.month == month):
                    
                    _logger.info(f"Processing birthday for {employee.name}")
                    
                    # Send personal birthday wish to the employee
                    if employee.work_email:
                        try:
                            birthday_template = self.env.ref(
                                'osus_hr_greetings.mail_template_birthday_personal'
                            )
                            birthday_template.send_mail(employee.id, force_send=True)
                            _logger.info(f"Personal birthday wish sent to {employee.name}")
                        except Exception as e:
                            _logger.error(f"Failed to send birthday wish to {employee.name}: {str(e)}")
                    
                    # Send announcement to all other employees
                    other_employees = self.search([
                        ('id', '!=', employee.id),
                        ('work_email', '!=', False),
                        ('active', '=', True)
                    ])
                    
                    if other_employees:
                        all_emails = other_employees.mapped('work_email')
                        if all_emails:
                            try:
                                reminder_template = self.env.ref(
                                    'osus_hr_greetings.mail_template_birthday_announcement'
                                )
                                email_values = {
                                    'email_to': ','.join(all_emails),
                                    'email_cc': False,
                                    'email_bcc': False,
                                }
                                reminder_template.send_mail(
                                    employee.id, 
                                    email_values=email_values, 
                                    force_send=True
                                )
                                _logger.info(f"Birthday announcement sent to {len(all_emails)} employees")
                            except Exception as e:
                                _logger.error(f"Failed to send birthday announcement: {str(e)}")
                                
        except Exception as e:
            _logger.error(f"Error in birthday_reminder function: {str(e)}")

    def work_anniversary_reminder(self):
        """
        Automated work anniversary reminder system for OSUS Properties
        Sends anniversary wishes to employees and notifications to team
        """
        try:
            today = date.today()
            month = today.month
            day = today.day
            
            # Find employees with work anniversaries today
            anniversary_employees = self.search([
                ('joining_date', '!=', False),
                ('active', '=', True)
            ])
            
            for employee in anniversary_employees:
                if (employee.joining_date and 
                    employee.joining_date.day == day and 
                    employee.joining_date.month == month):  # Check if today is anniversary
                    
                    # Calculate years of service for logging
                    years_of_service = relativedelta(today, employee.joining_date).years
                    _logger.info(f"Processing {years_of_service} year anniversary for {employee.name}")
                    
                    # Send personal anniversary wish to the employee
                    if employee.work_email:
                        try:
                            anniversary_template = self.env.ref(
                                'osus_hr_greetings.mail_template_anniversary_personal'
                            )
                            anniversary_template.send_mail(employee.id, force_send=True)
                            _logger.info(f"Personal anniversary wish sent to {employee.name}")
                        except Exception as e:
                            _logger.error(f"Failed to send anniversary wish to {employee.name}: {str(e)}")
                    
                    # Send announcement to all other employees
                    other_employees = self.search([
                        ('id', '!=', employee.id),
                        ('work_email', '!=', False),
                        ('active', '=', True)
                    ])
                    
                    if other_employees:
                        all_emails = other_employees.mapped('work_email')
                        if all_emails:
                            try:
                                announcement_template = self.env.ref(
                                    'osus_hr_greetings.mail_template_anniversary_announcement'
                                )
                                email_values = {
                                    'email_to': ','.join(all_emails),
                                    'email_cc': False,
                                    'email_bcc': False,
                                }
                                announcement_template.send_mail(
                                    employee.id, 
                                    email_values=email_values, 
                                    force_send=True
                                )
                                _logger.info(f"Anniversary announcement sent to {len(all_emails)} employees")
                            except Exception as e:
                                _logger.error(f"Failed to send anniversary announcement: {str(e)}")
                                
        except Exception as e:
            _logger.error(f"Error in work_anniversary_reminder function: {str(e)}")

    @api.model
    def _cron_birthday_reminder(self):
        """Cron job method for automated birthday reminders"""
        _logger.info("Starting OSUS Properties birthday reminder cron job")
        self.birthday_reminder()
        _logger.info("Completed OSUS Properties birthday reminder cron job")

    @api.model
    def _cron_anniversary_reminder(self):
        """Cron job method for automated work anniversary reminders"""
        _logger.info("Starting OSUS Properties work anniversary reminder cron job")
        self.work_anniversary_reminder()
        _logger.info("Completed OSUS Properties work anniversary reminder cron job")