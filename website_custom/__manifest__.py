# website_custom/__manifest__.py

{
    'name': 'Website Custom',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Customizations for the website module',
    'author': 'Your Name',
    'depends': ['website'],
    'data': [
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_custom/static/src/css/style.css',
        ],
    },
}
