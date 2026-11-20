from odoo import api, fields, models
from odoo.exceptions import ValidationError

class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.constrains('file_size')
    def _check_file_size(self):
        for record in self:
            if record.file_size > 50 * 1024:
                raise ValidationError("The file size should be less than 50kb")