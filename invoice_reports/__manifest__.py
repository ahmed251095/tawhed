# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "invoice_reports",
    "summary": "invoice_reports",
    'sequence': 1,
    'category': 'account',
    'version': '16',
    "depends": [
       "account",
        'base',
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/account_move.xml",
        "reports/header_report_template.xml",
        "reports/invoices_report.xml",
    ],
    'installable': True,
}
