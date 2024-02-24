from odoo import fields, api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    employee_id = fields.Many2one("hr.employee", string="Employee Id")
