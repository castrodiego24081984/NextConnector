from odoo import fields, models


class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'

    nxt_id_erp = fields.Char('Código ERP')