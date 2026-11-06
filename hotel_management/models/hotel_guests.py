from odoo import fields,models


class HotelGuests(models.Model):
    _name = 'hotel.guests'
    _description = 'Hotel Guests'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner',string="Guest Name")
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male','Male'),
        ('female','Female'),
        ('other','Other')
    ])
    additional_guests_id = fields.Many2one('hotel.accommodation',string="Additional Guest id")