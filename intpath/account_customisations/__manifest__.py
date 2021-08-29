# -*- coding: utf-8 -*-
{
    'name': "Odoo Account Customisation",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Nikunj Dhameliya",
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'views/assets.xml',
        'report/report_payment_receipt_templates.xml',
        'views/search_template_view.xml',
        # 'views/account_report_view.xml'
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'account', 'account_reports'
    ],
    'qweb': [
     ],
    'description': "Odoo Account Customisation",
    'installable': True,
    'summary': "Odoo Account Customisation",
    'test': [],
    'version': "1.0.1",
    'website': "https://www.fiverr.com/nikunjd",
}
