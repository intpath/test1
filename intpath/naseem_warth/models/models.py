# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NW_accountMove(models.Model):
    _inherit="account.move"
  
    # fields requested on print
    from_location_id = fields.Many2one("stock.location" ,string="Product Source", compute="cal_from_location")
    journal_type= fields.Char(string="Journal", default="")
    

    @api.depends('invoice_origin')
    def cal_from_location(self):
        for rec in self:
            if rec.invoice_origin:
                delivery_rec = self.env['stock.picking'].search([('group_id','=', rec.invoice_origin)], limit=1)

                if delivery_rec:
                    _location = delivery_rec.move_line_ids_without_package.location_id
                    rec.from_location_id = _location.id
                    return
    
            rec.from_location_id = False

    # to rest the journal_type field in case the invoice is reset to draft
    def button_draft(self):
        rec = super(NW_accountMove, self).button_draft()
        self.journal_type = ""

class NW_accountPayment(models.Model):
    _inherit = "account.payment"

    # to pass the journal type from account.payment to account.move
    def post(self):

        rec = super(NW_accountPayment, self).post()

        _invoice = self.invoice_ids
        _invoice.write({
            'journal_type': self.journal_id.name
        })

        return rec

class NW_PointofSale(models.Model):
    _inherit="pos.order"
    status = fields.Char(string=" PoS Order Status")




    def refund(self):
        self.status = "returned"
        res =super(NW_PointofSale,self).refund()
        return res
