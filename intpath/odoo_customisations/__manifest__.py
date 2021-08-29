# -*- coding: utf-8 -*-
{
    'name': "Odoo MRP Customisation",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Nikunj Dhameliya",
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'views/sale_order_view.xml',
        'views/account_journal_view.xml'
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'mrp', 'sale', 'sale_management', 'inventory_validation'
    ],
    'qweb': [
     ],
    'description': "Set qty 1 on work order",
    'installable': True,
    'summary': "Odoo MRP Customisation",
    'test': [],
    'version': "1.0.1",
    'website': "https://www.fiverr.com/nikunjd",
}
