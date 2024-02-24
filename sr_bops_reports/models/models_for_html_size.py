from lxml import etree
from io import StringIO
from markupsafe import Markup, escape

from odoo import api, fields, models


def set_fonts_def(data, set_font_size=""):
    if data:
        p_tag = etree.parse(StringIO(data), etree.HTMLParser()).find("//p")
        if p_tag is not None:
            if not set_font_size:
                p_tag.attrib["style"] = "font-size:12px;"
            else:
                p_tag.attrib["style"] = set_font_size
            return Markup(etree.tostring(p_tag).decode())
    return data


class AccoutMove(models.Model):
    _inherit = "account.move"

    def set_font_size(self, narration):
        return set_fonts_def(narration)


class SalesOrder(models.Model):
    _inherit = "sale.order"

    def set_font_size(self, note):
        return set_fonts_def(note, set_font_size="font-size: 15px;")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def set_font_size(self, notes):
        return set_fonts_def(notes)

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals.update({"purchase_reference": self.name})
        return invoice_vals
