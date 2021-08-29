# -*- coding: utf-8 -*-
{
    'name': "POS Products Quantity",
    'summary': """This module will get the quantity of the POS product based on the location and show a warning if the user exceeded that quantity.""",
    'description': """ This module will get the quantity of the POS product based on the location and show a warning if the user exceeded that quantity. """,
    'author': "AliFaleh",
    'website': "http://www.int-path.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/static_loader.xml',
    ],
    'qweb': ['static/src/xml/quantity_holder.xml'],
    'demo': [],
}
