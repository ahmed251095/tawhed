from odoo import fields, models, api, _

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_apply_inventory(self):
        products_tracked_without_lot = []
        for quant in self:
            rounding = quant.product_uom_id.rounding
            if fields.Float.is_zero(quant.inventory_diff_quantity, precision_rounding=rounding)\
                    and fields.Float.is_zero(quant.inventory_quantity, precision_rounding=rounding)\
                    and fields.Float.is_zero(quant.quantity, precision_rounding=rounding):
                continue
            if quant.product_id.tracking in ['lot', 'serial'] and\
                    not quant.lot_id and quant.inventory_quantity != quant.quantity:
                products_tracked_without_lot.append(quant.product_id.id)
        # for some reason if multi-record, env.context doesn't pass to wizards...
        ctx = dict(self.env.context or {})
        ctx['default_quant_ids'] = self.ids
        quants_outdated = self.filtered(lambda quant: quant.is_outdated)
        # if quants_outdated:
        #     ctx['default_quant_to_fix_ids'] = quants_outdated.ids
        #     return {
        #         'name': _('Conflict in Inventory Adjustment'),
        #         'type': 'ir.actions.act_window',
        #         'view_mode': 'form',
        #         'views': [(False, 'form')],
        #         'res_model': 'stock.inventory.conflict',
        #         'target': 'new',
        #         'context': ctx,
        #     }
        if products_tracked_without_lot:
            ctx['default_product_ids'] = products_tracked_without_lot
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'context': ctx,
            }
        self._apply_inventory()
        self.inventory_quantity_set = False

    inventory_diff_quantity = fields.Float(
        'Difference', compute='_compute_inventory_diff_quantity', store=True,
        help="Indicates the gap between the product's theoretical quantity and its counted quantity.",
        readonly=True, digits='Product Unit of Measure')
    # inventory_diff_quantity_new = fields.Float(
    #     'New Difference', compute='_compute_inventory_diff_new_quantity', store=True,
    #     help="Indicates the gap between the product's theoretical quantity and its counted quantity.",
    #     readonly=True, digits='Product Unit of Measure')
    # new_quantity = fields.Float(
    #     'Difference New', compute='_compute_inventory_diff_new_quantity', store=True,
    #     help="Indicates the gap between the product's theoretical quantity and its counted quantity.",
    #     readonly=True, digits='Product Unit of Measure')
    # @api.depends('inventory_quantity','product_uom_id_adj')
    # def _compute_inventory_diff_new_quantity(self):
    #     for quant in self:
    #         quant.inventory_diff_quantity_new = quant.product_uom_id_adj._compute_quantity(quant.inventory_quantity,
    #                                                                                        quant.product_uom_id)

    @api.depends('quantity','product_uom_id_adj')
    def _compute_inventory_diff_quantity(self):
        for quant in self:
            if quant.product_uom_id_adj:
                quant.inventory_diff_quantity = quant.product_uom_id_adj._compute_quantity(quant.inventory_quantity, quant.product_uom_id)-quant.quantity
            else:
                quant.inventory_diff_quantity = quant.inventory_quantity - quant.quantity






    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        fields = ['product_uom_id_adj','inventory_quantity', 'inventory_quantity_auto_apply', 'inventory_diff_quantity',
                  'inventory_date', 'user_id', 'inventory_quantity_set', 'is_outdated']
        return fields
    #
    product_uom_id_adj = fields.Many2one('uom.uom', string='UOM For Adjustment')

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):

        self.ensure_one()
        if fields.Float.is_zero(qty, 0, precision_rounding=self.product_uom_id.rounding):
            name = _('Product Quantity Confirmed')
        else:
            name = _('Product Quantity Updated')


        return {
            'name': self.env.context.get('inventory_name') or name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            # 'product_uom': self.product_uom_id_adj.id,
            'product_uom_qty': qty,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'is_inventory': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                # 'product_uom_id': self.product_uom_id_adj.id,
                'qty_done': qty,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': self.lot_id.id,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'owner_id': self.owner_id.id,
            })]
        }
