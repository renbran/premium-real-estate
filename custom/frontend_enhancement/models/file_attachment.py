# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import logging
import mimetypes
import os

_logger = logging.getLogger(__name__)


class FileAttachmentEnhancement(models.Model):
    """
    Model for handling enhanced file attachments with logging capabilities
    """
    _name = 'file.attachment.enhancement'
    _description = 'Enhanced File Attachment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char(
        string='File Name',
        required=True,
        tracking=True,
        help="Name of the uploaded file"
    )
    
    description = fields.Text(
        string='Description',
        help="Description of the file content"
    )
    
    file_data = fields.Binary(
        string='File Content',
        required=True,
        attachment=True,
        help="The actual file content"
    )
    
    file_size = fields.Integer(
        string='File Size (bytes)',
        compute='_compute_file_size',
        store=True,
        help="Size of the file in bytes"
    )
    
    file_type = fields.Char(
        string='File Type',
        compute='_compute_file_type',
        store=True,
        help="MIME type of the file"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Uploaded By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        help="User who uploaded the file"
    )
    
    related_model = fields.Char(
        string='Related Model',
        help="Model name that this file is related to"
    )
    
    related_record_id = fields.Integer(
        string='Related Record ID',
        help="ID of the record this file is related to"
    )
    
    upload_date = fields.Datetime(
        string='Upload Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help="Date and time when the file was uploaded"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Whether this file attachment is active"
    )
    
    access_level = fields.Selection([
        ('public', 'Public'),
        ('internal', 'Internal Only'),
        ('restricted', 'Restricted')
    ], default='internal', string='Access Level', tracking=True)
    
    download_count = fields.Integer(
        string='Download Count',
        default=0,
        help="Number of times this file has been downloaded"
    )
    
    @api.depends('file_data')
    def _compute_file_size(self):
        """
        Compute the file size from binary data
        """
        for record in self:
            if record.file_data:
                # Estimate size from base64 encoded data
                record.file_size = len(base64.b64decode(record.file_data)) if record.file_data else 0
            else:
                record.file_size = 0
    
    @api.depends('name')
    def _compute_file_type(self):
        """
        Compute the file type from file name
        """
        for record in self:
            if record.name:
                mime_type, _ = mimetypes.guess_type(record.name)
                record.file_type = mime_type or 'application/octet-stream'
            else:
                record.file_type = 'application/octet-stream'
    
    @api.model
    def create(self, vals):
        """
        Override create to validate and log file upload
        """
        # Validate file size (max 50MB)
        if vals.get('file_data'):
            file_size = len(base64.b64decode(vals['file_data']))
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                raise ValidationError(_("File size cannot exceed 50MB."))
        
        # Validate file type
        if vals.get('name'):
            file_ext = os.path.splitext(vals['name'])[1].lower()
            allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar']
            if file_ext not in allowed_extensions:
                raise ValidationError(_("File type '%s' is not allowed. Allowed types: %s") % (file_ext, ', '.join(allowed_extensions)))
        
        result = super(FileAttachmentEnhancement, self).create(vals)
        
        # Log file upload
        result.message_post(
            body=_("File uploaded: %s (%s bytes)") % (result.name, result.file_size),
            subject=_("File Upload")
        )
        
        # Log to related record if specified
        if result.related_model and result.related_record_id:
            try:
                related_record = self.env[result.related_model].browse(result.related_record_id)
                if related_record.exists():
                    related_record.message_post(
                        body=_("File attached: %s (uploaded by %s)") % (result.name, result.user_id.name),
                        subject=_("File Attachment"),
                        attachment_ids=[(4, result.id)]
                    )
            except Exception as e:
                _logger.warning("Could not log file attachment to related record: %s", str(e))
        
        return result
    
    def action_download(self):
        """
        Action to download the file and increment download count
        """
        self.ensure_one()
        
        # Increment download count
        self.download_count += 1
        
        # Log download
        self.message_post(
            body=_("File downloaded by %s") % self.env.user.name,
            subject=_("File Download")
        )
        
        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/file.attachment.enhancement/{self.id}/file_data/{self.name}?download=true',
            'target': 'self',
        }
    
    def action_delete(self):
        """
        Action to delete the file with confirmation
        """
        self.ensure_one()
        
        # Log deletion
        self.message_post(
            body=_("File marked for deletion by %s") % self.env.user.name,
            subject=_("File Deletion")
        )
        
        # Soft delete (mark as inactive)
        self.is_active = False
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_permanent_delete(self):
        """
        Action to permanently delete the file (admin only)
        """
        self.ensure_one()
        
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only system administrators can permanently delete files."))
        
        # Log permanent deletion
        file_name = self.name
        self.message_post(
            body=_("File permanently deleted by %s") % self.env.user.name,
            subject=_("Permanent File Deletion")
        )
        
        # Actually delete the record
        self.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('File "%s" has been permanently deleted.') % file_name,
                'type': 'success',
            }
        }
    
    @api.constrains('name')
    def _check_file_name(self):
        """
        Validate file name
        """
        for record in self:
            if not record.name or len(record.name.strip()) == 0:
                raise ValidationError(_("File name cannot be empty."))
            
            if len(record.name) > 255:
                raise ValidationError(_("File name cannot exceed 255 characters."))
    
    def get_file_icon(self):
        """
        Get appropriate icon for file type
        """
        self.ensure_one()
        
        icon_mapping = {
            'application/pdf': 'fa-file-pdf-o',
            'application/msword': 'fa-file-word-o',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fa-file-word-o',
            'application/vnd.ms-excel': 'fa-file-excel-o',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'fa-file-excel-o',
            'text/plain': 'fa-file-text-o',
            'image/jpeg': 'fa-file-image-o',
            'image/png': 'fa-file-image-o',
            'image/gif': 'fa-file-image-o',
            'application/zip': 'fa-file-archive-o',
            'application/x-rar-compressed': 'fa-file-archive-o',
        }
        
        return icon_mapping.get(self.file_type, 'fa-file-o')
    
    def get_human_readable_size(self):
        """
        Get human readable file size
        """
        self.ensure_one()
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
