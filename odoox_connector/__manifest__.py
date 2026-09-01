# -*- coding: utf-8 -*-
{
    'name': 'OdooX ULTRON Payment Recovery Connector',
    'version': '1.0.0',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Autonomous Failed-Payment Recovery integration with ULTRON control plane',
    'description': """
OdooX ULTRON Connector
======================
Automatically streams failed payment transactions from Odoo checkouts directly
into the ULTRON recovery engine for IVEN economic scoring and automated Razorpay
payment recovery link generation.
    """,
    'author': 'OdooX',
    'website': 'https://odoox.com',
    'depends': ['payment', 'sale'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
