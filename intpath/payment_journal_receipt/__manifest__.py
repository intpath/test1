# -*- coding: utf-8 -*-
{
    'name': "payment_journal_receipt",

    'summary': """
        adding journal to receipt""",

    'description': """
        adding journal to receipt
    """,

    'author': "Omer Aiman",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'reports/payment_receipt_journal.xml',
    ],

    'installable': True,
}
