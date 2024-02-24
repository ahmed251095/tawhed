from odoo import api, fields, models

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    product_id = fields.Many2one('product.product', required=True, string='Product')
    account_id = fields.Many2one('account.account', required=True, string='Account')
    move_id = fields.Many2one('account.move', readonly=False, string='Entry', copy=False)
    tax_ids = fields.Many2many('account.tax', string='Tax')





    @api.onchange('state')
    def _onchange_state(self):
        for rec in self:
            if rec.state == 'done':
                invoice_line_list = []
                vals = (0, 0, {
                    'name': rec.product_id.display_name,
                    'product_id': rec.product_id.id,
                    'price_unit': rec.amount,
                    'account_id': rec.account_id.id,
                    'quantity': 1,
                    'tax_ids': rec.tax_ids.ids,
                })
                invoice_line_list.append(vals)
                invoice = rec.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'invoice_date': rec.date,
                    'ref': rec.description,
                    'invoice_user_id': rec.env.user.id,
                    'partner_id': rec.vendor_id.id,
                    'currency_id': rec.env.user.company_id.currency_id.id,
                    # 'journal_id': int(customer_journal_id),
                    'invoice_line_ids': invoice_line_list
                })
                rec.move_id = invoice.id






