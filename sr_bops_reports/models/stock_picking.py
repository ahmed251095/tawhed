from odoo import fields, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_consumption = fields.Boolean("Is Consumption")
