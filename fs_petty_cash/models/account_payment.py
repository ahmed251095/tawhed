from odoo import fields, api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    cheque_date = fields.Date("Cheque Date")
    cheque_no = fields.Char("Cheque Number")
    mode_of_payment = fields.Selection(
        [("bank", "Bank"), ("cash", "Cash"), ("tt", "TT")], string="Mode Of Payment"
    )
    project_id = fields.Many2one("project.project", string="Job Reference")
