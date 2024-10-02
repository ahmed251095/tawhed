from odoo import fields, models, api,exceptions,_



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

    def action_post(self):
        for rec in self:
            if rec.amount <= 0 :
                raise exceptions.ValidationError(_("Please Set Amount > 0  First"))
            if not rec.sales_person_id:
                raise exceptions.ValidationError(_("Please Set Sales Person First"))
        super().action_post()
    def write(self, values):
        # Add code here
        res =  super(AccountPayment, self).write(values)
        if 'sales_person_id' in values:
            for payment in self:
                for line in payment.move_id.line_ids:
                    line.sales_person_id = payment.sales_person_id.id
        return res
class CustomAccountMove(models.Model):
    _inherit = 'account.move'

    def onchange_analytic_move(self):
        for rec in self :
            print(rec.id)
            record_analytic=self.env['account.move.line'].search([("move_id","=",rec.id),("sales_person_id","!=",None)],limit=1)
            analytic=record_analytic.sales_person_id
            records=self.env['account.move.line'].search([("move_id","=",rec.id),("sales_person_id","=",None)])
            if records:
                print("sssssssssssssssssssssssss")
                for rec in records:
                        rec.sales_person_id=analytic
            else:
                    print("ppppppppppppppppp")
    @api.model
    def create(self, vals):
        record = super(CustomAccountMove, self).create(vals)
        record.onchange_analytic_move()
        return record
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
