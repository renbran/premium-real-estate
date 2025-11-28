# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import logging

_logger = logging.getLogger(__name__)


class PortalController(CustomerPortal):
    """
    Extended portal controller for file management
    """
    
    def _prepare_home_portal_values(self, counters):
        """
        Add file attachment counts to portal home
        """
        values = super()._prepare_home_portal_values(counters)
        
        if 'file_count' in counters:
            file_count = request.env['file.attachment.enhancement'].search_count([
                ('user_id', '=', request.env.user.id),
                ('is_active', '=', True)
            ])
            values['file_count'] = file_count
            
        return values
    
    @http.route(['/my/files', '/my/files/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_files(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='name', **kw):
        """
        Display user's file attachments in portal
        """
        values = self._prepare_portal_layout_values()
        
        # Domain for user's active files
        domain = [
            ('user_id', '=', request.env.user.id),
            ('is_active', '=', True)
        ]
        
        # Search functionality
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in File Name')},
            'description': {'input': 'description', 'label': _('Search in Description')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        if search and search_in:
            if search_in == 'name':
                domain += [('name', 'ilike', search)]
            elif search_in == 'description':
                domain += [('description', 'ilike', search)]
            elif search_in == 'all':
                domain += ['|', ('name', 'ilike', search), ('description', 'ilike', search)]
        
        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Upload Date'), 'order': 'upload_date desc'},
            'name': {'label': _('File Name'), 'order': 'name'},
            'size': {'label': _('File Size'), 'order': 'file_size desc'},
            'downloads': {'label': _('Downloads'), 'order': 'download_count desc'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # Get files
        files = request.env['file.attachment.enhancement'].search(domain, order=order)
        
        values.update({
            'files': files,
            'page_name': 'my_files',
            'default_url': '/my/files',
            'searchbar_inputs': searchbar_inputs,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        
        return request.render("frontend_enhancement.portal_my_files", values)
    
    @http.route(['/my/files/upload'], type='http', auth="user", website=True, csrf=False)
    def portal_file_upload(self, **kw):
        """
        File upload page
        """
        if request.httprequest.method == 'POST':
            return self._handle_file_upload(**kw)
        
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'file_upload',
        })
        
        return request.render("frontend_enhancement.portal_file_upload", values)
    
    def _handle_file_upload(self, **kw):
        """
        Handle file upload POST request
        """
        try:
            # Get form data
            file_data = kw.get('file_data')
            name = kw.get('name', '').strip()
            description = kw.get('description', '').strip()
            access_level = kw.get('access_level', 'internal')
            
            # Validation
            if not file_data or not hasattr(file_data, 'read'):
                raise ValueError(_("No file was uploaded."))
            
            if not name:
                raise ValueError(_("File name is required."))
            
            # Read file content
            file_content = file_data.read()
            if not file_content:
                raise ValueError(_("Uploaded file is empty."))
            
            # Encode file content
            file_data_encoded = base64.b64encode(file_content)
            
            # Create attachment
            attachment = request.env['file.attachment.enhancement'].create({
                'name': name,
                'description': description,
                'file_data': file_data_encoded,
                'access_level': access_level,
                'user_id': request.env.user.id,
                'related_model': 'res.users',
                'related_record_id': request.env.user.id,
            })
            
            # Add to user's attachments
            request.env.user.attachment_ids = [(4, attachment.id)]
            
            # Success response
            return request.render("frontend_enhancement.portal_file_upload_success", {
                'attachment': attachment,
            })
            
        except Exception as e:
            _logger.error("File upload error: %s", str(e))
            
            values = self._prepare_portal_layout_values()
            values.update({
                'page_name': 'file_upload',
                'error_message': str(e),
            })
            
            return request.render("frontend_enhancement.portal_file_upload", values)
    
    @http.route(['/my/files/download/<int:attachment_id>'], type='http', auth="user", website=True)
    def portal_file_download(self, attachment_id, **kw):
        """
        Download file attachment
        """
        try:
            # Get attachment
            attachment = request.env['file.attachment.enhancement'].search([
                ('id', '=', attachment_id),
                ('user_id', '=', request.env.user.id),
                ('is_active', '=', True)
            ], limit=1)
            
            if not attachment:
                return request.not_found()
            
            # Check access level
            if attachment.access_level == 'restricted':
                # Add additional access checks if needed
                pass
            
            # Increment download count
            attachment.download_count += 1
            
            # Log download
            attachment.message_post(
                body=_("File downloaded from portal by %s") % request.env.user.name,
                subject=_("Portal Download")
            )
            
            # Return file
            file_content = base64.b64decode(attachment.file_data)
            
            response = request.make_response(
                file_content,
                headers=[
                    ('Content-Type', attachment.file_type or 'application/octet-stream'),
                    ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
                    ('Content-Length', len(file_content)),
                ]
            )
            
            return response
            
        except Exception as e:
            _logger.error("File download error: %s", str(e))
            return request.not_found()
    
    @http.route(['/my/files/delete/<int:attachment_id>'], type='http', auth="user", website=True, csrf=False)
    def portal_file_delete(self, attachment_id, **kw):
        """
        Soft delete file attachment
        """
        try:
            # Get attachment
            attachment = request.env['file.attachment.enhancement'].search([
                ('id', '=', attachment_id),
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not attachment:
                return request.redirect('/my/files?error=file_not_found')
            
            # Soft delete (mark as inactive)
            attachment.is_active = False
            
            # Log deletion
            attachment.message_post(
                body=_("File deleted from portal by %s") % request.env.user.name,
                subject=_("Portal Deletion")
            )
            
            return request.redirect('/my/files?success=file_deleted')
            
        except Exception as e:
            _logger.error("File deletion error: %s", str(e))
            return request.redirect('/my/files?error=delete_failed')
    
    @http.route(['/my/account'], type='http', auth="user", website=True)
    def account(self, **kw):
        """
        Override account page to include file upload statistics
        """
        response = super().account(**kw)
        
        # Add file statistics to context
        if hasattr(response, 'qcontext'):
            user = request.env.user
            file_stats = user.get_upload_statistics()
            response.qcontext.update({
                'file_stats': file_stats,
            })
        
        return response
