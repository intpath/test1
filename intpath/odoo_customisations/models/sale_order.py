# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('due', 'Due'),
        ], string='Payment Type')



class AccountMove(models.Model):
    _inherit = 'account.move'


    @api.model
    def create(self, vals):
        if self.env.user.has_group('inventory_validation.group_location_manager_it'):
            raise UserError (_("You don't have access to create invoice, Please contact your administrator."))
        res = super(AccountMove, self).create(vals)
        return res

    def write(self, vals):
        if self.env.user.has_group('inventory_validation.group_location_manager_it'):
            raise UserError (_("You don't have access to edit invoice, Please contact your administrator."))
        res = super(AccountMove, self).write(vals)
        return res
