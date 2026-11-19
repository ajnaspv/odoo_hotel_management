from odoo import fields, models


class HotelFoods(models.Model):
    _name = 'hotel.foods'
    _description = 'Hotel Foods'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    image = fields.Image(string='Image')
    category_id = fields.Many2one('hotel.foods.category',string='Category', required=True)
    price = fields.Monetary(string='Price', required=True)
    available_qty = fields.Integer(string='Available Quantity')
    currency_id = fields.Many2one('res.currency', string="Currency",default=lambda self: self.env.user.company_id.currency_id.id)

    def action_hotel_food_order_quantity_wizard(self):
        """Food order quantity entry wizard
        food_item_id, quantity, price, default_order_id, order_room_id, food_order_reference are used
        Return food order quantity wizard popup"""
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

    def create_food_product(self):
        """Create Food As a Product in product.template
        name, price, image are used
        Return food product created in product.template"""
        self.env['product.template'].create({
            'name': self.name,
            'image_1920': self.image,
            'list_price': self.price,
        })