from odoo import fields, models


class HotelFoodsCategory(models.Model):
    _name = 'hotel.foods.category'
    _description = 'Hotel Foods Category'

    name = fields.Char(string='Name')