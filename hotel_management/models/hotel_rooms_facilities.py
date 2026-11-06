from odoo import fields, models


class HotelRoomFacilities(models.Model):
    _name = "hotel.rooms.facilities"
    _description = "Hotel Facilities"

    name = fields.Char(string="Name")