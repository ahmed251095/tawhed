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
    "name": "Sitaram Custom Reports",
    "version": "15.0.0.0",
    "summary": "",
    "category": "Extra Addons",
    "description": """
    
    """,
    "author": "Sitaram",
    "website": "www.sitaramsolutions.in",
    "depends": ["base", "sale", "purchase", "account", "stock", "sale_management"],
    "data": [
        # "security/ir.model.access.csv",
        "data/paper_format_data.xml",
        "reports/sr_invoice_report.xml",
        "reports/sr_purchase_report.xml",
        "reports/sr_sale_report.xml",
        "reports/sr_invoice_report_without_header_footer.xml",
        "reports/report_payment_receipt_template.xml",
        "reports/sr_dub_sale_report.xml",
        # "views/bank_detail_view.xml",
        "views/sale_view.xml",
        "views/account_move_view.xml",
        "views/picking_view.xml",
        # 'reports/sr_stock_report.xml',
    ],
    "demo": [],
    "external_dependencies": {},
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
