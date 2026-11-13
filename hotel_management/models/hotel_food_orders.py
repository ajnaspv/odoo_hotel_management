from odoo import fields, models,api, _
from openpyxl.worksheet import related


class HotelFoodOreders(models.Model):
    _name = 'hotel.food.orders'
    _description = 'Hotel Food Orders'
    _rec_name = 'accommodation_id'

    accommodation_id = fields.Many2one('hotel.accommodation', readonly=False, domain="[('state', '=', 'check_in')]",required=True, string="Booking Id")
    rm_id = fields.Many2one('hotel.rooms', readonly=True, related='accommodation_id.room_id', string="Room Number")
    guest_name = fields.Char(string='Guest Name')
    order_date = fields.Datetime(string='Order Date',default=fields.Datetime.now, readonly=True)
    category_ids = fields.Many2many('hotel.foods.category', string='Categories')
    food_ids = fields.Many2many('hotel.foods', string='Foods', domain="[('category_id','in', category_ids)] if category_ids else []")
    order_line_ids = fields.One2many('hotel.food.order.lines','order_id', string='Order Lines')
    food_order_reference = fields.Char(string='Order Reference', readonly=True, default=lambda self: _('New'), copy=False)
    status = fields.Selection([('cancelled', 'Cancelled'),
                               ('confirmed','Confirmed'),],default='cancelled',string='Status')

    @api.onchange('accommodation_id')
    def _onchange_accommodation_id(self):
        """ On change room id select guest name
        guest_id, accommodation_id is used
        return guest name"""
        self.guest_name = self.accommodation_id.guest_id.name
        self.rm_id = self.accommodation_id.room_id

    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        """ On change category ids select guest name"""
        self.food_ids = self.env['hotel.foods'].search([('category_id', 'in', self.category_ids)])

    @api.model_create_multi
    def create(self, vals):
        """Creating sequence number.
        booking reference number is generating"""
        for val in vals:
            if val.get('food_order_reference', _('New')) == _('New'):
                val['food_order_reference'] = self.env['ir.sequence'].next_by_code('hotel.food.orders')
            return super(HotelFoodOreders, self).create(vals)

    def food_order_confirm_action(self):

        price = sum(self.order_line_ids.mapped('subtotal'))

        self.env['hotel.payments'].create({
            'description': "Food Order",
            'order_reference': self.food_order_reference,
            'uom': "Units",
            'quantity': 1,
            'unit_price': price,
            'subtotal': price,
            'accommodation_id': self.accommodation_id.id,
        })
        self.status = 'confirmed'

    def food_order_cancel_action(self):
        self.status = 'cancelled'
        payments = self.env['hotel.payments'].search([('order_reference', 'in', self.food_order_reference)])
        payments.unlink()

        food_orders = self.env['hotel.food.order.lines'].search([('food_order_reference', 'in', self.food_order_reference)])
        food_orders.unlink()