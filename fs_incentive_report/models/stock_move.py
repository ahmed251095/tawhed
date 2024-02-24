from odoo import fields, api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_cost = fields.Float(string="Cost", compute="_compute_product_cost")

    def _compute_product_cost(self):
        for move in self:
            scraps = self.env["stock.scrap"].search(
                [("picking_id", "=", move.picking_id.id)]
            )
            valuation_ids = (move + scraps.move_id).stock_valuation_layer_ids.filtered(
                lambda v: v.product_id.id == move.product_id.id
            )
            move.product_cost = abs(sum(valuation_ids.mapped("value")))


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_cost = fields.Float(string="Cost", compute="_compute_product_cost")

    def _compute_product_cost(self):
        for line in self:
            scraps = self.env["stock.scrap"].search(
                [("picking_id", "=", line.picking_id.id)]
            )
            valuation_ids = (
                line.move_id + scraps.move_id
            ).stock_valuation_layer_ids.filtered(
                lambda v: v.product_id.id == line.product_id.id
            )
            line.product_cost = abs(sum(valuation_ids.mapped("value")))
