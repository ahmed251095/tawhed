# -*- coding: utf-8 -*-

{
    'name': "Accounting Enhancement",
    'version': '1.0',
    'summary': "new fields in payment",
    'description': """
       new fields in payment
    """,
    'author': "Ahmed",
    'website': "",
    'category': '',
    'depends': [
        'base',
        'account',
        'hr',
    ],
    'data': [
        'views/account_payment.xml',
    ],

    'installable': True,
    'auto_install': False,
}
