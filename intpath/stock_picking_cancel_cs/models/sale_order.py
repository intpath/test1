from odoo import api, fields, models,exceptions
class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        self.picking_ids.with_context({'Flag':True}).action_cancel()
        res = super(SaleOrder, self).action_cancel()
        return res