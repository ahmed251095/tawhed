# * coding: utf8 *


from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_salesperson = None
    filter_employee = None

    @api.model
    def _init_filter_salesperson(self, options, previous_options=None):
        query = "UPDATE account_move_line SET invoice_user_id=(SELECT invoice_user_id from account_move where id=account_move_line.move_id) WHERE account_move_line.invoice_user_id is NULL;"
        self.env.cr.execute(query)
        query2 = "UPDATE account_move_line SET employee_id=(SELECT employee_id from account_payment where id=account_move_line.payment_id) WHERE account_move_line.employee_id is NULL;"
        self.env.cr.execute(query2)
        if not self.filter_salesperson or not self.filter_employee:
            return

        options['salesperson'] = self.filter_salesperson
        options['employee'] = self.filter_employee
        res_salesperson_obj = self.env['res.users']
        res_employee_obj = self.env['hr.employee']
        options['salespersons'] = previous_options and previous_options.get('salespersons') or [
        ]
        options['employees'] = previous_options and previous_options.get('employees') or [
        ]
        invoice_user_ids = [int(salesperson) for salesperson in options['salespersons']]
        employee_ids = [int(employee) for employee in options['employees']]
        selected_invoice_user_ids = invoice_user_ids and res_salesperson_obj.browse(
            invoice_user_ids) or res_salesperson_obj
        selected_employee_ids = employee_ids and res_employee_obj.browse(
            employee_ids) or res_employee_obj
        options['selected_invoice_user_ids'] = selected_invoice_user_ids.mapped('name')
        options['selected_employee_ids'] = selected_employee_ids.mapped('name')

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('salespersons'):
            ctx['invoice_user_ids'] = self.env['res.users'].browse(
                [int(salesperson) for salesperson in options['salespersons']]).ids
        if options.get('employees'):
            ctx['employee_ids'] = self.env['hr.employee'].browse(
                [int(employee) for employee in options['employees']]).ids
        return ctx

    def get_report_informations(self, options):
        options = self._get_options(options)
        if options.get('salesperson'):
            options['selected_invoice_user_ids'] = [self.env['res.users'].browse(
                int(salesperson)).name for salesperson in options['salespersons']]
        if options.get('employee'):
            options['selected_employee_ids'] = [self.env['hr.employee'].browse(
                int(employee)).name for employee in options['employees']]
        return super(AccountReport, self).get_report_informations(options)

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        if options.get('salesperson') and options.get('salespersons'):
            salespersons = [int(salesperson) for salesperson in options['salespersons']]
            domain.append(('invoice_user_id', 'in', salespersons))
        if options.get('employee') and options.get('employees'):
            employees = [int(employee) for employee in options['employees']]
            domain.append(('employee_id', 'in', employees))
        return domain