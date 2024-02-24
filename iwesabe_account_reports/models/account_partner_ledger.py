# * coding: utf8 *


from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from datetime import timedelta


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger'
    employee_id = fields.Many2one('hr.employee')

    filter_salesperson = True
    filter_employee = True

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountPartnerLedger, self)._get_options_domain(options)
        if options.get('salesperson') and options.get('salespersons'):
            salespersons = [int(salesperson) for salesperson in options['salespersons']]
            domain.append(('invoice_user_id', 'in', salespersons))
        elif options.get('employee') and options.get('employees'):
            employees = [int(employee) for employee in options['employees']]
            domain.append(('employee_id', 'in', employees))
        return domain
