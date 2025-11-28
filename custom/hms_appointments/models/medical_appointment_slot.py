# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta, time
from odoo.exceptions import UserError, ValidationError


class MedicalAppointmentSlot(models.Model):
    _name = 'medical.appointment.slot'
    _description = 'Medical Appointment Time Slot'
    _order = 'date, start_time'

    name = fields.Char('Slot Name', compute='_compute_name', store=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor', required=True)
    date = fields.Date('Date', required=True)
    start_time = fields.Float('Start Time', required=True)
    end_time = fields.Float('End Time', required=True)
    duration = fields.Integer('Duration (Minutes)', compute='_compute_duration', store=True)
    
    # Availability
    is_available = fields.Boolean('Available', default=True)
    appointment_id = fields.Many2one('medical.appointment', 'Appointment')
    
    # Slot Configuration
    max_patients = fields.Integer('Max Patients', default=1)
    booked_patients = fields.Integer('Booked Patients', compute='_compute_booked_patients')
    
    # Recurring Slots
    is_template = fields.Boolean('Template Slot')
    recurrence_rule = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], 'Recurrence')
    
    # Additional Info
    room_id = fields.Many2one('medical.room', 'Room')
    appointment_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('followup', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('surgery', 'Surgery'),
        ('therapy', 'Therapy'),
        ('checkup', 'Check-up'),
    ], 'Appointment Type')
    
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('blocked', 'Blocked'),
    ], 'Status', default='available', compute='_compute_state', store=True)

    @api.depends('doctor_id', 'date', 'start_time', 'end_time')
    def _compute_name(self):
        for slot in self:
            if slot.doctor_id and slot.date:
                start_hour = int(slot.start_time)
                start_minute = int((slot.start_time - start_hour) * 60)
                end_hour = int(slot.end_time)
                end_minute = int((slot.end_time - end_hour) * 60)
                
                slot.name = f"{slot.doctor_id.name} - {slot.date} {start_hour:02d}:{start_minute:02d}-{end_hour:02d}:{end_minute:02d}"
            else:
                slot.name = "New Slot"

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for slot in self:
            if slot.start_time and slot.end_time:
                slot.duration = int((slot.end_time - slot.start_time) * 60)
            else:
                slot.duration = 0

    @api.depends('appointment_id', 'max_patients')
    def _compute_booked_patients(self):
        for slot in self:
            if slot.appointment_id:
                slot.booked_patients = 1  # For now, one appointment per slot
            else:
                slot.booked_patients = 0

    @api.depends('is_available', 'booked_patients', 'max_patients')
    def _compute_state(self):
        for slot in self:
            if not slot.is_available:
                slot.state = 'blocked'
            elif slot.booked_patients >= slot.max_patients:
                slot.state = 'booked'
            else:
                slot.state = 'available'

    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for slot in self:
            if slot.start_time >= slot.end_time:
                raise ValidationError(_('End time must be after start time.'))

    @api.constrains('doctor_id', 'date', 'start_time', 'end_time')
    def _check_overlap(self):
        for slot in self:
            if slot.doctor_id and slot.date:
                overlapping = self.search([
                    ('doctor_id', '=', slot.doctor_id.id),
                    ('date', '=', slot.date),
                    ('id', '!=', slot.id),
                    ('start_time', '<', slot.end_time),
                    ('end_time', '>', slot.start_time),
                ])
                if overlapping:
                    raise ValidationError(_('This time slot overlaps with existing slots for the same doctor.'))

    def book_slot(self, appointment_id):
        """Book the slot for an appointment"""
        if self.state != 'available':
            raise UserError(_('This slot is not available for booking.'))
        
        self.write({
            'appointment_id': appointment_id,
            'is_available': False
        })
        return True

    def release_slot(self):
        """Release the slot"""
        self.write({
            'appointment_id': False,
            'is_available': True
        })
        return True

    def action_block_slot(self):
        """Block the slot"""
        self.write({'is_available': False})
        return True

    def action_unblock_slot(self):
        """Unblock the slot"""
        self.write({'is_available': True})
        return True

    @api.model
    def generate_slots_for_schedule(self, schedule_id, date_from, date_to):
        """Generate slots based on doctor schedule"""
        schedule = self.env['medical.doctor.schedule'].browse(schedule_id)
        if not schedule:
            return
        
        current_date = date_from
        slots_created = []
        
        while current_date <= date_to:
            # Check if schedule applies to this day
            weekday = current_date.weekday()  # 0 = Monday, 6 = Sunday
            
            if schedule.applies_to_weekday(weekday):
                # Create slots based on schedule
                slot_start = schedule.start_time
                
                while slot_start < schedule.end_time:
                    slot_end = slot_start + (schedule.slot_duration / 60.0)  # Convert minutes to hours
                    
                    if slot_end <= schedule.end_time:
                        slot_vals = {
                            'doctor_id': schedule.doctor_id.id,
                            'date': current_date,
                            'start_time': slot_start,
                            'end_time': slot_end,
                            'room_id': schedule.room_id.id if schedule.room_id else False,
                            'appointment_type': schedule.default_appointment_type,
                        }
                        
                        # Check if slot already exists
                        existing = self.search([
                            ('doctor_id', '=', schedule.doctor_id.id),
                            ('date', '=', current_date),
                            ('start_time', '=', slot_start),
                            ('end_time', '=', slot_end),
                        ])
                        
                        if not existing:
                            slot = self.create(slot_vals)
                            slots_created.append(slot.id)
                    
                    slot_start = slot_end
            
            current_date += timedelta(days=1)
        
        return slots_created

    def float_to_time(self, float_time):
        """Convert float time to time object"""
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return time(hours, minutes)