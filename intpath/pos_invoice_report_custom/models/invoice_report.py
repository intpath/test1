# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_is_zero

from odoo.exceptions import UserError

from datetime import date
import json
import re
    
def log(string):
    string = str(string)
    log_file = open('/usr/lib/python3/dist-packages/odoo/c-addons/log.txt','a')
    log_file.write(string)
    
def calc_check_digits(number):
    """Calculate the extra digits that should be appended to the number to make it a valid number.
    Source: python-stdnum iso7064.mod_97_10.calc_check_digits
    """
    number_base10 = ''.join(str(int(x, 36)) for x in number)
    checksum = int(number_base10) % 97
    return '%02d' % ((98 - 100 * checksum) % 97)


class InvoiceReport(models.Model):
    _name = "invoice.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Journal Entries"
    _order = 'date desc, name desc, id desc'


    @api.model
    def _get_default_invoice_date(self):
        return fields.Date.context_today(self)

    # ==== Business fields ====
    name = fields.Char(string='Number', required=True, readonly=True, copy=False, default='/')
    date = fields.Date(string='Date', required=True, index=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today)
    ref = fields.Char(string='Reference', copy=False)
    narration = fields.Text(string='Terms and Conditions')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    type = fields.Selection(selection=[
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True, change_default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(string='Company Currency')
    currency_id = fields.Many2one('res.currency',
        states={'draft': [('readonly', False)]},
        string='Currency')
    line_ids = fields.One2many('invoice.report.line', 'move_id', string='Journal Items', copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string='Partner', change_default=True)

    # === Amount fields ===
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True,
        )
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
        )
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)
    amount_residual = fields.Monetary(string='Amount Due', store=True,
        )
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount Signed', store=True, readonly=True,
        currency_field='company_currency_id')
    amount_tax_signed = fields.Monetary(string='Tax Signed', store=True, readonly=True,
        currency_field='company_currency_id')
    amount_total_signed = fields.Monetary(string='Total Signed', store=True, readonly=True,
        currency_field='company_currency_id')
    amount_residual_signed = fields.Monetary(string='Amount Due Signed', store=True,
        currency_field='company_currency_id')
    invoice_user_id = fields.Many2one('res.users', copy=False, tracking=True,
        string='Salesperson',
        default=lambda self: self.env.user)
    user_id = fields.Many2one(string='User', related='invoice_user_id',
        help='Technical field used to fit the generic behavior in mail templates.')
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')],
        string='Payment', store=True, readonly=True, copy=False, tracking=True,
        )
    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]},
        default=_get_default_invoice_date)
    invoice_date_due = fields.Date(string='Due Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]})
    invoice_payment_ref = fields.Char(string='Payment Reference', index=True, copy=False,
        help="The payment reference to set on journal items.")
    invoice_sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the invoice has been sent.")
    invoice_origin = fields.Char(string='Origin', readonly=True, tracking=True,
        help="The document(s) that generated the invoice.")
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True, states={'draft': [('readonly', False)]})
    invoice_line_ids = fields.One2many('invoice.report.line', 'move_id', string='Invoice lines',
        copy=False, readonly=True,
        states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Journal')

    # payment_methode = fields.Char(compute="_get_payment_methode", string="Payment Methode")
    cash_journal_id = fields.Char(compute="_get_cash_journal_id", string="Cash Journal Id")

    # def _get_payment_methode(self):
    #     for rec in self:
    #         pos_order = self.env['pos.order'].search([('name', '=', rec.ref)])
    #         rec.payment_methode = pos_order.payment_ids[0].payment_method_id.name

    def _get_cash_journal_id(self):
        for rec in self:
            pos_order = self.env['pos.order'].search([('name', '=', rec.ref)])
            if(pos_order.payment_ids[0].payment_method_id.cash_journal_id.name):
                rec.cash_journal_id = pos_order.payment_ids[0].payment_method_id.cash_journal_id.name
            else:
                rec.cash_journal_id = None

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM invoice_report move
                    JOIN invoice_report_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN invoice_report_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM invoice_report move
                    JOIN invoice_report_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN invoice_report_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

    
    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('invoice.report')
    #     res = super(InvoiceReport, self).create(vals)
    #     return res

    def _get_reconciled_info_JSON_values(self):
        self.ensure_one()
        foreign_currency = self.currency_id if self.currency_id != self.company_id.currency_id else False

        reconciled_vals = []
        pay_term_line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        partials = pay_term_line_ids.mapped('matched_debit_ids') + pay_term_line_ids.mapped('matched_credit_ids')
        for partial in partials:
            counterpart_lines = partial.debit_move_id + partial.credit_move_id
            counterpart_line = counterpart_lines.filtered(lambda line: line not in self.line_ids)

            if foreign_currency and partial.currency_id == foreign_currency:
                amount = partial.amount_currency
            else:
                amount = partial.company_currency_id._convert(partial.amount, self.currency_id, self.company_id, self.date)

            if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                continue

            ref = counterpart_line.move_id.name
            if counterpart_line.move_id.ref:
                ref += ' (' + counterpart_line.move_id.ref + ')'

            reconciled_vals.append({
                'name': counterpart_line.name,
                'amount': amount,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'position': self.currency_id.position,
                'date': counterpart_line.date,
                'payment_id': counterpart_line.id,
                'account_payment_id': counterpart_line.payment_id.id,
                'payment_method_name': counterpart_line.payment_id.payment_method_id.name or None,
                'move_id': counterpart_line.move_id.id,
                'ref': ref,
            })
        return reconciled_vals



class AccountMoveLine(models.Model):
    _name = "invoice.report.line"
    _description = "Journal Item"
    _order = "date desc, move_name desc, id"
    _check_company_auto = True

    # ==== Business fields ====
    move_id = fields.Many2one('invoice.report', string='Journal Entry',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        help="The move of this entry line.")
    move_name = fields.Char(string='Number', related='move_id.name', store=True, index=True)
    date = fields.Date(related='move_id.date', store=True, readonly=True, index=True, copy=False, group_operator='min')
    ref = fields.Char(related='move_id.ref', store=True, copy=False, index=True, readonly=False)
    parent_state = fields.Selection(related='move_id.state', store=True, readonly=True)
    currency_id = fields.Many2one(related="move_id.currency_id", string='Currency', store=True, readonly=True)
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True)
    name = fields.Char(string='Label')
    quantity = fields.Float(string='Quantity',
        default=1.0, digits='Product Unit of Measure',
        help="The optional quantity expressed by this line, eg: number of product sold. "
             "The quantity is not a legal requirement but is very useful for some reports.")
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    amount_currency = fields.Monetary(string='Amount in Currency', store=True, copy=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")
    price_subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True,
        currency_field='currency_id')
    price_total = fields.Monetary(string='Total', store=True, readonly=True,
        currency_field='currency_id')
    
    date_maturity = fields.Date(string='Due Date', index=True,
        help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    product_id = fields.Many2one('product.product', string='Product')

    # ==== Tax fields ====
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount")
    tax_line_id = fields.Many2one('account.tax', string='Originator Tax', ondelete='restrict', store=True,
        compute='_compute_tax_line_id', help="Indicates that this journal item is a tax line")
    tax_group_id = fields.Many2one(related='tax_line_id.tax_group_id', string='Originator tax group',
        readonly=True, store=True,
        help='technical field for widget tax-group-custom-field')
    tax_base_amount = fields.Monetary(string="Base Amount", store=True, readonly=True,
        currency_field='currency_id')
    tax_exigible = fields.Boolean(string='Appears in VAT report', default=True, readonly=True,
        help="Technical field used to mark a tax line as exigible in the vat report or not (only exigible journal items"
             " are displayed). By default all new journal items are directly exigible, but with the feature cash_basis"
             " on taxes, some will become exigible only when the payment is recorded.")
    tax_repartition_line_id = fields.Many2one(comodel_name='account.tax.repartition.line',
        string="Originator Tax Repartition Line", ondelete='restrict', readonly=True,
        help="Tax repartition line that caused the creation of this move line, if any")
    tag_ids = fields.Many2many(string="Tags", comodel_name='account.account.tag', ondelete='restrict',
        help="Tags assigned to this line by the tax creating it, if any. It determines its impact on financial reports.")
    tax_audit = fields.Char(string="Tax Audit String", compute="_compute_tax_audit", store=True,
        help="Computed field, listing the tax grids impacted by this line, and the amount it applies to each of them.")

    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.")

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.partner_ref:
            values.append(product.partner_ref)
            if product.description_sale:
                values.append(product.description_sale)
        return '\n'.join(values)

