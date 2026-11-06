from odoo import fields, models, api


class HotelRooms(models.Model):
    _name = "hotel.rooms"
    _description = "Hotel Room"
    _rec_name = "room_number"

    room_number = fields.Char(string="Room Number")
    bed_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),
    ])
    available_beds = fields.Integer(string="Available Beds")
    rent = fields.Monetary(string="Nightly Rent/rate")
    facilities_id =fields.Many2many('hotel.rooms.facilities',string="Facilities")
    state = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ],default='available')
    currency_id = fields.Many2one('res.currency', string="Currency",default=lambda self: self.env.user.company_id.currency_id.id)