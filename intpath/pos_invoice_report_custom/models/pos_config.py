# coding: utf-8

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    auto_invoice_print = fields.Boolean('Auto Print Invoice', help='Default Invoice button selected.')
