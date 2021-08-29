# -*- coding: utf-8 -*-
# from odoo import http


# class TrialBalanceBorders(http.Controller):
#     @http.route('/trial_balance_borders/trial_balance_borders/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/trial_balance_borders/trial_balance_borders/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('trial_balance_borders.listing', {
#             'root': '/trial_balance_borders/trial_balance_borders',
#             'objects': http.request.env['trial_balance_borders.trial_balance_borders'].search([]),
#         })

#     @http.route('/trial_balance_borders/trial_balance_borders/objects/<model("trial_balance_borders.trial_balance_borders"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('trial_balance_borders.object', {
#             'object': obj
#         })
