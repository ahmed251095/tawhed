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
