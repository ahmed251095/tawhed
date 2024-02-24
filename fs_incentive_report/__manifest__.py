# -*- coding: utf-8 -*-
{
    "name": "Incentive Report",
    "version": "15.0.0.0",
    "summary": "Incentive Report",
    "category": "Extra Addons",
    "description": """Incentive Report""",
    "author": "Chirag/fidobe",
    "website": "www.fidobe.com",
    "depends": ["base", "account", "project", "sale", "odoo_job_costing_management"],
    "data": [
        "security/incentive_security.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "wizard/incentive_report_view.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
