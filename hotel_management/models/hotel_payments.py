from odoo import api, fields, models

class HotelPayments(models.Model):
    _name = 'hotel.payments'
    _description = 'Hotel Payments'

    description = fields.Char('Description')
    quantity = fields.Integer('Quantity')
    uom= fields.Char('UoM')
    unit_price = fields.Monetary('Unit Price')
    subtotal = fields.Monetary('Subtotal')
    accommodation_id = fields.Many2one('hotel.accommodation')
    order_reference = fields.Char('Order Reference')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id.id)