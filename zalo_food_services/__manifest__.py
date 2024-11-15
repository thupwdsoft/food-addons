{
    'name': 'Food Zalo Services',
    'version': '1.0',
    'author': 'nvt',
    'category': 'Food',
    'depends': ['base', 'website'],  # Add other necessary modules if needed
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/category_view.xml',
        'views/product_view.xml',
        'views/order_view.xml',
    ],
    'installable': True,
    'application': True,
    'description': 'Module to integrate food ordering with Zalo for Odoo',
}
