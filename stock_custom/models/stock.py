from odoo import api, fields, models
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError



class StockMoveline(models.Model):
    _inherit = 'stock.move.line'
    is_bouns = fields.Boolean('Bouns ? ')
    picking_partner_id = fields.Many2one(related='picking_id.partner_id', readonly=True,store=True)

    origin = fields.Char(related='move_id.origin', string='Source',store=True)
