from odoo import api, fields, models

class HotelFoodOrderQuantityWizard(models.TransientModel):
    _name = "hotel.food.order.quantity.wizard"
    _description = "Hotel Food Order Quantity Wizard"
    food_item_name = fields.Char(string="Food Name", readonly=True)

    order_qty = fields.Integer(string='Quantity')
    food_item_id = fields.Many2one(
        'hotel.foods',
        default=lambda self: self.env.context.get('food_item_id')
    )
    food_image = fields.Image(related='food_item_id.image', readonly=True)

    def action_qty_entry(self):

        self.env['hotel.food.order.lines'].create({
            'food_item_id': self.env.context.get('food_item_id'),
            'food_qty': self.order_qty,
            'order_id': self.env.context.get('default_order_id'),
            'price' : self.env.context.get('price'),
            'order_room_id': self.env.context.get('order_room_id'),
            'food_order_reference' : self.env.context.get('food_order_reference'),
        })