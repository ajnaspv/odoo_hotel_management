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