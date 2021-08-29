# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class add_account_sale_order(models.Model):
#     _name = 'add_account_sale_order.add_account_sale_order'
#     _description = 'add_account_sale_order.add_account_sale_order'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

import json


class AccountMove(models.Model):

    _inherit = 'account.move'


    def get_payment_journal(self,json_info):
        if(json.loads(json_info)):
            dict_info = json.loads(json_info)
            journal_name = ''
            for index,content in enumerate(dict_info['content']):
                journal_name += content['journal_name']
                if index != len(dict_info):
                    journal_name+='\n'
            return str(journal_name)
        else:
            return 'None'