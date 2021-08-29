# -*- coding: utf-8 -*-
{
    'name': "Odoo Inventory Customisation",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Nikunj Dhameliya",
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'report/stock_move_report.xml',
        'views/stock_moves.xml',
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
