from odoo import fields, models


class HotelFoodsCategory(models.Model):
    _name = 'hotel.foods.category'
    _description = 'Hotel Foods Category'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    name = fields.Char(string='Name')