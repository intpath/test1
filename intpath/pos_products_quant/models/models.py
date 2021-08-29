# -*- coding: utf-8 -*-

from odoo import models, fields, api


class posProductsQuant(models.Model):
    _name = 'product.quant'
    _description = 'product.quant'


    @api.model
    def get_product_quant(self,product_id,session_id):

        config_id = self.env['pos.session'].search([('id','=',session_id)]).config_id
        location_id = config_id.picking_type_id.default_location_src_id
        product_quantity = self.env['stock.quant'].search([('product_id','=',product_id),('location_id','=',location_id.id)]).quantity

        return str(int(product_quantity))
