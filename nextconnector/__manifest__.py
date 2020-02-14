# -*- coding: utf-8 -*-
{
    'name': "Next-Connector",

    'summary': "Connect CRM With ERP",

    'description': "Connect CRM With ERP",

    'author': "Next-pro",
    'website': "http://www.nextpro.pe",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'application': True,
    'version': '0.1',
    'images': [
        'static/description/logo_empresa.jpg',
    ],

    # any module necessary for this one to work correctly
    'depends': ['base','crm',"sale"],

    # always loaded
    'data': [
        # vistas de formulario/ listas
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/popup_message_wizard.xml',
        'views/sales_rep_view.xml',
        'views/nextconnector_automated_actions.xml',
        'views/nextconnector_menu_import.xml',
        'views/nextconnector_menu_master_data.xml',
        'views/account_payment_term_views.xml',
        #data

        # seguridad
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': True
}