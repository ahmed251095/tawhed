# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class Move(models.Model):
    _inherit = 'account.move'
    address = fields.Char()
    company_name = fields.Many2one('company.company','Company Name')

class Company(models.Model):
    _name = 'company.company'

    name = fields.Char()
    address = fields.Char()


