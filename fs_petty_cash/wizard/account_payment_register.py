from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    cheque_date = fields.Date("Cheque Date")
    cheque_no = fields.Char("Cheque Number")
    mode_of_payment = fields.Selection(
        [("bank", "Bank"), ("cash", "Cash"), ("tt", "TT")], string="Mode Of Payment"
    )

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        payment_vals["cheque_date"] = self.cheque_date
        payment_vals["cheque_no"] = self.cheque_no
        payment_vals["mode_of_payment"] = self.mode_of_payment
        return payment_vals