# -*- coding: utf-8 -*-
{
    'name': 'HMS Advanced Appointments',
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Appointments',
    'summary': 'Advanced appointment scheduling and management for Hospital Management System',
    'description': '''
        HMS Advanced Appointments
        =========================
        
        Enhanced appointment management features for Basic Hospital Management System:
        
        * Advanced appointment scheduling with time slots
        * Doctor availability management
        * Appointment calendar integration
        * Online appointment booking
        * Appointment reminders and notifications
        * Recurring appointments support
        * Appointment conflicts detection
        * Waiting list management
        * Appointment history tracking
        * Patient no-show tracking
        * Appointment analytics and reports
        * Multi-location appointment support
        
        This module extends the basic HMS functionality with comprehensive
        appointment scheduling and management capabilities.
    ''',
    'author': 'HMS Development Team',
    'website': 'https://www.example.com',
    'depends': ['basic_hms', 'calendar', 'website', 'mail'],
    'data': [
        'security/appointment_security.xml',
        'security/ir.model.access.csv',
        'views/hms_appointments_menu.xml',
        'views/medical_appointment_extended_views.xml',
        'views/medical_appointment_slot_views.xml',
        'views/medical_doctor_schedule_views.xml',
        'views/medical_appointment_calendar_views.xml',
        'wizard/appointment_booking_wizard_views.xml',
        'wizard/appointment_reschedule_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}