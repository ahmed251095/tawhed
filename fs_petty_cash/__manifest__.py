# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    "name": "Petty Cash",
    "version": "15.0.0.0",
    "summary": "",
    "category": "Extra Addons",
    "description": """
    """,
    "author": "Chirag/fidobe",
    "website": "www.fidobe.com",
    "depends": ["base", "account"],
    "data": [
        # "security/ir.model.access.csv",
        "report/petty_cash_external_layout.xml",
        "report/report_petty_cash.xml",
        "report/report_petty_cash_document.xml",
        "report/report_payment_receipt_templates.xml",
        "views/res_company_view.xml",
        "views/account_journal_view.xml",
        "views/account_payment_view.xml",
        "views/petty_cash_view.xml",
        "wizard/account_payment_register_view.xml",
    ],
    "demo": [],
    "external_dependencies": {},
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
