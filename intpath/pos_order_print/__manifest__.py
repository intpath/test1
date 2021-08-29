# -*- coding: utf-8 -*-

{
    'name': 'POS Order Print',
    'version': '13.0.1.0.0',
    'summary': 'Print Order from Point of Sale Screen',
    'category': 'Point of Sale',
    'description': """" Display all pos order when user press show order button
        and also user can print report from there.""",
    'author': '',
    'depends': ['point_of_sale'],
    'data': [
            'views/pos_template.xml',
            'views/pos_order.xml',
            ],
    'qweb': ['static/src/xml/print_order.xml',
             'static/src/xml/show_order.xml'],
}
