from odoo import fields, models,api
from openpyxl.worksheet import related


class HotelFoodOreders(models.Model):
    _name = 'hotel.food.orders'
    _description = 'Hotel Food Orders'
    _rec_name = 'room_id'

    room_id = fields.Many2one('hotel.accommodation', readonly=False, domain="[('state', '=', 'check_in')]",required=True)
    guest_name = fields.Char(string='Guest Name')
    order_date = fields.Datetime(string='Order Date',default=fields.Datetime.now, readonly=True)
    category_ids = fields.Many2many('hotel.foods.category', string='Categories')
    food_ids = fields.Many2many('hotel.foods', string='Foods', domain="[('category_id','in', category_ids)] if category_ids else []")
    order_line_ids = fields.One2many('hotel.food.order.lines','order_id', string='Order Lines')

    @api.onchange('room_id')
    def _onchange_room_id(self):
        """ On change room id select guest name
        guest_id, room_id is used
        return guest name"""
        self.guest_name = self.room_id.guest_id.name

    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        """ On change category ids select guest name"""
        self.food_ids = self.env['hotel.foods'].search([('category_id', 'in', self.category_ids)])