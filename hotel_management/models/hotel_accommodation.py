from datetime import timedelta, datetime
from odoo import fields,models, api, _
from odoo.exceptions import UserError
from odoo import Command


class HotelAccommodation(models.Model):
    _name = 'hotel.accommodation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Accommodation'
    _rec_name = 'booking_reference'

    guest_id = fields.Many2one('res.partner',string='Guest Name', required=True)
    number_of_guests = fields.Integer(string='Number of Guests', default=1)
    additional_guest_ids = fields.One2many('hotel.guests','additional_guests_id',string='Additional Guests')
    check_in_date = fields.Datetime(string='Check In Date', tracking=True)
    check_out_date = fields.Datetime(string='Check Out Date', tracking=True)
    bed_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),
    ])
    facility_ids = fields.Many2many('hotel.rooms.facilities',string='Facility')
    room_id = fields.Many2many('hotel.rooms',string='Rooms' , domain="[('bed_type', '=', bed_type), ('facilities_id', '=', facility_ids), ('state', '=', 'available')] if bed_type and facility_ids else [('bed_type', '=', bed_type)] if bed_type else [('facilities_id', '=', facility_ids)] if facility_ids else []")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('check_in', 'Check-In'),
        ('check_out', 'Check-Out'),
        ('cancelled', 'Cancelled'),
    ],default='draft', tracking=True)
    id_proof = fields.Binary(string='Address Proof')
    expected_days = fields.Integer(string='Expected Days')
    expected_date = fields.Datetime(string='Expected Date', compute='_compute_expected_date')

    @api.depends('expected_days','check_in_date')
    def _compute_expected_date(self):
        if not self.check_in_date:
            self.expected_date=datetime.now()+timedelta(days=self.expected_days)
        else:
            self.expected_date = self.check_in_date + timedelta(days=self.expected_days)
    # Sequence or reference Number Creation
    booking_reference = fields.Char(string='Boooking Reference', readonly=True, default=lambda self: _('New'), copy=False)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('booking_reference', _('New')) == _('New'):
                val['booking_reference'] = self.env['ir.sequence'].next_by_code('hotel.accommodation')
            return super(HotelAccommodation, self).create(vals)

    def check_in_action(self):
        self.state = 'check_in'
        self.check_in_date = datetime.now()
        if not self.id_proof:
            raise UserError("Id Proof is Not Attached. Please Attach.")
        if len(self.additional_guest_ids)!=self.number_of_guests-1:
            raise UserError("Number of Guests or details is not correct. Please Provide details of all Guests.")
    def check_out_action(self):
        self.state = 'check_out'
        self.check_out_date = datetime.now()

        self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id': self.guest_id.id,
            'invoice_date': self.check_in_date,
            'invoice_line_ids': [Command.create({
                'name': self.room_id.room_number,
                'price_unit': int(self.room_id.rent),
                'quantity': 1,
                'tax_ids': [],
            })]
        })