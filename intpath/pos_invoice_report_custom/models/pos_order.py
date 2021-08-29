# -*- coding: utf-8 -*-
import logging
import pytz
import psycopg2

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class PosInvoiceReport(models.AbstractModel):
    _name = 'report.pos_invoice_report_custom.report_invoice_custom'
    _description = 'Point of Sale Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print ("1111111111111111")
        PosOrder = self.env['pos.order']
        ids_to_print = []
        invoiced_posorders_ids = []
        selected_orders = PosOrder.browse(docids)
        for order in selected_orders.filtered(lambda o: o.account_report):
            ids_to_print.append(order.account_report.id)
            invoiced_posorders_ids.append(order.id)
        not_invoiced_orders_ids = list(set(docids) - set(invoiced_posorders_ids))
        if not_invoiced_orders_ids:
            not_invoiced_posorders = PosOrder.browse(not_invoiced_orders_ids)
            not_invoiced_orders_names = [a.name for a in not_invoiced_posorders]
            raise UserError(_('No link to an invoice for %s.') % ', '.join(not_invoiced_orders_names))
        return {'docs': self.env['invoice.report'].sudo().browse(ids_to_print)}


class PosOrder(models.Model):
    _inherit = "pos.order"

    account_report = fields.Many2one('invoice.report', string='Invoice', readonly=True, copy=False)

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns number pos_order id
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice_custom()

        return pos_order.id
    
    def _prepare_invoice_line_custom(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'price_subtotal': order_line.price_subtotal,
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom_id.id
        }


    def _prepare_invoice_vals_custom(self):
        self.ensure_one()
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')

        vals = {
            'invoice_payment_ref': self.name,
            'invoice_origin': self.name,
            'type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
            'ref': self.name,
            'name': self.pos_reference,
            'partner_id': self.partner_id.id,
            'narration': self.note or '',
            'company_id': self.company_id and self.company_id.id or False,
            'currency_id': self.pricelist_id.currency_id.id,
            'invoice_user_id': self.user_id.id,
            'invoice_date': self.date_order.astimezone(timezone).date(),
            'amount_total': self.amount_total,
            'amount_untaxed': self.amount_total,
            'journal_id': self.session_id.config_id.invoice_journal_id.id or False,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line_custom(line)) for line in self.lines],
        }
        return vals

    def action_pos_order_invoice_custom(self):
        moves = self.env['invoice.report']
        for order in self:
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            move_vals = order._prepare_invoice_vals_custom()
            new_move = moves.sudo()\
                            .with_context(default_type=move_vals['type'], force_company=order.company_id.id)\
                            .create(move_vals)
            order.write({'account_report': new_move.id, 'state': 'invoiced'})
            new_move.sudo().with_context(force_company=order.company_id.id)
            moves += new_move

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'res_model': 'invoice.report',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }
