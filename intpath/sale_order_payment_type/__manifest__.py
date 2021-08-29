# -*- coding: utf-8 -*-
{
    'name': "Sale Order Payment Type",

    'summary': """
        This module will add payment type field to sale order form and report.""",

    'description': """
        This module will add payment type field to sale order form and report.
    """,

    'author': "Int-Path",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale Order',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'sale', 'sale_management', 'inventory_validation'],

    # always loaded
    'data': [
        'views/sale_order_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
