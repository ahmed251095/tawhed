from odoo import fields, models, api



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  related='payment_id.employee_id', store=True
                                  )

    invoice_user_id = fields.Many2one('res.users',
                                      string='Sales Person',
                                      related='move_id.invoice_user_id', store=True
                                      )
    sales_person_id = fields.Many2one(comodel_name='res.users', string='Sales Person')



class AccountPayment(models.Model):
    _inherit = 'account.payment'
    partner_balance = fields.Monetary('Partner Balance',compute='compute_partner_balance',store=True)

    @api.depends("partner_id")
    def compute_partner_balance(self):
        total = 0
        for k in self:
            obj = self.env['account.move.line'].search([('partner_id', '=', k.partner_id.id)])
            for i in obj:
                if i.move_id.state == "posted":
                    if i.account_id.user_type_id.type in ['payable', 'receivable']:
                        total = total + (i.debit-i.credit)
            k.partner_balance = total
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  tracking=True, copy=False
                                  )
    sales_person_id = fields.Many2one("res.users", string="Sales Person")



class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  tracking=True, copy=False
                                  )

    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()
        vals.update({'employee_id': self.employee_id.id})
        return vals
