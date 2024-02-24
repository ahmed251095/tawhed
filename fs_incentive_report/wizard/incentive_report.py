from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError
import pytz

import os
import time
import tempfile
import logging

_logger = logging.getLogger("Incentive Report")
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


class IncentiveReport(models.TransientModel):
    _name = "incentive.report"
    _description = "Incentive Report"

    file_name = fields.Char("File Name")
    report_by = fields.Selection(
        [("person_wise", "Sale Person"), ("cordinator_wise", "Sales Cordinator")],
        string="Report By",
    )
    file_data = fields.Binary("Download", readonly=True)

    def get_cordinator_commission(self, invoice, gp, pay_date):
        days = 0
        if invoice.invoice_date_due and pay_date:
            days = abs((invoice.invoice_date_due - pay_date).days)
        if invoice.invoice_date and invoice.invoice_date_due:
            days += abs((invoice.invoice_date - invoice.invoice_date_due).days)
        if gp > 45:
            if 0 <= days and days <= 30:
                return 1.4
            elif 31 <= days and days <= 45:
                return 1.3
            elif 46 <= days and days <= 60:
                return 1.1
            elif 61 <= days and days <= 75:
                return 1.0
            elif 76 <= days and days <= 90:
                return 0.9
            elif 91 <= days and days <= 105:
                return 0.8
            elif 106 <= days and days <= 120:
                return 0.7
            elif 121 <= days and days <= 150:
                return 0.7
            elif 151 <= days and days <= 180:
                return 0.6
            elif 180 < days:
                return 0.5
        elif 44 > gp and gp <= 45:
            if 0 <= days and days <= 30:
                return 1.4
            elif 31 <= days and days <= 45:
                return 1.3
            elif 46 <= days and days <= 60:
                return 1.1
            elif 61 <= days and days <= 75:
                return 1.0
            elif 76 <= days and days <= 90:
                return 0.9
            elif 91 <= days and days <= 105:
                return 0.8
            elif 106 <= days and days <= 120:
                return 0.7
            elif 121 <= days and days <= 150:
                return 0.7
            elif 151 <= days and days <= 180:
                return 0.6
            elif 180 < days:
                return 0.5
        elif 43 > gp and gp <= 44:
            if 0 <= days and days <= 30:
                return 1.3
            elif 31 <= days and days <= 45:
                return 1.1
            elif 46 <= days and days <= 60:
                return 1.0
            elif 61 <= days and days <= 75:
                return 0.9
            elif 76 <= days and days <= 90:
                return 0.8
            elif 91 <= days and days <= 105:
                return 0.7
            elif 106 <= days and days <= 120:
                return 0.7
            elif 121 <= days and days <= 150:
                return 0.6
            elif 151 <= days and days <= 180:
                return 0.5
            elif 180 < days:
                return 0.5
        elif 42 > gp and gp <= 43:
            if 0 <= days and days <= 30:
                return 1.1
            elif 31 <= days and days <= 45:
                return 1.0
            elif 46 <= days and days <= 60:
                return 0.9
            elif 61 <= days and days <= 75:
                return 0.8
            elif 76 <= days and days <= 90:
                return 0.7
            elif 91 <= days and days <= 105:
                return 0.7
            elif 106 <= days and days <= 120:
                return 0.6
            elif 121 <= days and days <= 150:
                return 0.5
            elif 151 <= days and days <= 180:
                return 0.5
            elif 180 < days:
                return 0.4
        elif 41 > gp and gp <= 42:
            if 0 <= days and days <= 30:
                return 1.0
            elif 31 <= days and days <= 45:
                return 0.9
            elif 46 <= days and days <= 60:
                return 0.8
            elif 61 <= days and days <= 75:
                return 0.7
            elif 76 <= days and days <= 90:
                return 0.7
            elif 91 <= days and days <= 105:
                return 0.6
            elif 106 <= days and days <= 120:
                return 0.5
            elif 121 <= days and days <= 150:
                return 0.5
            elif 151 <= days and days <= 180:
                return 0.4
            elif 180 < days:
                return 0.4
        elif 40 >= gp and gp <= 41:
            if 0 <= days and days <= 30:
                return 0.9
            elif 31 <= days and days <= 45:
                return 0.8
            elif 46 <= days and days <= 60:
                return 0.74
            elif 61 <= days and days <= 75:
                return 0.7
            elif 76 <= days and days <= 90:
                return 0.6
            elif 91 <= days and days <= 105:
                return 0.5
            elif 106 <= days and days <= 120:
                return 0.5
            elif 121 <= days and days <= 150:
                return 0.4
            elif 151 <= days and days <= 180:
                return 0.4
            elif 180 < days:
                return 0.4
        elif 40 > gp:
            return 0.0

    def get_commission(self, invoice, gp, pay_date):
        days = 0
        if invoice.invoice_date_due and pay_date:
            days = abs((invoice.invoice_date_due - pay_date).days)
        if invoice.invoice_date and invoice.invoice_date_due:
            days += abs((invoice.invoice_date - invoice.invoice_date_due).days)
        if gp > 45:
            if 0 <= days and days <= 30:
                return 2.8
            elif 31 <= days and days <= 45:
                return 2.5
            elif 46 <= days and days <= 60:
                return 2.3
            elif 61 <= days and days <= 75:
                return 2.0
            elif 76 <= days and days <= 90:
                return 1.8
            elif 91 <= days and days <= 105:
                return 1.7
            elif 106 <= days and days <= 120:
                return 1.5
            elif 121 <= days and days <= 150:
                return 1.3
            elif 151 <= days and days <= 180:
                return 1.2
            elif 180 < days:
                return 1.1
        elif 44 > gp and gp <= 45:
            if 0 <= days and days <= 30:
                return 2.8
            elif 31 <= days and days <= 45:
                return 2.5
            elif 46 <= days and days <= 60:
                return 2.3
            elif 61 <= days and days <= 75:
                return 2.0
            elif 76 <= days and days <= 90:
                return 1.8
            elif 91 <= days and days <= 105:
                return 1.7
            elif 106 <= days and days <= 120:
                return 1.5
            elif 121 <= days and days <= 150:
                return 1.3
            elif 151 <= days and days <= 180:
                return 1.2
            elif 180 < days:
                return 1.1
        elif 43 > gp and gp <= 44:
            if 0 <= days and days <= 30:
                return 2.5
            elif 31 <= days and days <= 45:
                return 2.3
            elif 46 <= days and days <= 60:
                return 2.0
            elif 61 <= days and days <= 75:
                return 1.8
            elif 76 <= days and days <= 90:
                return 1.7
            elif 91 <= days and days <= 105:
                return 1.5
            elif 106 <= days and days <= 120:
                return 1.3
            elif 121 <= days and days <= 150:
                return 1.2
            elif 151 <= days and days <= 180:
                return 1.1
            elif 180 < days:
                return 1.0
        elif 42 > gp and gp <= 43:
            if 0 <= days and days <= 30:
                return 2.3
            elif 31 <= days and days <= 45:
                return 2.0
            elif 46 <= days and days <= 60:
                return 1.8
            elif 61 <= days and days <= 75:
                return 1.7
            elif 76 <= days and days <= 90:
                return 1.5
            elif 91 <= days and days <= 105:
                return 1.3
            elif 106 <= days and days <= 120:
                return 1.2
            elif 121 <= days and days <= 150:
                return 1.1
            elif 151 <= days and days <= 180:
                return 1.0
            elif 180 < days:
                return 0.9
        elif 41 > gp and gp <= 42:
            if 0 <= days and days <= 30:
                return 2.0
            elif 31 <= days and days <= 45:
                return 1.8
            elif 46 <= days and days <= 60:
                return 1.7
            elif 61 <= days and days <= 75:
                return 1.5
            elif 76 <= days and days <= 90:
                return 1.3
            elif 91 <= days and days <= 105:
                return 1.2
            elif 106 <= days and days <= 120:
                return 1.1
            elif 121 <= days and days <= 150:
                return 1.0
            elif 151 <= days and days <= 180:
                return 0.9
            elif 180 < days:
                return 0.8
        elif 40 >= gp and gp <= 41:
            if 0 <= days and days <= 30:
                return 1.8
            elif 31 <= days and days <= 45:
                return 1.7
            elif 46 <= days and days <= 60:
                return 1.5
            elif 61 <= days and days <= 75:
                return 1.3
            elif 76 <= days and days <= 90:
                return 1.2
            elif 91 <= days and days <= 105:
                return 1.1
            elif 106 <= days and days <= 120:
                return 1.0
            elif 121 <= days and days <= 150:
                return 0.9
            elif 151 <= days and days <= 180:
                return 0.8
            elif 180 < days:
                return 0.7
        elif 40 > gp:
            return 0.0

    def generate_report(self):
        temp_dir = tempfile.gettempdir() or "/tmp"
        f_name = os.path.join(temp_dir, "incentive_report.xlsx")
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
            {"bold": 1, "align": "center", "valign": "vcenter"}
        )
        style_header.set_font_size(18)
        style_header.set_text_wrap()
        style_header.set_bg_color("#d7e4bd")
        style_header.set_font_name("Agency FB")
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        style_data.set_text_wrap()
        style_data.set_font_name("Agency FB")
        style_data2.set_font_size(12)
        style_data2.set_font_name("Agency FB")
        style_data3.set_font_size(12)
        style_data3.set_font_name("Agency FB")
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
        style_header2.set_font_size(12)
        style_header2.set_bg_color("#FFD700")
        style_header2.set_font_name("Agency FB")
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet("Incentive Report")
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(3, 3, 12)
        worksheet.set_column(4, 4, 12)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 35)
        worksheet.set_column(8, 8, 12)
        # worksheet.set_column(9, 9, 15)
        worksheet.set_column(9, 9, 15)
        worksheet.set_column(10, 10, 12)
        worksheet.set_column(11, 11, 12)
        worksheet.set_column(12, 12, 12)
        worksheet.set_column(13, 13, 35)
        worksheet.set_column(14, 14, 12)
        worksheet.set_column(15, 15, 12)
        worksheet.set_column(16, 16, 15)
        worksheet.set_column(17, 17, 20)
        worksheet.set_column(18, 18, 12)
        worksheet.set_row(0, 25)
        row, col = 0, 0
        worksheet.write(row, col, "Invoice No.", style_header2)
        worksheet.write(row, col + 1, "Invoice Date", style_header2)
        worksheet.write(row, col + 2, "Due Date", style_header2)
        worksheet.write(row, col + 3, "Payment Date", style_header2)
        worksheet.write(row, col + 4, "Payment Terms", style_header2)
        worksheet.write(row, col + 5, "Payment Late By", style_header2)
        worksheet.write(row, col + 6, "Job#", style_header2)
        worksheet.write(row, col + 7, "Client", style_header2)
        worksheet.write(row, col + 8, "Invoice Amount", style_header2)
        # worksheet.write(row, col + 9, "Shipping/INSTALLATION", style_header2)
        worksheet.write(row, col + 9, "COVID/PERMITS/STORAGE/SHIPMENT", style_header2)
        worksheet.write(row, col + 10, "Amount", style_header2)
        worksheet.write(row, col + 11, "Estimate", style_header2)
        worksheet.write(row, col + 12, "G.P%", style_header2)
        worksheet.write(row, col + 13, "Subject", style_header2)
        worksheet.write(row, col + 14, "Collection", style_header2)
        worksheet.write(row, col + 15, "Commission", style_header2)
        worksheet.write(row, col + 16, "Commsion Elegibility", style_header2)
        worksheet.write(row, col + 17, "Sales Person", style_header2)
        worksheet.write(row, col + 18, "Rank", style_header2)
        invoice_ids = self.env["account.move"].search(
            [
                ("payment_state", "=", "paid"),
                ("move_type", "=", "out_invoice"),
                ("state", "!=", "cancel"),
            ]
        )
        invoices_data = {}
        for invoice in invoice_ids:
            if invoices_data.get(invoice.project_no):
                invoices_data[invoice.project_no].append(invoice)
            else:
                if not invoice.project_no:
                    continue
                invoices_data.update({invoice.project_no: [invoice]})
        row = 1
        collection = 0.0
        comission_total = 0.0
        inv_total = 0.0
        for project_no, vals in invoices_data.items():
            if len(vals) > 1:
                flag = False
                for invoice in vals:
                    if (
                        self.report_by == "person_wise"
                        and invoice.invoice_user_id.has_group(
                            "fs_incentive_report.group_sales_person_user"
                        )
                        or self.report_by == "cordinator_wise"
                        and invoice.invoice_user_id.has_group(
                            "odoo_job_costing_management.group_sales_cordinator"
                        )
                    ):
                        worksheet.write(row, col, invoice.name, style_data3)
                        worksheet.write(
                            row,
                            col + 1,
                            invoice.invoice_date.strftime("%Y-%m-%d"),
                            style_data3,
                        )
                        worksheet.write(
                            row,
                            col + 2,
                            invoice.invoice_date_due.strftime("%Y-%m-%d"),
                            style_data3,
                        )
                        payment_date = ""
                        pay_date = ""
                        for pay_vals in invoice._get_reconciled_info_JSON_values():
                            if pay_vals.get("date"):
                                payment_date = pay_vals.get("date").strftime("%Y-%m-%d")
                                pay_date = pay_vals.get("date")
                        worksheet.write(
                            row,
                            col + 3,
                            payment_date,
                            style_data3,
                        )
                        worksheet.write(
                            row,
                            col + 4,
                            abs((invoice.invoice_date - invoice.invoice_date_due).days),
                            style_data3,
                        )
                        worksheet.write(
                            row,
                            col + 5,
                            abs((invoice.invoice_date_due - pay_date).days),
                            style_data3,
                        )
                        worksheet.write(row, col + 6, project_no, style_data3)
                        worksheet.write(
                            row, col + 7, invoice.partner_id.name, style_data3
                        )
                        worksheet.write(
                            row, col + 8, invoice.amount_untaxed, style_data3
                        )
                        # worksheet.write(row, col + 9, "", style_data3)
                        covid_line = invoice.invoice_line_ids.filtered(
                            lambda l: l.product_id.name
                            in (
                                "COVID CHARGES",
                                "SHIPMENT CHARGES",
                                "RTA Parking Fee",
                                "STORAGE",
                                "STORAGE CHARGES",
                            )
                        )
                        covid_permit_storage_shipment = sum(
                            covid_line.mapped("price_unit")
                        )
                        worksheet.write(
                            row, col + 9, covid_permit_storage_shipment, style_data3
                        )
                        invoice_amount_total = sum([inv.amount_untaxed for inv in vals])
                        # if not flag:
                        #     worksheet.merge_range(
                        #         row,
                        #         col + 10,
                        #         row + len(vals),
                        #         col + 10,
                        #         "%.2f" % invoice_amount_total,
                        #         style_data3,
                        #     )
                        #     flag = True
                        # picking_ids = self.env["stock.picking"].search(
                        #     [
                        #         ("picking_type_id.code", "in", ("outgoing", "internal")),
                        #         ("project_id.job_number", "=", project_no),
                        #         ("state", "=", "done"),
                        #     ]
                        # )
                        costing_ids = self.env["job.costing"].search(
                            [
                                ("project_id.job_number", "=", project_no),
                                ("state", "!=", "cancel"),
                            ]
                        )
                        # total_valuation_cost = sum(
                        #     [picking.total_valuation_cost for picking in picking_ids]
                        # )
                        estimate_total = sum(
                            [costing.jobcost_total for costing in costing_ids]
                        )
                        # bill_amount_total = total_valuation_cost + estimate_total
                        gp_amount = abs(
                            (invoice_amount_total - estimate_total)
                            / invoice_amount_total
                            * 100
                        )
                        amount = invoice_amount_total - covid_permit_storage_shipment
                        if not flag:
                            worksheet.merge_range(
                                row,
                                col + 10,
                                row + len(vals) - 1,
                                col + 10,
                                "%.2f" % amount,
                                style_data3,
                            )
                            worksheet.merge_range(
                                row,
                                col + 11,
                                row + len(vals) - 1,
                                col + 11,
                                "%.2f" % estimate_total,
                                style_data3,
                            )
                            worksheet.merge_range(
                                row,
                                col + 12,
                                row + len(vals) - 1,
                                col + 12,
                                "%.2f" % gp_amount,
                                style_data3,
                            )
                            flag = True
                        worksheet.write(
                            row, col + 13, invoice.opportunity_id.name, style_data3
                        )
                        worksheet.write(
                            row, col + 14, invoice.amount_total, style_data3
                        )
                        comission = 0.0
                        if (
                            self.report_by == "person_wise"
                            and invoice.invoice_user_id.has_group(
                                "fs_incentive_report.group_sales_person_user"
                            )
                        ):
                            comission = self.get_commission(
                                invoice=invoice,
                                gp=gp_amount,
                                pay_date=pay_date,
                            )
                        if (
                            self.report_by == "cordinator_wise"
                            and invoice.invoice_user_id.has_group(
                                "odoo_job_costing_management.group_sales_cordinator"
                            )
                        ):
                            comission = self.get_cordinator_commission(
                                invoice=invoice,
                                gp=gp_amount,
                                pay_date=pay_date,
                            )
                        comission_amount = 0.0
                        if invoice.amount_total > 0:
                            if invoice_amount_total and comission:
                                comission_amount = (
                                    invoice_amount_total * comission
                                ) / 100
                            else:
                                comission_amount = 0.0
                        comission_eligibility = ""
                        if 40 < gp_amount:
                            comission_eligibility = "Elegible"
                        else:
                            comission_eligibility = "Non Elegible"
                        collection += invoice.amount_total
                        comission_total += comission_amount
                        inv_total += invoice_amount_total
                        worksheet.write(
                            row, col + 15, "%.2f" % comission_amount, style_data3
                        )
                        worksheet.write(
                            row, col + 16, comission_eligibility, style_data3
                        )
                        worksheet.write(
                            row, col + 17, invoice.invoice_user_id.name, style_data3
                        )
                        worksheet.write(row, col + 18, comission, style_data3)
                        row = row + 1
            else:
                for invoice in vals:
                    if (
                        self.report_by == "person_wise"
                        and invoice.invoice_user_id.has_group(
                            "fs_incentive_report.group_sales_person_user"
                        )
                        or self.report_by == "cordinator_wise"
                        and invoice.invoice_user_id.has_group(
                            "odoo_job_costing_management.group_sales_cordinator"
                        )
                    ):
                        worksheet.write(row, col, invoice.name, style_data3)
                        worksheet.write(
                            row,
                            col + 1,
                            invoice.invoice_date.strftime("%Y-%m-%d"),
                            style_data3,
                        )
                        worksheet.write(
                            row,
                            col + 2,
                            invoice.invoice_date_due.strftime("%Y-%m-%d"),
                            style_data3,
                        )
                        payment_date = ""
                        pay_date = ""
                        for pay_vals in invoice._get_reconciled_info_JSON_values():
                            if pay_vals.get("date"):
                                payment_date = pay_vals.get("date").strftime("%Y-%m-%d")
                                pay_date = pay_vals.get("date")
                        worksheet.write(
                            row,
                            col + 3,
                            payment_date,
                            style_data3,
                        )
                        worksheet.write(
                            row,
                            col + 4,
                            abs((invoice.invoice_date - invoice.invoice_date_due).days),
                            style_data3,
                        )
                        worksheet.write(
                            row,
                            col + 5,
                            abs((invoice.invoice_date_due - pay_date).days),
                            style_data3,
                        )
                        worksheet.write(row, col + 6, project_no, style_data3)
                        worksheet.write(
                            row, col + 7, invoice.partner_id.name, style_data3
                        )
                        worksheet.write(
                            row, col + 8, invoice.amount_untaxed, style_data3
                        )
                        # worksheet.write(row, col + 9, "", style_data3)
                        covid_line = invoice.invoice_line_ids.filtered(
                            lambda l: l.product_id.name
                            in (
                                "COVID CHARGES",
                                "SHIPMENT CHARGES",
                                "RTA Parking Fee",
                                "STORAGE",
                                "STORAGE CHARGES",
                            )
                        )
                        covid_permit_storage_shipment = sum(
                            covid_line.mapped("price_unit")
                        )
                        worksheet.write(
                            row, col + 9, covid_permit_storage_shipment, style_data3
                        )
                        invoice_amount_total = sum([inv.amount_untaxed for inv in vals])
                        amount = invoice_amount_total - covid_permit_storage_shipment
                        worksheet.write(row, col + 10, "%.2f" % amount, style_data3)
                        # picking_ids = self.env["stock.picking"].search(
                        #     [
                        #         ("picking_type_id.code", "in", ("outgoing", "internal")),
                        #         ("project_id.job_number", "=", project_no),
                        #         ("state", "=", "done"),
                        #     ]
                        # )
                        costing_ids = self.env["job.costing"].search(
                            [
                                ("project_id.job_number", "=", project_no),
                                ("state", "!=", "cancel"),
                            ]
                        )
                        # total_valuation_cost = sum(
                        #     [picking.total_valuation_cost for picking in picking_ids]
                        # )
                        estimate_total = sum(
                            [costing.jobcost_total for costing in costing_ids]
                        )
                        # bill_amount_total = total_valuation_cost + estimate_total
                        gp_amount = abs(
                            (invoice_amount_total - estimate_total)
                            / invoice_amount_total
                            * 100
                        )
                        worksheet.write(
                            row, col + 11, "%.2f" % estimate_total, style_data3
                        )
                        worksheet.write(row, col + 12, "%.2f" % gp_amount, style_data3)
                        worksheet.write(
                            row, col + 13, invoice.opportunity_id.name, style_data3
                        )
                        comission = 0.0
                        if (
                            self.report_by == "person_wise"
                            and invoice.invoice_user_id.has_group(
                                "fs_incentive_report.group_sales_person_user"
                            )
                        ):
                            comission = self.get_commission(
                                invoice=invoice,
                                gp=gp_amount,
                                pay_date=pay_date,
                            )
                        if (
                            self.report_by == "cordinator_wise"
                            and invoice.invoice_user_id.has_group(
                                "odoo_job_costing_management.group_sales_cordinator"
                            )
                        ):
                            comission = self.get_cordinator_commission(
                                invoice=invoice,
                                gp=gp_amount,
                                pay_date=pay_date,
                            )
                        comission_amount = 0.0
                        if invoice.amount_total > 0:
                            if invoice_amount_total and comission:
                                comission_amount = (
                                    invoice_amount_total * comission
                                ) / 100
                            else:
                                comission_amount = 0.0
                        comission_eligibility = ""
                        if 40 < gp_amount:
                            comission_eligibility = "Elegible"
                        else:
                            comission_eligibility = "Non Elegible"
                        collection += invoice.amount_total
                        comission_total += comission_amount
                        inv_total += invoice_amount_total
                        worksheet.write(
                            row, col + 14, invoice.amount_total, style_data3
                        )
                        worksheet.write(
                            row, col + 15, "%.2f" % comission_amount, style_data3
                        )
                        worksheet.write(
                            row, col + 16, comission_eligibility, style_data3
                        )
                        worksheet.write(
                            row, col + 17, invoice.invoice_user_id.name, style_data3
                        )
                        worksheet.write(row, col + 18, comission, style_data3)
                        row = row + 1
        worksheet.write(row + 3, col + 7, "Grand Total", style_total)
        worksheet.write(row + 4, col + 7, "Target ( 220,000 x 3 )", style_data3)
        worksheet.write(row + 5, col + 7, "Achievements", style_achivement)
        worksheet.write(row + 5, col + 8, "", style_achivement)
        worksheet.write(row + 5, col + 9, "", style_achivement)
        worksheet.write(row + 5, col + 10, "", style_achivement)
        worksheet.write(row + 5, col + 11, "", style_achivement)
        worksheet.write(row + 6, col + 7, "Average GP", style_total)
        worksheet.write(row + 7, col + 7, "Grand Total", style_total)
        worksheet.write(row + 3, col + 10, "%.2f" % inv_total, style_total)
        worksheet.write(row + 3, col + 14, "%.2f" % collection, style_total)
        worksheet.write(row + 3, col + 15, "%.2f" % comission_total, style_total)
        worksheet.write(row + 14, col + 7, "Rizwan Amir Ali", style_data3)
        worksheet.write(row + 14, col + 10, "Mr. Mamoun Khalifa", style_data3)
        worksheet.write(row + 14, col + 14, "Mr. Farrukh Khan", style_data3)
        worksheet.write(
            row + 7, col + 13, "Eligible commission 1.5 % of total Sales", style_data3
        )
        workbook.close()
        f = open(f_name, "rb")
        data = f.read()
        f.close()
        name = "%s.xlsx" % ("IncentiveReport_" + str(datetime.now() or ""))
        incentive_report = self.env["incentive.report"].create(
            {"file_name": name, "file_data": base64.encodebytes(data)}
        )
        view_id = self.env.ref("fs_incentive_report.incentive_report_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "incentive.report",
            "target": "new",
            "view_mode": "form",
            "res_id": incentive_report.id,
            "views": [[view_id, "form"]],
            "context": {"download_incentive_report": True},
        }
