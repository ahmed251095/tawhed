from odoo import models, api, fields, _
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    invoice_date = fields.Date(string="Inv Date")
    invoice_no = fields.Char(string="Invoice no")
    invoice_user_id = fields.Many2one("res.users", string="Sales Person")
    contact = fields.Char(string="Contact")
    project_no = fields.Char(string="Project no")
    lpo = fields.Char("LPO")
    opportunity_id = fields.Many2one("crm.lead", string="Subject")
    invoice_amt = fields.Monetary("Invoice Amt")
    amount_due = fields.Monetary("Amount Due")
    ref = fields.Char("Reference")

    @api.model
    def _get_column_details(self, options):
        # self._field_column("expected_pay_date"),
        columns = [
            self._header_column(),
            self._field_column("invoice_date"),
            self._field_column("report_date"),
            self._field_column("invoice_no"),
            self._field_column("invoice_user_id"),
            self._field_column("contact"),
            self._field_column("project_no"),
            self._field_column("lpo"),
            self._field_column('ref'),
            self._field_column("opportunity_id"),
            # self._field_column("account_name", name=_("Account"), ellipsis=True),
            self._field_column("invoice_amt"),
            self._field_column("amount_due"),
            self._field_column(
                "period0",
                name=_("As of: %s", format_date(self.env, options["date"]["date_to"])),
            ),
            self._field_column("period1", sortable=True),
            self._field_column("period2", sortable=True),
            self._field_column("period3", sortable=True),
            self._field_column("period4", sortable=True),
            self._field_column("period5", sortable=True),
            self._custom_column(  # Avoid doing twice the sub-select in the view
                name=_("Total"),
                classes=["number"],
                formatter=self.format_value,
                getter=(
                    lambda v: v["period0"]
                    + v["period1"]
                    + v["period2"]
                    + v["period3"]
                    + v["period4"]
                    + v["period5"]
                ),
                sortable=True,
            ),
        ]

        # if self.user_has_groups("base.group_multi_currency"):
        #     columns[2:2] = [
        #         self._field_column("amount_currency"),
        #         self._field_column("currency_id"),
        #     ]
        return columns

    @api.model
    def _get_sql(self):
        options = self.env.context["report_options"]
        query = (
            """
            SELECT
                {move_line_fields},
                account_move_line.amount_currency as amount_currency,
                account_move_line.partner_id AS partner_id,
                partner.name AS partner_name,
                COALESCE(trust_property.value_text, 'normal') AS partner_trust,
                COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
                account_move_line.payment_id AS payment_id,
                move.invoice_date As invoice_date,
                COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
                move.name As invoice_no,
                move.invoice_user_id as invoice_user_id,
                move.contact As contact,
                move.project_no As project_no,
                move.lpo As lpo,
                move.ref As ref,
                move.opportunity_id As opportunity_id,
                account_move_line.expected_pay_date AS expected_pay_date,
                move.amount_total As invoice_amt,
                move.amount_residual As amount_due,
                move.move_type AS move_type,
                move.name AS move_name,
                move.ref AS move_ref,
                account.code || ' ' || account.name AS account_name,
                account.code AS account_code,"""
            + ",".join(
                [
                    (
                        """
                CASE WHEN period_table.period_index = {i}
                THEN %(sign)s * ROUND((
                    account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
                ) * currency_table.rate, currency_table.precision)
                ELSE 0 END AS period{i}"""
                    ).format(i=i)
                    for i in range(6)
                ]
            )
            + """
            FROM account_move_line
            JOIN account_move move ON account_move_line.move_id = move.id
            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            JOIN account_account account ON account.id = account_move_line.account_id
            JOIN res_partner partner ON partner.id = account_move_line.partner_id
            LEFT JOIN ir_property trust_property ON (
                trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
                AND trust_property.name = 'trust'
                AND trust_property.company_id = account_move_line.company_id
            )
            JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN LATERAL (
                SELECT part.amount, part.debit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date)s
            ) part_debit ON part_debit.debit_move_id = account_move_line.id
            LEFT JOIN LATERAL (
                SELECT part.amount, part.credit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date)s
            ) part_credit ON part_credit.credit_move_id = account_move_line.id
            JOIN {period_table} ON (
                period_table.date_start IS NULL
                OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
            )
            AND (
                period_table.date_stop IS NULL
                OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
            )
            WHERE account.internal_type = %(account_type)s
            AND account.exclude_from_aged_reports IS NOT TRUE
            GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
                     period_table.period_index, currency_table.rate, currency_table.precision
            HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
        """
        ).format(
            move_line_fields=self._get_move_line_fields("account_move_line"),
            currency_table=self.env["res.currency"]._get_query_currency_table(options),
            period_table=self._get_query_period_table(options),
        )
        params = {
            "account_type": options["filter_account_type"],
            "sign": 1 if options["filter_account_type"] == "receivable" else -1,
            "date": options["date"]["date_to"],
        }
        return self.env.cr.mogrify(query, params).decode(
            self.env.cr.connection.encoding
        )
