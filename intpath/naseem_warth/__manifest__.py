# -*- coding: utf-8 -*-
{
    'name': "Naseem Warth",

    'summary': """
        An extenions module for Naseem Warth.
        Developed By Integrated Path""",

    'author': "Intergrated Path",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'account', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/invoice_receipt_ext.xml',
        'report/delievery_report.xml',
        # 'views/assets.xml' #this
    ],

    'qweb': [
        'report/pos_receipt_ext.xml',
        'report/delievery_report.xml',
    ],
}
