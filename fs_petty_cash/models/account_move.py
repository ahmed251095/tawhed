from odoo import fields, api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_petty_cash = fields.Boolean(string="Is Petty Cash")
    payee = fields.Text(string="Payee")
    document_description = fields.Char(string="Document Description")
    cheque_date = fields.Date("Cheque Date")
    cheque_no = fields.Char("Cheque Number")
    mode_of_payment = fields.Selection(
        [("bank", "Bank"), ("cash", "Cash"), ("tt", "TT")], string="Mode Of Payment"
    )

    @api.model
    def _search_default_journal(self, journal_types):
        journal = super(AccountMove, self)._search_default_journal(journal_types)
        if self._context.get("default_is_petty_cash"):
            journal = self.env["account.journal"].search(
                [("is_petty_cash_journal", "=", True)], limit=1
            )
        return journal

    @api.depends("company_id", "invoice_filter_type_domain")
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or "general"
            company_id = m.company_id.id or self.env.company.id
            if m.is_petty_cash:
                domain = [
                    ("company_id", "=", company_id),
                ]
                # ("is_petty_cash_journal", "=", True),
            else:
                # ("type", "=", journal_type)
                domain = [("company_id", "=", company_id)]
            m.suitable_journal_ids = self.env["account.journal"].search(domain)
