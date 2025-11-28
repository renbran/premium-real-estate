# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    """
        Inherits from 'account.move' to customize behavior or add additional fields.
    """
    _inherit = 'account.move'

    is_split_invoice = fields.Boolean(string="Is Split Invoice", default=False)
