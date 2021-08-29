# -*- coding: utf-8 -*-
{
    'name': "Odoo POS Draft Invoice",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Nikunj Dhameliya",
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'report/report_invoice.xml',
        'views/point_of_sale_report.xml',
        'views/pos_view.xml',
        'views/invoice_report.xml',
        'views/pos_config_view.xml',
        'views/templates.xml'
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'account', 'point_of_sale'
    ],
    'qweb': [
     ],
    'description': "Odoo POS Draft Invoice",
    'installable': True,
    'summary': "Odoo POS Draft Invoice",
    'test': [],
    'version': "1.0.1",
}
