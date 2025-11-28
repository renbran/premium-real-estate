# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class MedicalAppointmentExtended(models.Model):
    _inherit = 'medical.appointment'

    # Enhanced appointment fields
    appointment_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('followup', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('surgery', 'Surgery'),
        ('therapy', 'Therapy'),
        ('checkup', 'Check-up'),
        ('vaccination', 'Vaccination'),
    ], 'Appointment Type', default='consultation')
    
    # Appointment Slot Management
    appointment_slot_id = fields.Many2one('medical.appointment.slot', 'Time Slot')
    slot_duration = fields.Integer('Duration (Minutes)', default=30)
    
    # Enhanced Status Management
    state = fields.Selection(selection_add=[
        ('scheduled', 'Scheduled'),
        ('arrived', 'Patient Arrived'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ], ondelete={'scheduled': 'cascade', 'arrived': 'cascade', 'in_progress': 'cascade', 
                'completed': 'cascade', 'no_show': 'cascade', 'rescheduled': 'cascade'})
    
    # Patient Management
    arrival_time = fields.Datetime('Arrival Time')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    actual_duration = fields.Integer('Actual Duration (Minutes)', compute='_compute_actual_duration', store=True)
    
    # Reminders and Notifications
    reminder_sent = fields.Boolean('Reminder Sent', default=False)
    reminder_date = fields.Datetime('Reminder Date')
    confirmation_required = fields.Boolean('Confirmation Required', default=False)
    confirmed = fields.Boolean('Confirmed', default=False)
    confirmation_date = fields.Datetime('Confirmation Date')
    
    # Recurring Appointments
    is_recurring = fields.Boolean('Recurring Appointment')
    recurrence_rule = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], 'Recurrence')
    recurrence_count = fields.Integer('Number of Occurrences')
    parent_appointment_id = fields.Many2one('medical.appointment', 'Parent Appointment')
    child_appointment_ids = fields.One2many('medical.appointment', 'parent_appointment_id', 'Recurring Appointments')
    
    # Additional Information
    chief_complaint = fields.Text('Chief Complaint')
    symptoms = fields.Text('Symptoms')
    vital_signs = fields.Text('Vital Signs')
    diagnosis = fields.Text('Diagnosis')
    treatment_plan = fields.Text('Treatment Plan')
    follow_up_required = fields.Boolean('Follow-up Required')
    follow_up_date = fields.Date('Follow-up Date')
    follow_up_notes = fields.Text('Follow-up Notes')
    
    # Location and Resources
    room_id = fields.Many2one('medical.room', 'Room')
    equipment_needed = fields.Text('Equipment Needed')
    special_instructions = fields.Text('Special Instructions')
    
    # Integration with Calendar
    calendar_event_id = fields.Many2one('calendar.event', 'Calendar Event')
    
    # No-Show Management
    no_show_count = fields.Integer('No Show Count', compute='_compute_no_show_count')
    no_show_reason = fields.Text('No Show Reason')
    
    @api.depends('start_time', 'end_time')
    def _compute_actual_duration(self):
        for appointment in self:
            if appointment.start_time and appointment.end_time:
                delta = appointment.end_time - appointment.start_time
                appointment.actual_duration = int(delta.total_seconds() / 60)
            else:
                appointment.actual_duration = 0

    @api.depends('patient_id')
    def _compute_no_show_count(self):
        for appointment in self:
            if appointment.patient_id:
                no_shows = self.search_count([
                    ('patient_id', '=', appointment.patient_id.id),
                    ('state', '=', 'no_show')
                ])
                appointment.no_show_count = no_shows
            else:
                appointment.no_show_count = 0

    @api.constrains('appointment_date', 'appointment_end')
    def _check_appointment_dates(self):
        for appointment in self:
            if appointment.appointment_date >= appointment.appointment_end:
                raise ValidationError(_('Appointment end time must be after start time.'))

    def action_schedule(self):
        """Schedule the appointment"""
        self.write({
            'state': 'scheduled',
            'confirmed': True,
            'confirmation_date': fields.Datetime.now()
        })
        self._create_calendar_event()
        self._schedule_reminder()
        return True

    def action_patient_arrived(self):
        """Mark patient as arrived"""
        self.write({
            'state': 'arrived',
            'arrival_time': fields.Datetime.now()
        })
        return True

    def action_start_appointment(self):
        """Start the appointment"""
        self.write({
            'state': 'in_progress',
            'start_time': fields.Datetime.now()
        })
        return True

    def action_complete_appointment(self):
        """Complete the appointment"""
        self.write({
            'state': 'completed',
            'end_time': fields.Datetime.now()
        })
        if self.follow_up_required:
            self._create_follow_up_appointment()
        return True

    def action_mark_no_show(self):
        """Mark patient as no show"""
        self.write({'state': 'no_show'})
        # Could trigger penalties or notifications
        return True

    def action_reschedule(self):
        """Reschedule appointment"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reschedule Appointment',
            'res_model': 'appointment.reschedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_appointment_id': self.id}
        }

    def _create_calendar_event(self):
        """Create calendar event for appointment"""
        if not self.calendar_event_id:
            event_vals = {
                'name': f'Appointment: {self.patient_id.name} - {self.doctor_id.name}',
                'description': f'Patient: {self.patient_id.name}\nDoctor: {self.doctor_id.name}\nType: {self.appointment_type}',
                'start': self.appointment_date,
                'stop': self.appointment_end,
                'user_id': self.doctor_id.user_id.id if self.doctor_id.user_id else self.env.user.id,
                'partner_ids': [(6, 0, [self.patient_id.patient_id.id])] if self.patient_id.patient_id else [],
            }
            event = self.env['calendar.event'].create(event_vals)
            self.calendar_event_id = event.id

    def _schedule_reminder(self):
        """Schedule appointment reminder"""
        if not self.reminder_sent and self.appointment_date:
            reminder_time = self.appointment_date - timedelta(hours=24)  # 24 hours before
            self.reminder_date = reminder_time
            # Could create mail activity or cron job for reminder

    def _create_follow_up_appointment(self):
        """Create follow-up appointment"""
        if self.follow_up_required and self.follow_up_date:
            follow_up_vals = {
                'patient_id': self.patient_id.id,
                'doctor_id': self.doctor_id.id,
                'appointment_date': datetime.combine(self.follow_up_date, datetime.min.time()),
                'appointment_end': datetime.combine(self.follow_up_date, datetime.min.time()) + timedelta(minutes=self.slot_duration),
                'appointment_type': 'followup',
                'comments': self.follow_up_notes,
                'parent_appointment_id': self.id,
            }
            follow_up = self.create(follow_up_vals)
            return follow_up

    def create_recurring_appointments(self):
        """Create recurring appointments"""
        if not self.is_recurring or not self.recurrence_rule or not self.recurrence_count:
            return

        appointments = []
        base_date = self.appointment_date
        
        for i in range(1, self.recurrence_count + 1):
            if self.recurrence_rule == 'daily':
                next_date = base_date + timedelta(days=i)
            elif self.recurrence_rule == 'weekly':
                next_date = base_date + timedelta(weeks=i)
            elif self.recurrence_rule == 'monthly':
                next_date = base_date + timedelta(days=30*i)  # Simplified monthly
            elif self.recurrence_rule == 'yearly':
                next_date = base_date + timedelta(days=365*i)  # Simplified yearly
            
            appointment_vals = {
                'patient_id': self.patient_id.id,
                'doctor_id': self.doctor_id.id,
                'appointment_date': next_date,
                'appointment_end': next_date + timedelta(minutes=self.slot_duration),
                'appointment_type': self.appointment_type,
                'consultations_id': self.consultations_id.id,
                'parent_appointment_id': self.id,
            }
            appointments.append(appointment_vals)
        
        if appointments:
            self.env['medical.appointment'].create(appointments)


class MedicalRoom(models.Model):
    _name = 'medical.room'
    _description = 'Medical Room'

    name = fields.Char('Room Name', required=True)
    code = fields.Char('Room Code')
    room_type = fields.Selection([
        ('consultation', 'Consultation Room'),
        ('examination', 'Examination Room'),
        ('surgery', 'Surgery Room'),
        ('emergency', 'Emergency Room'),
        ('therapy', 'Therapy Room'),
        ('waiting', 'Waiting Room'),
    ], 'Room Type', required=True)
    
    capacity = fields.Integer('Capacity', default=1)
    equipment_ids = fields.Many2many('medical.equipment', string='Equipment')
    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Notes')
    
    appointment_ids = fields.One2many('medical.appointment', 'room_id', 'Appointments')


class MedicalEquipment(models.Model):
    _name = 'medical.equipment'
    _description = 'Medical Equipment'

    name = fields.Char('Equipment Name', required=True)
    code = fields.Char('Equipment Code')
    equipment_type = fields.Char('Equipment Type')
    manufacturer = fields.Char('Manufacturer')
    model = fields.Char('Model')
    serial_number = fields.Char('Serial Number')
    
    room_ids = fields.Many2many('medical.room', string='Rooms')
    maintenance_date = fields.Date('Last Maintenance')
    next_maintenance_date = fields.Date('Next Maintenance')
    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Notes')