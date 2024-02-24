from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError
import pytz

import os
import time
import tempfile
import logging

_logger = logging.getLogger("SalesmanWise Report")
from datetime import datetime, timedelta

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import xlwt
    import xlsxwriter
    from xlwt.Utils import rowcol_to_cell
except ImportError:
    _logger.debug("Can not import xlsxwriter`.")
import base64


class SalesmanWiseReport(models.TransientModel):
    _name = "salesperson.report"
    _description = "SalesPerson Report"

    file_name = fields.Char("File Name")
    file_data = fields.Binary("Download", readonly=True)
    select_year = fields.Selection(
        [
            ("2021", "2021"),
            ("2022", "2022"),
            ("2023", "2023"),
            ("2024", "2024"),
            ("2025", "2025"),
            ("2026", "2026"),
            ("2027", "2027"),
        ],
        string="Select Year",
    )

    def generate_report(self):
        temp_dir = tempfile.gettempdir() or "/tmp"
        f_name = os.path.join(temp_dir, "salesman_wise_report.xlsx")
        workbook = xlsxwriter.Workbook(f_name)
        date_format = workbook.add_format(
            {"num_format": "d-m-yyyy", "align": "center", "valign": "vcenter"}
        )
        # Styles
        style_header = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vcenter"}
        )
        style_data = workbook.add_format({"border": 1, "align": "left"})
        style_data2 = workbook.add_format({"border": 1, "align": "center"})
        style_data3 = workbook.add_format({"border": 1, "align": "left"})
        style_achivement = workbook.add_format(
            {"bold": 1, "border": 1, "align": "left"}
        )
        style_total = workbook.add_format({"bold": 1, "border": 1, "align": "left"})
        style_header2 = workbook.add_format(
            {"bold": 1, "color": "white", "align": "center", "valign": "vcenter"}
        )
        style_header.set_font_size(18)
        style_header.set_text_wrap()
        style_header.set_font_name("Agency FB")
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        style_data.set_text_wrap()
        style_data.set_font_name("Agency FB")
        style_data2.set_font_size(12)
        style_data2.set_font_name("Agency FB")
        style_data3.set_font_size(11)
        style_data3.set_font_name("Calibri")
        style_total.set_font_size(12)
        style_total.set_text_wrap()
        style_achivement.set_font_size(12)
        style_achivement.set_text_wrap()
        style_achivement.set_bg_color("#FF8C00")
        # style_total.set_border(style=2)
        # date_format.set_font_size(12)
        # date_format.set_bg_color('#d7e4bd')
        # date_format.set_font_name('Agency FB')
        # date_format.set_border(style=2)
        style_header2.set_font_size(11)
        style_header2.set_bg_color("65ACCF")
        style_header2.set_font_name("Calibri")
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet("SalesMan Wise Report")
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 20)
        worksheet.set_column(5, 5, 20)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 20)
        # worksheet.set_column(9, 9, 15)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 20)
        worksheet.set_column(11, 11, 20)
        worksheet.set_column(12, 12, 20)
        worksheet.set_column(13, 13, 20)
        worksheet.set_column(14, 14, 20)
        worksheet.set_column(15, 15, 20)
        worksheet.set_column(16, 16, 20)
        worksheet.set_column(17, 17, 20)
        worksheet.set_column(18, 18, 20)
        worksheet.set_column(19, 19, 20)
        worksheet.set_column(20, 20, 20)
        worksheet.set_column(21, 21, 20)
        worksheet.set_column(22, 22, 20)
        worksheet.set_column(23, 23, 20)
        worksheet.set_column(24, 24, 20)
        worksheet.set_column(25, 25, 20)
        worksheet.set_row(0, 25)
        row, col = 0, 0
        worksheet.write(row, col, "Client Name", style_header2)
        all_invoice_ids = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "=", "posted")]
        )
        invoice_user_ids = all_invoice_ids.mapped("invoice_user_id")
        col = 1
        list_of_user = []
        for user in invoice_user_ids:
            worksheet.write(row, col, user.name, style_header2)
            list_of_user.append(user.name)
            col += 1
        row = col = 1
        partners = all_invoice_ids.mapped("partner_id")
        row = 1
        column = 0
        for partner in partners:
            worksheet.write(row, column, partner.name, style_data3)
            col = 1
            for user in invoice_user_ids:
                invoice_ids = self.env["account.move"].search(
                    [
                        ("invoice_user_id.id", "=", user.id),
                        ("partner_id", "=", partner.id),
                        ("move_type", "=", "out_invoice"),
                        ("state", "=", "posted"),
                    ]
                )
                total_amount = sum(
                    [
                        move.amount_untaxed_signed
                        for move in invoice_ids
                        if move.invoice_date
                        and move.invoice_date.year == int(self.select_year)
                    ]
                )
                worksheet.write(row, col, total_amount, style_data3)
                col += 1
            row += 1
        col = 1
        for user in invoice_user_ids:
            invoice_ids = self.env["account.move"].search(
                [
                    ("invoice_user_id", "=", user.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                ]
            )
            total = sum(
                [
                    move.amount_untaxed_signed
                    for move in invoice_ids
                    if move.invoice_date
                    and move.invoice_date.year == int(self.select_year)
                ]
            )
            worksheet.write(row, col, total, style_data3)
            col += 1
        workbook.close()
        f = open(f_name, "rb")
        data = f.read()
        f.close()
        name = "%s.xlsx" % ("SalesmanWiseReport_" + str(datetime.now() or ""))
        wip_report = self.env["sales.report"].create(
            {"file_name": name, "file_data": base64.encodebytes(data)}
        )
        view_id = self.env.ref("fs_sales_report.sales_report_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "sales.report",
            "target": "new",
            "view_mode": "form",
            "res_id": wip_report.id,
            "views": [[view_id, "form"]],
            "context": {"download_sales_report": True},
        }
