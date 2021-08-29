# -*- coding: utf-8 -*-

from odoo import _, api, fields, tools, models
from odoo.exceptions import UserError, AccessError
from odoo.tools import config


from odoo.tools import lazy
from odoo.sql_db import TestCursor
from collections import OrderedDict
import logging
from datetime import datetime



_logger = logging.getLogger(__name__)



class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def web_read_group(self, domain, fields, groupby, limit=None, offset=0, orderby=False,
                       lazy=True, expand=False, expand_limit=None, expand_orderby=False):
        if self._name == 'stock.move' and domain:
            from_date = ''
            to_date = ''
            for i in domain: 
                if len(i) == 3 and i[0] == 'date' and '>' in i[1]:
                    date = i[2].split(' ')[0]
                    from_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
                if len(i) == 3 and i[0] == 'date' and '<' in i[1]:
                    date = i[2].split(' ')[0]
                    to_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
            report = self.env['ir.actions.report'].search([('report_name', '=', 'stock_move_report_custom.report_stock_moves_custom')])
            report.sudo().write({'context': {'from_date':from_date, 'to_date':to_date}})
        return super(Base, self).web_read_group(domain, fields, groupby, limit=None, offset=0, orderby=False,
                       lazy=True, expand=False, expand_limit=None, expand_orderby=False)
