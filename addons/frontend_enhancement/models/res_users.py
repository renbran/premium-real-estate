# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    """
    Extended User model to support file upload functionality
    """
    _inherit = 'res.users'
    
    # Many2many relationship for file attachments
    attachment_ids = fields.Many2many(
        'file.attachment.enhancement',
        'user_file_attachment_rel',
        'user_id',
        'attachment_id',
        string='File Attachments',
        help="Files uploaded by or related to this user"
    )
    
    # Count of attachments for display
    attachment_count = fields.Integer(
        string='Attachment Count',
        compute='_compute_attachment_count',
        help="Total number of file attachments"
    )
    
    # Additional fields for enhanced functionality
    max_upload_size = fields.Integer(
        string='Max Upload Size (MB)',
        default=50,
        help="Maximum file upload size in MB for this user"
    )
    
    allowed_file_types = fields.Text(
        string='Allowed File Types',
        default='.pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar',
        help="Comma-separated list of allowed file extensions"
    )
    
    upload_notifications = fields.Boolean(
        string='Upload Notifications',
        default=True,
        help="Receive notifications when files are uploaded"
    )
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        """
        Compute the count of active attachments
        """
        for user in self:
            user.attachment_count = len(user.attachment_ids.filtered('is_active'))
    
    def action_view_attachments(self):
        """
        Action to view user's file attachments
        """
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('My File Attachments'),
            'res_model': 'file.attachment.enhancement',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.id), ('is_active', '=', True)],
            'context': {
                'default_user_id': self.id,
                'default_related_model': 'res.users',
                'default_related_record_id': self.id,
            },
            'target': 'current',
        }
    
    def action_upload_file(self):
        """
        Action to open file upload dialog
        """
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Upload File'),
            'res_model': 'file.attachment.enhancement',
            'view_mode': 'form',
            'view_id': self.env.ref('frontend_enhancement.view_file_attachment_form_upload').id,
            'context': {
                'default_user_id': self.id,
                'default_related_model': 'res.users',
                'default_related_record_id': self.id,
            },
            'target': 'new',
        }
    
    @api.model
    def create_file_attachment(self, file_data, file_name, description=None):
        """
        Helper method to create file attachment for user
        """
        user = self.env.user
        
        # Validate file size
        max_size = user.max_upload_size * 1024 * 1024  # Convert MB to bytes
        if len(file_data) > max_size:
            raise ValidationError(_("File size exceeds the maximum allowed size of %d MB.") % user.max_upload_size)
        
        # Validate file type
        if user.allowed_file_types:
            import os
            file_ext = os.path.splitext(file_name)[1].lower()
            allowed_types = [ext.strip() for ext in user.allowed_file_types.split(',')]
            if file_ext not in allowed_types:
                raise ValidationError(_("File type '%s' is not allowed. Allowed types: %s") % (file_ext, user.allowed_file_types))
        
        # Create attachment
        attachment = self.env['file.attachment.enhancement'].create({
            'name': file_name,
            'description': description or '',
            'file_data': file_data,
            'user_id': user.id,
            'related_model': 'res.users',
            'related_record_id': user.id,
        })
        
        # Add to user's attachments
        user.attachment_ids = [(4, attachment.id)]
        
        # Send notification if enabled
        if user.upload_notifications:
            user.message_post(
                body=_("New file uploaded: %s") % file_name,
                subject=_("File Upload Notification")
            )
        
        return attachment
    
    def get_allowed_file_types_list(self):
        """
        Get list of allowed file types for this user
        """
        self.ensure_one()
        if self.allowed_file_types:
            return [ext.strip() for ext in self.allowed_file_types.split(',')]
        return []
    
    def get_upload_statistics(self):
        """
        Get upload statistics for the user
        """
        self.ensure_one()
        
        attachments = self.attachment_ids.filtered('is_active')
        
        total_files = len(attachments)
        total_size = sum(attachments.mapped('file_size'))
        total_downloads = sum(attachments.mapped('download_count'))
        
        # Calculate average file size
        avg_size = total_size / total_files if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_downloads': total_downloads,
            'average_size': avg_size,
            'recent_uploads': attachments.sorted('create_date', reverse=True)[:5],
        }
    
    def cleanup_inactive_attachments(self):
        """
        Clean up inactive attachments (admin only)
        """
        if not self.env.user.has_group('base.group_system'):
            raise ValidationError(_("Only system administrators can clean up attachments."))
        
        inactive_attachments = self.attachment_ids.filtered(lambda a: not a.is_active)
        count = len(inactive_attachments)
        
        inactive_attachments.unlink()
        
        self.message_post(
            body=_("Cleaned up %d inactive file attachments") % count,
            subject=_("Attachment Cleanup")
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Cleaned up %d inactive attachments.') % count,
                'type': 'success',
            }
        }
    
    @api.constrains('max_upload_size')
    def _check_max_upload_size(self):
        """
        Validate maximum upload size
        """
        for user in self:
            if user.max_upload_size <= 0:
                raise ValidationError(_("Maximum upload size must be greater than 0."))
            if user.max_upload_size > 100:  # 100MB hard limit
                raise ValidationError(_("Maximum upload size cannot exceed 100 MB."))
