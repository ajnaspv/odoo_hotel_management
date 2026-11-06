from odoo import fields, models


class HotelFacilities(models.Model):
    _name = "hotel.facilities"
    _description = "Hotel Facilities"

    name = fields.Char(string="Name")