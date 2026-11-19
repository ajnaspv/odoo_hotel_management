from odoo import fields, models


class HotelRoomFacilities(models.Model):
    _name = "hotel.rooms.facilities"
    _description = "Hotel Facilities"

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    name = fields.Char(string="Name")