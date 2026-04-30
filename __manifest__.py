# -*- coding: utf-8 -*-
{
    'name': 'SID Nonconformity Management',
    'version': '15.0.1.0.0',
    'category': 'Quality',
    'summary': 'Simple nonconformity tracking for ISO 9001/14001 distribution workflows.',
    'author': 'SIDSA / OV',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'stock',
        'purchase',
        'sale_management',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/sid_nonconformity_report.xml',
        'views/sid_nonconformity_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}
