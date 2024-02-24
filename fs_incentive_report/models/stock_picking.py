from odoo import fields, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_valuation_cost = fields.Float(
        "Total Valuation Cost", compute="_compute_total_valuation_cost"
    )

    def _compute_total_valuation_cost(self):
        for picking in self:
            picking.total_valuation_cost = abs(
                sum(picking.move_ids_without_package.mapped("product_cost"))
            )
