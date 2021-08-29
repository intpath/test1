# -*- coding: utf-8 -*-
# from odoo import http


# class AddAccountSaleOrder(http.Controller):
#     @http.route('/add_account_sale_order/add_account_sale_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_account_sale_order/add_account_sale_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_account_sale_order.listing', {
#             'root': '/add_account_sale_order/add_account_sale_order',
#             'objects': http.request.env['add_account_sale_order.add_account_sale_order'].search([]),
#         })

#     @http.route('/add_account_sale_order/add_account_sale_order/objects/<model("add_account_sale_order.add_account_sale_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_account_sale_order.object', {
#             'object': obj
#         })
