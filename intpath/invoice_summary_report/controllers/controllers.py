# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceSummaryReport(http.Controller):
#     @http.route('/invoice_summary_report/invoice_summary_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_summary_report/invoice_summary_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_summary_report.listing', {
#             'root': '/invoice_summary_report/invoice_summary_report',
#             'objects': http.request.env['invoice_summary_report.invoice_summary_report'].search([]),
#         })

#     @http.route('/invoice_summary_report/invoice_summary_report/objects/<model("invoice_summary_report.invoice_summary_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_summary_report.object', {
#             'object': obj
#         })
