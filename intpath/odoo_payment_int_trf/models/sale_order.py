# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('due', 'Due'),
        ], string='Payment Type')



