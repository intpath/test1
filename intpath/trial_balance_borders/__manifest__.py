# -*- coding: utf-8 -*-
{
    'name': "Trial Balance Borders",

    'summary': """
        This module will add borders to the trial balance report in the Acountant module.""",

    'description': """
        This module will add borders to the trial balance report in the Acountant module.
    """,

    'author': "Int-Path",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/css_loader.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
