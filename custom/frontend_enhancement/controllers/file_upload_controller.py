# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import base64
import json
import logging

_logger = logging.getLogger(__name__)


class FileUploadController(http.Controller):
    """
    Controller for handling file upload operations
    """
    
    @http.route('/web/file_upload/validate', type='json', auth='user', methods=['POST'])
    def validate_file_upload(self, **kw):
        """
        Validate file before upload
        """
        try:
            file_name = kw.get('file_name', '')
            file_size = kw.get('file_size', 0)
            file_type = kw.get('file_type', '')
            
            user = request.env.user
            
            # Validate file size
            max_size = user.max_upload_size * 1024 * 1024  # Convert MB to bytes
            if file_size > max_size:
                return {
                    'success': False,
                    'error': _("File size (%s MB) exceeds the maximum allowed size of %d MB.") % (
                        round(file_size / (1024 * 1024), 2), user.max_upload_size
                    )
                }
            
            # Validate file type
            if user.allowed_file_types:
                import os
                file_ext = os.path.splitext(file_name)[1].lower()
                allowed_types = [ext.strip() for ext in user.allowed_file_types.split(',')]
                if file_ext not in allowed_types:
                    return {
                        'success': False,
                        'error': _("File type '%s' is not allowed. Allowed types: %s") % (
                            file_ext, user.allowed_file_types
                        )
                    }
            
            return {
                'success': True,
                'message': _("File validation passed.")
            }
            
        except Exception as e:
            _logger.error("File validation error: %s", str(e))
            return {
                'success': False,
                'error': _("File validation failed: %s") % str(e)
            }
    
    @http.route('/web/file_upload/create', type='json', auth='user', methods=['POST'])
    def create_file_attachment(self, **kw):
        """
        Create file attachment via AJAX
        """
        try:
            # Get form data
            file_data = kw.get('file_data', '')
            name = kw.get('name', '').strip()
            description = kw.get('description', '').strip()
            access_level = kw.get('access_level', 'internal')
            related_model = kw.get('related_model', 'res.users')
            related_record_id = kw.get('related_record_id', request.env.user.id)
            
            # Validation
            if not file_data:
                raise ValueError(_("No file data provided."))
            
            if not name:
                raise ValueError(_("File name is required."))
            
            # Create attachment
            attachment = request.env['file.attachment.enhancement'].create({
                'name': name,
                'description': description,
                'file_data': file_data,
                'access_level': access_level,
                'user_id': request.env.user.id,
                'related_model': related_model,
                'related_record_id': related_record_id,
            })
            
            # Add to user's attachments if it's a user file
            if related_model == 'res.users' and related_record_id == request.env.user.id:
                request.env.user.attachment_ids = [(4, attachment.id)]
            
            return {
                'success': True,
                'message': _("File uploaded successfully."),
                'attachment_id': attachment.id,
                'attachment_data': {
                    'id': attachment.id,
                    'name': attachment.name,
                    'description': attachment.description,
                    'file_size': attachment.file_size,
                    'file_type': attachment.file_type,
                    'upload_date': attachment.upload_date.isoformat(),
                    'download_count': attachment.download_count,
                    'access_level': attachment.access_level,
                }
            }
            
        except Exception as e:
            _logger.error("File upload creation error: %s", str(e))
            return {
                'success': False,
                'error': _("File upload failed: %s") % str(e)
            }
    
    @http.route('/web/file_upload/bulk_upload', type='json', auth='user', methods=['POST'])
    def bulk_file_upload(self, **kw):
        """
        Handle bulk file upload
        """
        try:
            files_data = kw.get('files', [])
            related_model = kw.get('related_model', 'res.users')
            related_record_id = kw.get('related_record_id', request.env.user.id)
            
            if not files_data:
                raise ValueError(_("No files provided for upload."))
            
            successful_uploads = []
            failed_uploads = []
            
            for file_info in files_data:
                try:
                    # Create individual attachment
                    attachment = request.env['file.attachment.enhancement'].create({
                        'name': file_info.get('name', ''),
                        'description': file_info.get('description', ''),
                        'file_data': file_info.get('file_data', ''),
                        'access_level': file_info.get('access_level', 'internal'),
                        'user_id': request.env.user.id,
                        'related_model': related_model,
                        'related_record_id': related_record_id,
                    })
                    
                    successful_uploads.append({
                        'name': attachment.name,
                        'id': attachment.id,
                        'size': attachment.file_size,
                    })
                    
                except Exception as file_error:
                    failed_uploads.append({
                        'name': file_info.get('name', 'Unknown'),
                        'error': str(file_error),
                    })
            
            return {
                'success': len(failed_uploads) == 0,
                'message': _("Uploaded %d files successfully. %d files failed.") % (
                    len(successful_uploads), len(failed_uploads)
                ),
                'successful_uploads': successful_uploads,
                'failed_uploads': failed_uploads,
                'total_uploaded': len(successful_uploads),
                'total_failed': len(failed_uploads),
            }
            
        except Exception as e:
            _logger.error("Bulk file upload error: %s", str(e))
            return {
                'success': False,
                'error': _("Bulk upload failed: %s") % str(e)
            }
    
    @http.route('/web/file_upload/get_user_stats', type='json', auth='user', methods=['POST'])
    def get_user_upload_stats(self, **kw):
        """
        Get user's file upload statistics
        """
        try:
            user = request.env.user
            stats = user.get_upload_statistics()
            
            return {
                'success': True,
                'stats': {
                    'total_files': stats['total_files'],
                    'total_size': stats['total_size'],
                    'total_downloads': stats['total_downloads'],
                    'average_size': stats['average_size'],
                    'max_upload_size': user.max_upload_size * 1024 * 1024,  # Convert to bytes
                    'allowed_file_types': user.get_allowed_file_types_list(),
                    'recent_uploads': [{
                        'id': f.id,
                        'name': f.name,
                        'size': f.file_size,
                        'upload_date': f.upload_date.isoformat(),
                        'download_count': f.download_count,
                    } for f in stats['recent_uploads']],
                }
            }
            
        except Exception as e:
            _logger.error("Error getting user upload stats: %s", str(e))
            return {
                'success': False,
                'error': _("Failed to get upload statistics: %s") % str(e)
            }
    
    @http.route('/web/file_upload/delete', type='json', auth='user', methods=['POST'])
    def delete_file_attachment(self, **kw):
        """
        Delete file attachment via AJAX
        """
        try:
            attachment_id = kw.get('attachment_id')
            permanent = kw.get('permanent', False)
            
            if not attachment_id:
                raise ValueError(_("Attachment ID is required."))
            
            # Get attachment
            attachment = request.env['file.attachment.enhancement'].search([
                ('id', '=', attachment_id),
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not attachment:
                raise ValueError(_("File not found or you don't have permission to delete it."))
            
            file_name = attachment.name
            
            if permanent and request.env.user.has_group('base.group_system'):
                # Permanent deletion (admin only)
                attachment.unlink()
                message = _("File '%s' has been permanently deleted.") % file_name
            else:
                # Soft deletion
                attachment.is_active = False
                message = _("File '%s' has been archived.") % file_name
            
            return {
                'success': True,
                'message': message,
                'attachment_id': attachment_id,
            }
            
        except Exception as e:
            _logger.error("File deletion error: %s", str(e))
            return {
                'success': False,
                'error': _("File deletion failed: %s") % str(e)
            }
    
    @http.route('/web/file_upload/restore', type='json', auth='user', methods=['POST'])
    def restore_file_attachment(self, **kw):
        """
        Restore archived file attachment
        """
        try:
            attachment_id = kw.get('attachment_id')
            
            if not attachment_id:
                raise ValueError(_("Attachment ID is required."))
            
            # Get attachment
            attachment = request.env['file.attachment.enhancement'].search([
                ('id', '=', attachment_id),
                ('user_id', '=', request.env.user.id),
                ('is_active', '=', False)
            ], limit=1)
            
            if not attachment:
                raise ValueError(_("Archived file not found or you don't have permission to restore it."))
            
            # Restore file
            attachment.is_active = True
            
            # Log restoration
            attachment.message_post(
                body=_("File restored by %s") % request.env.user.name,
                subject=_("File Restoration")
            )
            
            return {
                'success': True,
                'message': _("File '%s' has been restored.") % attachment.name,
                'attachment_id': attachment_id,
            }
            
        except Exception as e:
            _logger.error("File restoration error: %s", str(e))
            return {
                'success': False,
                'error': _("File restoration failed: %s") % str(e)
            }
    
    @http.route('/web/file_upload/search', type='json', auth='user', methods=['POST'])
    def search_file_attachments(self, **kw):
        """
        Search user's file attachments
        """
        try:
            search_term = kw.get('search_term', '').strip()
            file_type = kw.get('file_type', '')
            access_level = kw.get('access_level', '')
            active_only = kw.get('active_only', True)
            limit = kw.get('limit', 50)
            
            # Build domain
            domain = [('user_id', '=', request.env.user.id)]
            
            if active_only:
                domain.append(('is_active', '=', True))
            
            if search_term:
                domain.extend([
                    '|', 
                    ('name', 'ilike', search_term),
                    ('description', 'ilike', search_term)
                ])
            
            if file_type:
                domain.append(('file_type', 'ilike', file_type))
            
            if access_level:
                domain.append(('access_level', '=', access_level))
            
            # Search attachments
            attachments = request.env['file.attachment.enhancement'].search(
                domain, 
                limit=limit, 
                order='upload_date desc'
            )
            
            # Format results
            results = []
            for attachment in attachments:
                results.append({
                    'id': attachment.id,
                    'name': attachment.name,
                    'description': attachment.description or '',
                    'file_size': attachment.file_size,
                    'file_type': attachment.file_type,
                    'upload_date': attachment.upload_date.isoformat(),
                    'download_count': attachment.download_count,
                    'access_level': attachment.access_level,
                    'is_active': attachment.is_active,
                    'file_icon': attachment.get_file_icon(),
                    'human_size': attachment.get_human_readable_size(),
                })
            
            return {
                'success': True,
                'results': results,
                'total_found': len(results),
                'search_term': search_term,
            }
            
        except Exception as e:
            _logger.error("File search error: %s", str(e))
            return {
                'success': False,
                'error': _("File search failed: %s") % str(e)
            }
