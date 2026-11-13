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
    # order_qty = fields.Integer(string='Order Quantity')

    # def action_qty_entry(self):
    #     # print("Context id:",self.env.context.get('default_order_id'))
    #     self.env['hotel.food.order.lines'].create({
    #         'food_item_id': self.id,
    #         'food_category_ids': self.category_id,
    #         'food_qty': self.order_qty,
    #         'price': self.price,
    #         'order_id': self.env.context.get('default_order_id'),
    #     })

    def action_hotel_food_order_quantity_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quantity Entry',
            'res_model': 'hotel.food.order.quantity.wizard',
            'view_mode': 'form',
            'target': 'new',  # optional: opens as popup
            'context': {
                'food_item_id': self.id,
                'price': self.price,
                'default_order_id': self.env.context.get('default_order_id'),
                'order_room_id': self.env.context.get('order_room_id'),
                'food_order_reference' : self.env.context.get('food_order_reference'),
                'default_food_item_name': self.name,
            },
        }
