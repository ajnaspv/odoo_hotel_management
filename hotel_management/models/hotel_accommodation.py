from datetime import timedelta, datetime
from odoo import fields,models, api, _
from odoo.exceptions import UserError
from odoo import Command
from odoo.orm.fields_relational import Many2one


class HotelAccommodation(models.Model):
    _name = 'hotel.accommodation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Accommodation'
    _rec_name = 'room_id'

    guest_id = fields.Many2one('res.partner',string='Guest Name', required=True)
    number_of_guests = fields.Integer(string='Number of Guests', default=1)
    additional_guest_ids = fields.One2many('hotel.guests','additional_guests_id',string='Additional Guests')
    check_in_date = fields.Datetime(string='Check In Date', tracking=True)
    check_out_date = fields.Datetime(string='Check Out Date', tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    bed_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),
    ])
    facility_ids = fields.Many2many('hotel.rooms.facilities',string='Facility')
    room_id = fields.Many2one('hotel.rooms',string='Rooms' , domain="[('bed_type', '=', bed_type), ('facilities_id', '=', facility_ids), ('state', '=', 'available')] if bed_type and facility_ids else [('bed_type', '=', bed_type), ('state', '=', 'available')] if bed_type else [('facilities_id', '=', facility_ids), ('state', '=', 'available')] if facility_ids else [('state', '=', 'available')]", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('check_in', 'Check-In'),
        ('check_out', 'Check-Out'),
        ('cancelled', 'Cancelled'),
    ],default='draft', tracking=True)
    id_proof = fields.Binary(string='Address Proof')
    expected_days = fields.Integer(string='Expected Days')
    expected_date = fields.Datetime(string='Expected Date', compute='_compute_expected_date')
    booking_reference = fields.Char(string='Boooking Reference', readonly=True, default=lambda self: _('New'), copy=False)


    @api.depends('expected_days','check_in_date')
    def _compute_expected_date(self):
        """Compute expected checkout date.
        Check in date, checkout date, expected days are used.
        Returns an expected checkout date"""

        if not self.check_in_date:
            self.expected_date=datetime.now()+timedelta(days=self.expected_days)
        else:
            self.expected_date = self.check_in_date + timedelta(days=self.expected_days)

    @api.model_create_multi
    def create(self, vals):
        """Creating sequence number.
        booking reference number is generating"""
        for val in vals:
            if val.get('booking_reference', _('New')) == _('New'):
                val['booking_reference'] = self.env['ir.sequence'].next_by_code('hotel.accommodation')
            return super(HotelAccommodation, self).create(vals)

    def check_in_action(self):
        """Performing the checkout button action
        check in, checkout dates, id proof, additional guest ids are used.
        id proof, guest details validating"""
        if not self.id_proof:
            raise UserError("Id Proof is Not Attached. Please Attach.")
        elif len(self.additional_guest_ids)!=self.number_of_guests-1:
            raise UserError("Number of Guests or details is not correct. Please Provide details of all Guests.")
        else:
            self.state = 'check_in'
            self.check_in_date = datetime.now()
            self.room_id.state = 'not_available'

    def check_out_action(self):
        """Performing check-out button action & invoice generation,computed  total days, generating invoice
        guest id, room id, rent from room id, total days are used.
        return the invoice"""
        self.state = 'check_out'
        self.check_out_date = datetime.now()
        self.room_id.state = 'available'
        if (self.check_out_date.date() - self.check_in_date.date()).days == 0:
            total_days=1
        else:
            total_days=(self.check_out_date.date()-self.check_in_date.date()).days


        invoice= self.env['account.move'].create({
                'move_type':'out_invoice',
                'partner_id': self.guest_id.id,
                'invoice_date': datetime.today(),
                'invoice_line_ids': [Command.create({
                    'name': "Room "+self.room_id.room_number,
                    'price_unit': self.room_id.rent,
                    'quantity': total_days,
                })]
            })
        self.invoice_id=invoice.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id' : invoice.id,
            'target': 'current',
        }

    def cancel_btn_action(self):
        """Performing cancel button action.
        state is used.
        Change the state into canceled"""
        self.state = 'cancelled'

    def draft_btn_action(self):
        """Performing draft button action.
        state is used.
        Change the state into draft."""
        self.state = 'draft'

    def action_view_invoice(self):
        """Action for Invoice stat button.
        invoice_id is used
        return the view of invoice."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }