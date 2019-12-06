# -*- coding: utf-8 -*-

from odoo import models, fields


class Survey(models.Model):
    _inherit = 'survey.survey'

    expires = fields.Integer(string="Expires In (months)")

    def action_certifications_export(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Export data",
            'target': 'blank',
            'url': "/certifications_export/export"
        }

    def action_certifications_export_self(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Export data",
            'target': 'blank',
            'url': "/certifications_export/export/?certs=%s" % (self.id)
        }
