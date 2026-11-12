from odoo import api, fields, models

class HotelPayments(models.Model):
    _name = 'hotel.payments'
    _description = 'Hotel Payments'

    description = fields.Char('Hotel Payments')
    quantity = fields.Integer('Quantity')
    uom= fields.Char('UoM')
    unit_price = fields.Float('Unit Price')
    subtotal = fields.Float('Subtotal')
    accommodation_id = fields.Many2one('hotel.accommodation')
