from odoo import fields, api, models


class BankDetails(models.Model):
    _name = "bank.detail"
    _description = "Bank Details"

    name = fields.Char("Name")
    bank_details = fields.Text("Bank Details")
