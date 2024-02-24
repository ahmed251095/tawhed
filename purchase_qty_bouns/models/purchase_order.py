from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'



class AccountMoveline(models.Model):
    _inherit = 'account.move.line'
    qty = fields.Float(string='Quantity', default=1,digits=dp.get_precision('Product Unit of Measure'), required=True)
    bouns_qty = fields.Float(string='Bouns Quantity', digits=dp.get_precision('Product Unit of Measure'), )
    quantity = fields.Float(string='Total Quantity', digits=dp.get_precision('Product Unit of Measure'),
            required=True, default=1)



    @api.onchange('bouns_qty', 'qty')
    def onchange_qtyss(self):
        self.quantity = self.qty + self.bouns_qty

    @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
        'product_id', 'move_id.partner_id', 'move_id.currency_id', 'move_id.company_id',
        'move_id.invoice_date', 'move_id.date')
    def _compute_price(self):
        if self.move_id.move_type in ['in_invoice', 'in_refund']:
            qt = self.qty
        else:
            qt = self.quantity

        currency = self.move and self.move_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.tax_ids:
            taxes = self.tax_ids.compute_all(price, currency, qt, product=self.product_id, partner=self.move_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else (self.qty) * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.move_id.currency_id and self.move_id.currency_id != self.move_id.company_id.currency_id:
            currency = self.move_id.currency_id
            date = self.move_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.move_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
        sign = self.move_id.move_type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    #
    # def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
    #     self.ensure_one()
    #     return self._get_price_total_and_subtotal_model(
    #         price_unit=self.price_unit if price_unit is None else price_unit,
    #         quantity=self.qty if quantity is None else quantity,
    #         discount=self.discount if discount is None else discount,
    #         currency=self.currency_id if currency is None else currency,
    #         product=self.product_id if product is None else product,
    #         partner=self.partner_id if partner is None else partner,
    #         taxes=self.tax_ids if taxes is None else taxes,
    #         move_type=self.move_id.move_type if move_type is None else move_type,
    #     )
    #
    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
    #
    #     res = {}
    #
    #     # Compute 'price_subtotal'.
    #     line_discount_price_unit = price_unit * (1 - (discount / 100.0))
    #     subtotal = quantity * line_discount_price_unit
    #
    #     # Compute 'price_total'.
    #     if taxes:
    #         taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
    #             quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
    #         print(taxes_res)
    #         res['price_subtotal'] = taxes_res['total_excluded']
    #         res['price_total'] = taxes_res['total_included']
    #     else:
    #         res['price_total'] = res['price_subtotal'] = subtotal
    #     #In case of multi currency, round before it's use for computing debit credit
    #     if currency:
    #         res = {k: currency.round(v) for k, v in res.items()}
    #     return res
    #

# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"
#     def _prepare_invoice(self, ):
#         invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
#         invoice_vals.update({
#             'amount_tax': self.amount_tax,
#             'amount_total': self.amount_total,
#         })
#         return invoice_vals

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_qty = fields.Float(string='Total Quantity',  required=True)
    qty = fields.Float(string='Quantity',default=1,  required=True)
    bouns_qty = fields.Float(string='Bouns Quantity', )

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency': self.order_id.currency_id,
            'quantity': self.qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     for line in self:
    #         taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
    #         line.update({
    #             'price_tax': taxes['total_included'] - taxes['total_excluded'],
    #             'price_total': taxes['total_included']-(line.bouns_qty*line.price_unit),
    #             'price_subtotal': taxes['total_excluded']-(line.bouns_qty*line.price_unit),
    #         })

    @api.onchange('bouns_qty','qty')
    def onchange_qtybouns(self):
        self.product_qty = self.qty + self.bouns_qty

    def _prepare_account_move_line(self, move=False):
        invoice_line = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        invoice_line['price_unit']= self.price_unit
        invoice_line['qty']= self.qty
        invoice_line['bouns_qty']= self.bouns_qty
        invoice_line['quantity']= self.product_qty
        return invoice_line