# -*- coding: utf-8 -*-
{
    'name': "expense_report_journal",

    'summary': """
        This module is to modify some fields in the expense report""",

    'description': """
        This module is to modify some fields in the 
        expense report by substituting the payment by with 
        journal entry and name with account
    """,

    'author': "Omer Aiman",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/expense_report_journal.xml',
    ],
    # only loaded in demonstration mode
}
