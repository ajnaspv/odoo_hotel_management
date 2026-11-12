from odoo import api, fields, models

class HotelFoodOrderLines(models.Model):
    _name = 'hotel.food.order.lines'
    _description = 'Hotel Food Order Lines'

    food_item_id = fields.Many2one('hotel.foods')
    food_qty = fields.Integer('Food Qty')
    order_id = fields.Many2one('hotel.food.orders')
    description = fields.Char('Description')
    price = fields.Float('Price')
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)
    order_room_id = fields.Many2one('hotel.rooms')
    food_order_reference = fields.Char(string='Food Order Reference')

    @api.depends('food_qty', 'price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.food_qty * record.price


