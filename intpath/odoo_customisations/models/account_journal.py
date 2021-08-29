# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_user = fields.Many2one('res.groups', string="Journal User")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    state = fields.Selection([
        ('draft', 'Draft'), 
        ('send', 'Send'), 
        # ('receive', 'Received'),
        ('posted', 'Validated'),
        ('sent', 'Sent'), 
        ('reconciled', 'Reconciled'), 
        ('cancelled', 'Cancelled')], readonly=True, default='draft',
        copy=False, string="Status")

    def button_sent(self):
        if self.env.user.id in self.journal_id.journal_user.users.ids:
            return self.write({'state': 'send'})
        else:
            raise ValidationError('Only users who has access on (%s) are allowed to ....' % self.journal_id.name)

    def button_receive(self):
        if self.env.user.id in self.journal_id.journal_user.users.ids:
            return self.post()
        else:
            raise ValidationError('Only users who has access on (%s) are allowed to ....' % self.journal_id.name)

    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:

            # if rec.state != 'draft':
            #     raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id)\
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids')\
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
                    .reconcile()
                if self.journal_id.type in ['bank', 'cash'] and self.journal_id.journal_user:
                    partner_ids = self.journal_id.journal_user.users.mapped(
                        'partner_id.id')
                    mail_body = _('The transfer %s is approved by %s !!') % (self.name, self.env.user.name)
                    mail = self.env['mail.mail'].create({
                        'subject': _('%s Journal (Ref %s )') % (self.company_id.name, self.name or 'n/a'),
                        'email_from': self.env.company.email,
                        'recipient_ids': [(6, 0, partner_ids)],
                        'body_html': mail_body,
                    })
                    mail.send()
        return True




class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.journal_id.type in ['bank', 'cash'] and self.journal_id.journal_user:
            partner_ids = self.journal_id.journal_user.users.mapped(
                'partner_id.id')
            mail_body = _('Cash entry "%s" has been posted!') % (self.name,)
            mail = self.env['mail.mail'].create({
                'subject': _('%s Journal (Ref %s )') % (self.company_id.name, self.name or 'n/a'),
                'email_from': self.env.company.email,
                'recipient_ids': [(6, 0, partner_ids)],
                'body_html': mail_body,
            })
            mail.send()
