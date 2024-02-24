from odoo import fields, api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    partner_id = fields.Many2one("res.partner", string="Related Partner")

    def set_related_partner_in_employee(self):
        for rec in self:
            partner = self.env["res.partner"].search([("name", "=", rec.name)], limit=1)
            partnerObj = self.env["res.partner"]
            if partner:
                rec.partner_id = partner.id
            else:
                partner = partnerObj.create(
                    {
                        "name": rec.name,
                        "phone": rec.work_phone,
                        "email": rec.work_email,
                        "mobile": rec.mobile_phone,
                    }
                )
                rec.address_home_id = partner.id
                rec.partner_id = partner.id

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        partnerObj = self.env["res.partner"]
        for emp in employee:
            partner = partnerObj.create(
                {
                    "name": emp.name,
                    "phone": emp.work_phone,
                    "email": emp.work_email,
                    "mobile": emp.mobile_phone,
                }
            )
            emp.address_home_id = partner.id
            emp.partner_id = partner.id
        return employee
