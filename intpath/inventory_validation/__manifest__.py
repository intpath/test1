# -*- coding: utf-8 -*-
{
    'name': "Odoo Inventory Customisation",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Nikunj Dhameliya",
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/users_view.xml',
        'views/stock_picking_views.xml',
        'report/report_stockpicking_operations.xml'
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'sale', 'stock',
    ],
    'qweb': [
     ],
    'description': "Odoo Inventory Customisation",
    'installable': True,
    'summary': "Odoo Inventory Customisation",
    'test': [],
    'version': "1.0.1",
    'website': "https://www.fiverr.com/nikunjd",
}
