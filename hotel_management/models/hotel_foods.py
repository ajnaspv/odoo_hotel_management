from odoo import fields, models


class HotelFoods(models.Model):
    _name = 'hotel.foods'
    _description = 'Hotel Foods'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    image = fields.Image(string='Image')
    category_id = fields.Many2one('hotel.foods.category',string='Category')
    price = fields.Monetary(string='Price')
    available_qty = fields.Integer(string='Available Quantity')
    currency_id = fields.Many2one('res.currency', string="Currency",default=lambda self: self.env.user.company_id.currency_id.id)
    order_qty = fields.Integer(string='Order Quantity')

    def action_qty_entry(self):
        # print("Context id:",self.env.context.get('default_order_id'))
        self.env['hotel.food.order.lines'].create({
            'food_item_id': self.id,
            'food_category_ids': self.category_id,
            'food_qty': self.order_qty,
            'price': self.price,
            'order_id': self.env.context.get('default_order_id'),
        })
