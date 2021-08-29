# -*- coding: utf-8 -*-
{
    'name': "Odoo Payment Internal Transfer",  # Name first, others listed in alphabetical order
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
        'sale', 'sale_management', 'inventory_validation', 'account'
    ],
    'qweb': [
     ],
    'description': "Odoo Payment Internal Transfer",
    'installable': True,
    'summary': "Odoo Payment Internal Transfer",
    'test': [],
    'version': "13.0.0.1"
}
