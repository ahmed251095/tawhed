from odoo import api, fields, models
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    mandoub_id = fields.Many2one('hr.employee', string='اسم المندوب', tracking=True)
    driver_id = fields.Many2one('hr.employee', string='اسم السائق', tracking=True)



    @api.onchange('invoice_line_ids.discount', 'invoice_line_ids')
    def _check_discount_value(self):
        for rec in self.invoice_line_ids:
            if rec.discount > rec.env.user.percentage:
                raise ValidationError('User Discount Limit is (%s) ' % (str(rec.env.user.percentage) + ' %'))


class AccountMoveline(models.Model):
    _inherit = 'account.move.line'
    is_bouns = fields.Boolean('Bouns ? ')

    @api.onchange('is_bouns')
    def _onchange_is_bouns(self):
        for rec in self:
            if rec.is_bouns == True:
                rec.price_unit = 0
    price_after = fields.Float(string='Price after disc.',compute='compute_price_after')
    @api.depends('discount')
    def compute_price_after(self):
        for rec in self:
            rec.price_after = (1-rec.discount/100) * rec.price_unit

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('order_line.discount', 'order_line')
    def _check_discount_value(self):
        for rec in self.order_line:
            if rec.discount > rec.env.user.percentage:
                raise ValidationError('User Discount Limit is (%s) ' % (str(rec.env.user.percentage)+' %'))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    is_bouns = fields.Boolean('Bouns ? ')

    @api.constrains('price_unit','is_bouns')
    def _price_validation(self):
        for rec in self:
            if rec.price_unit < rec.product_id.standard_price and not rec.is_bouns:
                raise UserError('For product:{}\nPrice Unit Must be >=  Product cost'.format(rec.product_id.name))

    @api.onchange('is_bouns')
    def _onchange_is_bouns(self):
        for rec in self:
            if rec.is_bouns == True:
                rec.price_unit = 0

    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        invoice_line['is_bouns'] = self.is_bouns
        invoice_line['is_bouns'] = self.is_bouns
        return invoice_line

class ResUsers(models.Model):
    _inherit = "res.users"

    is_cashier = fields.Boolean('Cashier')
    percentage = fields.Float('Discount(%)')


