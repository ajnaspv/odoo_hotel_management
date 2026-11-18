from datetime import timedelta, datetime
from odoo import fields,models, api, _
from odoo.exceptions import UserError
from odoo import Command
from odoo.orm.fields_relational import Many2one


class HotelAccommodation(models.Model):
    _name = 'hotel.accommodation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Accommodation'
    _rec_name = 'booking_reference'

    today = fields.Date.today()
    active = fields.Boolean(string="Is Active", default=True, readonly=True)
    guest_id = fields.Many2one('res.partner',string='Guest Name', required=True)
    number_of_guests = fields.Integer(string='Number of Guests', default=1)
    additional_guest_ids = fields.One2many('hotel.guests','additional_guests_id',string='Additional Guests')
    check_in_date = fields.Datetime(string='Check In Date', tracking=True, readonly=True)
    check_in_date_only = fields.Date('Check In Date Only', readonly=True, compute='_compute_check_in_date_only', store=True)
    check_out_date = fields.Datetime(string='Check Out Date', tracking=True, readonly=True)
    check_out_date_only = fields.Date('Check Out Date Only', readonly=True, compute='_compute_check_out_date_only', store=True)
    cancelled_date = fields.Date(string='Cancelled Date', readonly=True)
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
    expected_date = fields.Date(string='Expected Date', compute='_compute_expected_date', store=True)
    booking_reference = fields.Char(string='Boooking Reference', readonly=True, default=lambda self: _('New'), copy=False)
    invoice_count = fields.Integer(string='Invoice Count',compute='_compute_invoice_count', store=True)
    payment_ids = fields.One2many('hotel.payments', 'accommodation_id', string='Payments', ondelete='cascade')
    inv_line_ids = []
    date_today = fields.Datetime.today()
    today_date_only = fields.Date.today()
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id.id)
    invoice_payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
    ], default='not_paid', readonly=True, compute='_compute_invoice_payment_status', store=True)

    @api.depends('expected_days','check_in_date')
    def _compute_expected_date(self):
        """Compute expected checkout date.
        Check in date, checkout date, expected days are used.
        Returns an expected checkout date"""
        for rec in self:
            if not rec.check_in_date:
                rec.expected_date=(datetime.now()+timedelta(days=rec.expected_days)).date()
            else:
                rec.expected_date = (rec.check_in_date + timedelta(days=rec.expected_days)).date()

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
            self.guest_id.is_hotel_guest = True

            self.env['hotel.payments'].create({
                'description': "Room Rent",
                'order_reference' : self.booking_reference,
                'uom': "Units",
                'quantity': 1,
                'unit_price': self.room_id.rent,
                'subtotal': 1*self.room_id.rent,
                'accommodation_id': self.id,
            })

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

        payments = self.env['hotel.payments'].search([('order_reference', '=', self.booking_reference)])
        payments.write({
            'quantity': total_days,
            'subtotal': total_days * self.room_id.rent,
        })

        invoice_lines = []
        for payment in self.payment_ids:
            invoice_lines.append({
                'name': payment.description,
                'price_unit': payment.unit_price,
                'quantity': payment.quantity,
            })

        invoice= self.env['account.move'].create({
                'move_type':'out_invoice',
                'partner_id': self.guest_id.id,
                'invoice_date': datetime.today(),
                'invoice_line_ids': [Command.create(vals) for vals in invoice_lines]
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
        today = fields.Date.today()
        self.state = 'cancelled'
        self.cancelled_date = today
        self.room_id.state = 'available'
        payments = self.env['hotel.payments'].search([('accommodation_id', '=', self.id)])
        payments.unlink()
        self.invoice_id = ""

    def draft_btn_action(self):
        """Performing draft button action.
        state is used.
        Change the state into draft."""
        self.state = 'draft'
        payments = self.env['hotel.payments'].search([('accommodation_id', '=', self.id)])
        payments.unlink()
        self.room_id.state = 'available'
        self.invoice_id = ""

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

    @api.depends('invoice_id')
    def _compute_invoice_count(self):
        """Compute total invoice count
        invoice_id,invoice count is used"""
        self.invoice_count=len(self.invoice_id)

    def action_view_food_orders(self):
        """Action for Orders stat button
        return food orders list"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Food Orders',
            'res_model': 'hotel.food.order.lines',
            'view_mode': 'list',
            'target': 'current',
            'domain': [('order_room_id', 'in', self.room_id.id)],
        }

    def update_room_rent(self):
        """Update room rent automatically
        current date and check_in_date is used
        return the room rent till current date"""
        date_today = fields.Datetime.today().date()
        bookings = self.env['hotel.accommodation'].search([('state', '=', 'check_in')])
        for rec in bookings:
            if rec.check_in_date.date():
                if ((date_today - rec.check_in_date.date()).days) == 0:
                    total_days=1
                else:
                    total_days = (date_today - rec.check_in_date.date()).days
                payments = rec.env['hotel.payments'].search([('order_reference', '=', rec.booking_reference)])
                payments.write({
                    'quantity': total_days,
                    'subtotal': total_days * rec.room_id.rent,
                })

    def check_out_reminder(self):
        """Check out email reminder
        All Check-in records are used
        return the reminder"""
        date_today = fields.Datetime.today().date()
        bookings = self.env['hotel.accommodation'].search([('state', '=', 'check_in')])
        for rec in bookings:
            if rec.expected_date==date_today:
                mail_template = rec.env.ref('hotel_management.email_template_checkout_reminder')
                mail_template.send_mail(rec.id, force_send=True)

    @api.depends('invoice_id','invoice_id.payment_state')
    def _compute_invoice_payment_status(self):
        """Computing invoice paid status
        using invoice id and payment state
        return invoice paid or not"""
        for rec in self:
            if rec.invoice_id.payment_state == 'paid':
                rec.invoice_payment_status = 'paid'
            else:
                rec.invoice_payment_status = 'not_paid'

    @api.depends('check_in_date')
    def _compute_check_in_date_only(self):
        """Computing check_in_date only
        check_in_date is used
        Return only check_in_date(Exclude time)"""
        for rec in self:
            if rec.check_in_date:
                rec.check_in_date_only = rec.check_in_date.date()
                print(rec.check_in_date_only)

    @api.depends('check_out_date')
    def _compute_check_out_date_only(self):
        """Computing check_out_date only
                check_out_date is used
                Return only check_out_date(Exclude time)"""
        for rec in self:
            if rec.check_out_date:
                rec.check_out_date_only = rec.check_out_date.date()


    def cancelled_bookings_archive(self):
        date_today = fields.Datetime.today().date()
        bookings = self.env['hotel.accommodation'].search([('state', '=', 'cancelled')])
        for rec in bookings:
            if (rec.cancelled_date + timedelta(days=2)) == date_today:
                rec.active = False
