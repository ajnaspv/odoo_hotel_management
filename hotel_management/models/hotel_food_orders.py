from odoo import fields, models
from openpyxl.worksheet import related


class HotelFoodOreders(models.Model):
    _name = 'hotel.food.orders'
    _description = 'Hotel Food Orders'

    accommodation_ids= fields.Many2many('hotel.accommodation', string='Room')
    room_id= fields.Many2one('hotel.rooms', string='Room', domain=[('state', '=', 'not_available')])
    guest = fields.Many2one(related='accommodation_ids.guest_id', string='Guest', readonly=False)
    order_date = fields.Datetime(string="Order Date", default=fields.Date.today())
