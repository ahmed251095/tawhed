from odoo import fields, models, api, _

import os
import tempfile
import logging

_logger = logging.getLogger("Purchase Report")
from datetime import datetime

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


class CustomerPurchaseReport(models.TransientModel):
    _name = "purchase.xlxs.report"
    _description = "Purchase Report"

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
        f_name = os.path.join(temp_dir, "purchase_xlsx_report.xlsx")
        workbook = xlsxwriter.Workbook(f_name)

        report_name = "Purchase Report"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.set_column(0, 0, 35)
        sheet.set_column(1, 1, 35)
        sheet.set_column(2, 2, 12)
        sheet.set_column(3, 3, 12)
        sheet.set_column(4, 4, 12)
        sheet.set_column(5, 5, 12)
        sheet.set_column(6, 6, 12)
        sheet.set_column(7, 7, 12)
        sheet.set_column(8, 8, 12)
        # sheet.set_column(9, 9, 15)
        sheet.set_column(9, 9, 12)
        sheet.set_column(10, 10, 12)
        sheet.set_column(11, 11, 12)
        sheet.set_column(12, 12, 12)
        sheet.set_column(13, 13, 12)
        sheet.set_column(14, 14, 12)
        cell_format = workbook.add_format({"bold": True, "align": "left"})
        cell_format_right = workbook.add_format({"align": "left"})
        cell_format.set_font_size(11)
        cell_format.set_bg_color("65ACCF")
        cell_format.set_font_name("Calibri")
        cell_format_right.set_font_size(11)
        cell_format_right.set_font_name("Calibri")
        row = col = 0
        sheet.write(row, 0, "Supplier Name", cell_format)
        sheet.write(row, 1, "Payment terms", cell_format)
        sheet.write(row, 2, "JAN", cell_format)
        sheet.write(row, 3, "FEB", cell_format)
        sheet.write(row, 4, "MAR", cell_format)
        sheet.write(row, 5, "APR", cell_format)
        sheet.write(row, 6, "MAY", cell_format)
        sheet.write(row, 7, "JUN", cell_format)
        sheet.write(row, 8, "JUL", cell_format)
        sheet.write(row, 9, "AUG", cell_format)
        sheet.write(row, 10, "SEP", cell_format)
        sheet.write(row, 11, "OCT", cell_format)
        sheet.write(row, 12, "NOV", cell_format)
        sheet.write(row, 13, "DEC", cell_format)
        sheet.write(row, 14, "Total Amount", cell_format)

        jan_total = (
            feb_total
        ) = (
            march_total
        ) = (
            april_total
        ) = (
            may_total
        ) = (
            jun_total
        ) = (
            july_total
        ) = (
            aug_total
        ) = sept_total = oct_total = nov_total = dec_total = total_amount = 0
        current_year = int(self.select_year)

        invoice_ids = self.env["account.move"].search(
            [
                ("move_type", "=", "in_invoice"),
                ("state", "=", "posted"),
            ]
        )
        invoice_partner_ids = invoice_ids.mapped("partner_id")
        row = 1
        for partner in invoice_partner_ids:
            move_ids = self.env["account.move"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("move_type", "=", "in_invoice"),
                    ("state", "=", "posted"),
                ]
            )
            if not move_ids.partner_id:
                continue
            january_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 1
                    and move.invoice_date.year == current_year
                ]
            )

            feb_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 2
                    and move.invoice_date.year == current_year
                ]
            )

            march_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 3
                    and move.invoice_date.year == current_year
                ]
            )

            april_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 4
                    and move.invoice_date.year == current_year
                ]
            )

            may_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 5
                    and move.invoice_date.year == current_year
                ]
            )

            jun_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 6
                    and move.invoice_date.year == current_year
                ]
            )

            july_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 7
                    and move.invoice_date.year == current_year
                ]
            )

            aug_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 8
                    and move.invoice_date.year == current_year
                ]
            )

            sept_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 9
                    and move.invoice_date.year == current_year
                ]
            )

            oct_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 10
                    and move.invoice_date.year == current_year
                ]
            )

            nov_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 11
                    and move.invoice_date.year == current_year
                ]
            )

            dec_amount = sum(
                [
                    move.amount_untaxed_signed
                    for move in move_ids
                    if move.invoice_date
                    and move.invoice_date.month == 12
                    and move.invoice_date.year == current_year
                ]
            )

            jan_total += january_amount
            feb_total += feb_amount
            march_total += march_amount
            april_total += april_amount
            may_total += may_amount
            jun_total += jun_amount
            july_total += july_amount
            aug_total += aug_amount
            sept_total += sept_amount
            oct_total += oct_amount
            nov_total += nov_amount
            dec_total += dec_amount

            total_amount = (
                january_amount
                + feb_amount
                + march_amount
                + april_amount
                + may_amount
                + jun_amount
                + july_amount
                + aug_amount
                + sept_amount
                + oct_amount
                + nov_amount
                + dec_amount
            )

            if move_ids:
                sheet.write(row, col, move_ids[0].partner_id.name, cell_format_right)
                sheet.write(
                    row,
                    col + 1,
                    move_ids[0].invoice_payment_term_id.name,
                    cell_format_right,
                )
                sheet.write(row, col + 2, january_amount or 0, cell_format_right)
                sheet.write(row, col + 3, feb_amount or 0, cell_format_right)
                sheet.write(row, col + 4, march_amount or 0, cell_format_right)
                sheet.write(row, col + 5, april_amount or 0, cell_format_right)
                sheet.write(row, col + 6, may_amount or 0, cell_format_right)
                sheet.write(row, col + 7, jun_amount or 0, cell_format_right)
                sheet.write(row, col + 8, july_amount or 0, cell_format_right)
                sheet.write(row, col + 9, aug_amount or 0, cell_format_right)
                sheet.write(row, col + 10, sept_amount or 0, cell_format_right)
                sheet.write(row, col + 11, oct_amount or 0, cell_format_right)
                sheet.write(row, col + 12, nov_amount or 0, cell_format_right)
                sheet.write(row, col + 13, dec_amount or 0, cell_format_right)
                sheet.write(row, col + 14, total_amount, cell_format_right)
                row += 1
        total = (
            jan_total
            + feb_total
            + march_total
            + april_total
            + may_total
            + jun_total
            + july_total
            + aug_total
            + sept_total
            + nov_total
            + oct_total
            + dec_total
        )
        col = 1
        sheet.write(row, col + 1, jan_total or 0, cell_format_right)
        sheet.write(row, col + 2, feb_total or 0, cell_format_right)
        sheet.write(row, col + 3, march_total or 0, cell_format_right)
        sheet.write(row, col + 4, april_total or 0, cell_format_right)
        sheet.write(row, col + 5, may_total or 0, cell_format_right)
        sheet.write(row, col + 6, jun_total or 0, cell_format_right)
        sheet.write(row, col + 7, july_total or 0, cell_format_right)
        sheet.write(row, col + 8, aug_total or 0, cell_format_right)
        sheet.write(row, col + 9, sept_total or 0, cell_format_right)
        sheet.write(row, col + 10, oct_total or 0, cell_format_right)
        sheet.write(row, col + 11, nov_total or 0, cell_format_right)
        sheet.write(row, col + 12, dec_total or 0, cell_format_right)
        sheet.write(row, col + 13, total, cell_format_right)
        workbook.close()
        f = open(f_name, "rb")
        data = f.read()
        f.close()
        name = "%s.xlsx" % ("PurchaseReport_" + str(datetime.now() or ""))
        wip_report = self.env["purchase.xlxs.report"].create(
            {"file_name": name, "file_data": base64.encodebytes(data)}
        )
        view_id = self.env.ref("purchase_xlsx_report.purchase_report_wizard_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.xlxs.report",
            "target": "new",
            "view_mode": "form",
            "res_id": wip_report.id,
            "views": [[view_id, "form"]],
            "context": {"download_purchase_report": True},
        }
