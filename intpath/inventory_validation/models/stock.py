# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Allow Locations')
    stock_location_ids = fields.Many2many('stock.location', string='Stock Locations')

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_picking_sent = fields.Integer(compute='_compute_picking_count')
    count_picking_receive = fields.Integer(compute='_compute_picking_count')

    def _compute_picking_count(self):
        # TDE TODO count picking can be done using previous two
        domains = {
            'count_picking_draft': [('state', '=', 'draft')],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': [('state', '=', 'assigned')],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': [('scheduled_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
            'count_picking_sent': [('state', '=', 'draft'), ('picking_type_code', '=', 'internal')],
            'count_picking_receive': [('state', '=', 'sent'), ('picking_type_code', '=', 'internal')],
        }
        for field in domains:
            data = self.env['stock.picking'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)
        for record in self:
            record.rate_picking_late = record.count_picking and record.count_picking_late * 100 / record.count_picking or 0
            record.rate_picking_backorders = record.count_picking and record.count_picking_backorders * 100 / record.count_picking or 0
    
    def get_action_picking_tree_to_send(self):
        return self._get_action('inventory_validation.action_picking_tree_sent_custom')
    
    def get_action_picking_tree_to_receive(self):
        return self._get_action('inventory_validation.action_picking_tree_receive_custom')


class Picking(models.Model):
    _inherit = "stock.picking"

    # Un comment this if want to edit on custom stage
    # @api.depends('state', 'picking_id', 'product_id')
    # def _compute_is_quantity_done_editable(self):
    #     for move in self:
    #         if not move.product_id:
    #             move.is_quantity_done_editable = False
    #         elif not move.picking_id.immediate_transfer and move.picking_id.state == 'draft':
    #             move.is_quantity_done_editable = False
    #         elif move.picking_id.is_locked and move.state in ('done', 'cancel'):
    #             move.is_quantity_done_editable = False
    #         elif move.show_details_visible:
    #             move.is_quantity_done_editable = False
    #         elif move.show_operations:
    #             move.is_quantity_done_editable = False
    #         else:
    #             move.is_quantity_done_editable = True

    @api.depends('state', 'is_locked')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned', 'receive') or not picking.is_locked:
                picking.show_validate = False
            elif picking.state in ('draft', 'assigned') and picking.picking_type_code == 'internal':
                picking.show_validate = False
            else:
                picking.show_validate = True

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('sent', 'Sent'),
        ('receive', 'Receive'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    def button_validate(self):
        if self.env.user.has_group('inventory_validation.group_location_manager_it') and not self.env.user.has_group('stock.group_stock_manager'):
            if self.state == 'receive' and self.location_dest_id.id not in self.env.user.stock_location_ids.ids:
                raise ValidationError('Only users who has access on (%s) are allowed to ....' % self.location_dest_id.name)
        result = super(Picking, self).button_validate()
        return result

    def button_sent(self):
        warehouse = self.location_dest_id.get_warehouse()
        new_picking_type = False
        if warehouse:
            new_picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', warehouse.id)], limit=1)
        if self.env.user.has_group('inventory_validation.group_location_manager_it') and not self.env.user.has_group('stock.group_stock_manager'):
            if self.state in ['draft', 'assigned'] and self.location_id.id not in self.env.user.stock_location_ids.ids:
                raise ValidationError('Only users who has access on (%s) are allowed to ....' % self.location_id.name)
            else:
                if new_picking_type:
                    return self.write({'state': 'sent', 'picking_type_id': new_picking_type.id})
                else:
                    return self.write({'state': 'sent'})
        if self.env.user.has_group('stock.group_stock_manager'):
            if new_picking_type:
                return self.write({'state': 'sent', 'picking_type_id': new_picking_type.id})
            else:
                return self.write({'state': 'sent'})


    def button_receive(self):
        if self.env.user.has_group('inventory_validation.group_location_manager_it') and not self.env.user.has_group('stock.group_stock_manager'):
            if self.state == 'sent' and self.location_dest_id.id not in self.env.user.stock_location_ids.ids:
                raise ValidationError('Only users who has access on (%s) are allowed to ....' % self.location_dest_id.name)
            else:
                return self.write({'state': 'receive'})
        if self.env.user.has_group('stock.group_stock_manager'):
            return self.write({'state': 'receive'})
    
    def get_invoice_list(self):
        if self.picking_type_code == 'outgoing' and self.origin:
            sale_id = self.env['sale.order'].search([('name', '=', self.origin)])
            if sale_id and sale_id.invoice_ids:
                return ','.join(a.name for a in sale_id.invoice_ids)
            else:
                return ''
        elif self.picking_type_code == 'incoming' and self.origin:
            purchase_id = self.env['purchase.order'].search([('name', '=', self.origin)])
            if purchase_id and purchase_id.invoice_ids:
                return ','.join(a.name for a in purchase_id.invoice_ids)
            else:
                return ''
        else:
            return ''
    
    # def write(self, vals):
    #     if self.env.user.has_group('inventory_validation.group_location_manager_it'):
    #         if vals.get('picking_type_id') or vals.get('location_id') or vals.get('location_dest_id'):
    #             raise UserError(_("You don't have access to change this record."))
    #     res = super(Picking, self).write(vals)
    #     return res




# class StockMoveLine(models.Model):
#     _inherit = "stock.move.line"

#     def write(self, vals):
#         if self.env.user.has_group('inventory_validation.group_location_manager_it'):
#             if len(vals) != 1:
#                 raise UserError(_("You don't have access to change this record."))
#             if not vals.get("qty_done"):
#                 raise UserError(_("You don't have access to change this record."))
#         res = super(StockMoveLine, self).write(vals)
#         return res



# class StockMove(models.Model):
#     _inherit = "stock.move"

#     def write(self, vals):
#         if self.env.user.has_group('inventory_validation.group_location_manager_it'):
#             if len(vals) != 1:
#                 raise UserError(_("You don't have access to change this record."))
#             if not vals.get("quantity_done"):
#                 raise UserError(_("You don't have access to change this record."))
#         res = super(StockMove, self).write(vals)
#         return res