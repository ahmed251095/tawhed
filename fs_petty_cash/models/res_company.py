from odoo import fields, api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    trn_number = fields.Char("TRN")
