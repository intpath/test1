# -*- coding: utf-8 -*-
{
    'name': "add account invoice",

    'summary': """
        This module willadd the account receivable in the invoices""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Integrated Path",
    'website': "https://www.int-path.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

