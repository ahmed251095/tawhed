from odoo import fields, api, models, _
from odoo.tools.misc import formatLang
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = "account.move"

    contact = fields.Char("Contact", store=True)
    lpo = fields.Char("LPO", store=True)
    opportunity_id = fields.Many2one("crm.lead", string="Subject", store=True)
    project_no = fields.Char("Project no", store=True)
    purchase_reference = fields.Char("Purchase Reference")
    text1 = fields.Char("Text", compute="_compute_set_from_sale", compute_sudo=True)
    # bank_detail_id = fields.Text("bank.detail", string="Bank Details")

    def _compute_set_from_sale(self):
        for invoice in self:
            sale_id = self.env["sale.order"].search(
                [("invoice_ids", "in", invoice.ids)], limit=1
            )
            invoice.text1 = ""
            invoice.contact = sale_id.contact
            invoice.opportunity_id = sale_id.crm_lead_id.id
            invoice.project_no = sale_id.opportunity_project_id.job_number

    @api.model
    def _get_tax_totals(
        self, partner, tax_lines_data, amount_total, amount_untaxed, currency
    ):
        """Compute the tax totals for the provided data.

        :param partner:        The partner to compute totals for
        :param tax_lines_data: All the data about the base and tax lines as a list of dictionaries.
                               Each dictionary represents an amount that needs to be added to either a tax base or amount.
                               A tax amount looks like:
                                   {
                                       'line_key':             unique identifier,
                                       'tax_amount':           the amount computed for this tax
                                       'tax':                  the account.tax object this tax line was made from
                                   }
                               For base amounts:
                                   {
                                       'line_key':             unique identifier,
                                       'base_amount':          the amount to add to the base of the tax
                                       'tax':                  the tax basing itself on this amount
                                       'tax_affecting_base':   (optional key) the tax whose tax line is having the impact
                                                               denoted by 'base_amount' on the base of the tax, in case of taxes
                                                               affecting the base of subsequent ones.
                                   }
        :param amount_total:   Total amount, with taxes.
        :param amount_untaxed: Total amount without taxes.
        :param currency:       The currency in which the amounts are computed.

        :return: A dictionary in the following form:
            {
                'amount_total':                              The total amount to be displayed on the document, including every total types.
                'amount_untaxed':                            The untaxed amount to be displayed on the document.
                'formatted_amount_total':                    Same as amount_total, but as a string formatted accordingly with partner's locale.
                'formatted_amount_untaxed':                  Same as amount_untaxed, but as a string formatted accordingly with partner's locale.
                'allow_tax_edition':                         True if the user should have the ability to manually edit the tax amounts by group
                                                             to fix rounding errors.
                'groups_by_subtotals':                       A dictionary formed liked {'subtotal': groups_data}
                                                             Where total_type is a subtotal name defined on a tax group, or the default one: 'Untaxed Amount'.
                                                             And groups_data is a list of dict in the following form:
                                                                {
                                                                    'tax_group_name':                  The name of the tax groups this total is made for.
                                                                    'tax_group_amount':                The total tax amount in this tax group.
                                                                    'tax_group_base_amount':           The base amount for this tax group.
                                                                    'formatted_tax_group_amount':      Same as tax_group_amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                    'formatted_tax_group_base_amount': Same as tax_group_base_amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                    'tax_group_id':                    The id of the tax group corresponding to this dict.
                                                                    'group_key':                       A unique key identifying this total dict,
                                                                }
                'subtotals':                                 A list of dictionaries in the following form, one for each subtotal in groups_by_subtotals' keys
                                                                {
                                                                    'name':                            The name of the subtotal
                                                                    'amount':                          The total amount for this subtotal, summing all
                                                                                                       the tax groups belonging to preceding subtotals and the base amount
                                                                    'formatted_amount':                Same as amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                }
            }
        """
        lang_env = self.with_context(lang=partner.lang).env
        account_tax = self.env["account.tax"]

        grouped_taxes = defaultdict(
            lambda: defaultdict(
                lambda: {"base_amount": 0.0, "tax_amount": 0.0, "base_line_keys": set()}
            )
        )
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data["tax"].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("PreVAT Amount")
                new_priority = 0

            if (
                subtotal_title not in subtotal_priorities
                or new_priority < subtotal_priorities[subtotal_title]
            ):
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if "base_amount" in line_data:
                # Base line
                if (
                    tax_group
                    == line_data.get("tax_affecting_base", account_tax).tax_group_id
                ):
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data["line_key"] not in tax_group_vals["base_line_keys"]:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals["base_line_keys"].add(line_data["line_key"])
                    tax_group_vals["base_amount"] += line_data["base_amount"]

            else:
                # Tax line
                tax_group_vals["tax_amount"] += line_data["tax_amount"]

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [
                {
                    "tax_group_name": group.name,
                    "tax_group_amount": amounts["tax_amount"],
                    "tax_group_base_amount": amounts["base_amount"],
                    "formatted_tax_group_amount": formatLang(
                        lang_env, amounts["tax_amount"], currency_obj=currency
                    ),
                    "formatted_tax_group_base_amount": formatLang(
                        lang_env, amounts["base_amount"], currency_obj=currency
                    ),
                    "tax_group_id": group.id,
                    "group_key": "%s-%s" % (subtotal_title, group.id),
                }
                for group, amounts in sorted(
                    groups.items(), key=lambda l: l[0].sequence
                )
            ]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = []  # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted(
            (sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]
        ):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append(
                {
                    "name": subtotal_title,
                    "amount": subtotal_value,
                    "formatted_amount": formatLang(
                        lang_env, subtotal_value, currency_obj=currency
                    ),
                }
            )

            subtotal_tax_amount = sum(
                group_val["tax_group_amount"]
                for group_val in groups_by_subtotal[subtotal_title]
            )
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            "amount_total": amount_total,
            "amount_untaxed": amount_untaxed,
            "formatted_amount_total": formatLang(
                lang_env, amount_total, currency_obj=currency
            ),
            "formatted_amount_untaxed": formatLang(
                lang_env, amount_untaxed, currency_obj=currency
            ),
            "groups_by_subtotal": groups_by_subtotal,
            "subtotals": subtotals_list,
            "allow_tax_edition": False,
        }
