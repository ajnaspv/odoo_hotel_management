from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_hotel_guest = fields.Boolean(string="Is Hotel Guest")