from odoo import fields, api, models


class Sale(models.Model):
    _inherit = "sale.order"

    def _get_default_greeting(self):
        greeting = (
            "Dear Ms.  ,\n"
            + "We thank you for your enquiry, and as per your requirement please find below quote."
        )
        return greeting

    quote_validity = fields.Text("Quote Validity", default="15days")
    delivery = fields.Text("Delivery")
    greeting = fields.Text("Greeting", default=_get_default_greeting)
    amount_untaxed = fields.Monetary(
        string="PreVat Amount", store=True, compute="_amount_all", tracking=5
    )
    store = fields.Char(string="Store")
    location = fields.Char(string="Location")
    brand = fields.Char(string="Brand")
