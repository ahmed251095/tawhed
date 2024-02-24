# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, create_index
from odoo.tools.float_utils import float_compare


class InventoryAdjustment(models.Model):
    _inherit = "stock.quant"

    force_date = fields.Datetime(string="Force Date")

    @api.model
    def _get_inventory_fields_create(self):
        """Returns a list of fields user can edit when he want to create a quant in `inventory_mode`."""
        return [
            "product_id",
            "location_id",
            "lot_id",
            "package_id",
            "owner_id",
        ] + self._get_inventory_fields_write()

    @api.model
    def _get_inventory_fields_write(self):
        """Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`."""
        fields = [
            "inventory_quantity",
            "inventory_quantity_auto_apply",
            "inventory_diff_quantity",
            "inventory_date",
            "user_id",
            "inventory_quantity_set",
            "is_outdated",
            "force_date",
        ]
        return fields

    def _apply_inventory(self):
        move_vals = []
        if not self.user_has_groups("stock.group_stock_manager"):
            raise UserError(
                _("Only a stock manager can validate an inventory adjustment.")
            )
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if (
                float_compare(
                    quant.inventory_diff_quantity,
                    0,
                    precision_rounding=quant.product_uom_id.rounding,
                )
                > 0
            ):
                move_vals.append(
                    quant._get_inventory_move_values(
                        quant.inventory_diff_quantity,
                        quant.product_id.with_company(
                            quant.company_id
                        ).property_stock_inventory,
                        quant.location_id,
                    )
                )
            else:
                move_vals.append(
                    quant._get_inventory_move_values(
                        -quant.inventory_diff_quantity,
                        quant.location_id,
                        quant.product_id.with_company(
                            quant.company_id
                        ).property_stock_inventory,
                        out=True,
                    )
                )
        moves = (
            self.env["stock.move"].with_context(inventory_mode=False).create(move_vals)
        )
        moves._action_done()
        for quant in self:
            if quant.force_date:
                for move in moves:
                    svl = self.env["stock.valuation.layer"].search(
                        [("stock_move_id", "=", move.id)], limit=1
                    )
                    if svl:
                        self.env.cr.execute(
                            "UPDATE public.stock_valuation_layer SET create_date=%s WHERE id=%s ",
                            (quant.force_date, svl.id),
                        )
                        # svl.create_date = self.force_date or move.picking_id.force_date
                        name = svl.account_move_id.name.split("/")
                        year = str(quant.force_date.year)
                        month = str(quant.force_date.month)
                        if len(month) == 1:
                            month = "0" + month
                        journal_name = (
                            name[0] + "/" + year + "/" + month + "/" + name[3]
                        )
                        svl.account_move_id.write(
                            {"name": journal_name, "date": quant.force_date}
                        )
                        svl.account_move_id.line_ids.write({"date": quant.force_date})
                    move.write({"date": quant.force_date})
                    # svl.write({"create_date": self.force_date})
            quant.location_id.write({"last_inventory_date": fields.Date.today()})
            date_by_location = {
                loc: loc._get_next_inventory_date()
                for loc in quant.mapped("location_id")
            }
            quant.inventory_date = date_by_location[quant.location_id]
            quant.write({"inventory_quantity": 0, "user_id": False})
            quant.write({"inventory_diff_quantity": 0})


class StockPicking(models.Model):
    _inherit = "stock.picking"

    force_date = fields.Datetime(string="Force Date")
    scheduled_date = fields.Datetime(compute="_compute_scheduled_date", store=True)

    @api.depends("force_date")
    def _compute_scheduled_date(self):
        for picking in self:
            if picking.force_date:
                picking.scheduled_date = picking.force_date


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_vals(
        self,
        credit_account_id,
        debit_account_id,
        journal_id,
        qty,
        description,
        svl_id,
        cost,
    ):
        self.ensure_one()
        move_lines = self._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, description
        )
        date = self._context.get("force_period_date", fields.Date.context_today(self))
        if self.env.user.has_group("stock_force_date_app.group_stock_force_date"):
            if self.picking_id.force_date:
                self.date = self.picking_id.force_date.date()
                date = self.picking_id.force_date.date()
        return {
            "journal_id": journal_id,
            "line_ids": move_lines,
            "date": date,
            "ref": description,
            "stock_move_id": self.id,
            "stock_valuation_layer_ids": [(6, None, [svl_id])],
            "move_type": "entry",
        }


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    def init(self):
        create_index(
            self._cr,
            "stock_valuation_layer_index",
            self._table,
            [
                "product_id",
                "remaining_qty",
                "stock_move_id",
                "company_id",
                # "create_date",
            ],
        )

    def _validate_accounting_entries(self):
        am_vals = []
        for svl in self:
            if not svl.product_id.valuation == "real_time":
                continue
            if svl.currency_id.is_zero(svl.value):
                continue
            if svl.stock_move_id.picking_id.force_date:
                self.env.cr.execute(
                    "UPDATE public.stock_valuation_layer SET create_date=%s WHERE id=%s ",
                    (svl.stock_move_id.picking_id.force_date, svl.id),
                )
                # svl.create_date = svl.stock_move_id.picking_id.force_date
            am_vals += svl.stock_move_id._account_entry_move(
                svl.quantity, svl.description, svl.id, svl.value
            )
        if am_vals:
            account_moves = self.env["account.move"].sudo().create(am_vals)
            if svl.stock_move_id.picking_id.property_stock_account_input_categ_id:
                for move in account_moves:
                    move.line_ids[0].write(
                        {
                            "account_id": svl.stock_move_id.picking_id.property_stock_account_input_categ_id.id
                        }
                    )
            account_moves._post()
        for svl in self:
            # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            if svl.company_id.anglo_saxon_accounting:
                svl.stock_move_id._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(
                    product=svl.product_id
                )
