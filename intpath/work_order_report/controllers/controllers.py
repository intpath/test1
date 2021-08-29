# -*- coding: utf-8 -*-
# from odoo import http


# class WorkOrderReport(http.Controller):
#     @http.route('/work_order_report/work_order_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/work_order_report/work_order_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('work_order_report.listing', {
#             'root': '/work_order_report/work_order_report',
#             'objects': http.request.env['work_order_report.work_order_report'].search([]),
#         })

#     @http.route('/work_order_report/work_order_report/objects/<model("work_order_report.work_order_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('work_order_report.object', {
#             'object': obj
#         })
