# -*- coding: utf-8 -*-

from odoo import models, fields


class Survey(models.Model):
    _inherit = 'survey.survey'

    expires = fields.Integer(string="Expires In (months)")

    def action_firefly_export(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Export data",
            'target': 'blank',
            'url': "/firefly/export"
        }

    def action_firefly_export_self(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Export data",
            'target': 'blank',
            'url': "/firefly/export/?certs=%s" % (self.id)
        }
