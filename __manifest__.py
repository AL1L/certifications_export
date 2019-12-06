# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Certifications Export",
    'summary': 'Modify Odoo to better track and manage eLearning and empolyee Training',
    'description': """Modify Odoo to better track and manage eLearning and empolyee Training""",
    'website': "https://docs.google.com/document/d/1iU890IC8wAx3aSGntsKDihk4ZReMatiKecmKhnQWrMw/edit",
    'category': 'Survey',
    'version': '1.0',
    'depends': ['website_slides', 'survey'],
    'installable': True,
    'auto_install': True,
    'data': [
        'views/survey_export.xml'
    ],
    'demo': [],
}
