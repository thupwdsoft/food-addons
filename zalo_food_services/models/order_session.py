from odoo import models, fields

class OrderSession(models.Model):
    _name = 'food.order_session'
    _description = 'Order Session'

    session_id = fields.Char(
        string="Session ID",
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('food.order_session')
    )

    mini_app_id = fields.Char(string="APP-ID", required=True)  # Trường APP-ID để xác định Mini App

    status = fields.Selection(
        [('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')],
        default='ACTIVE',
        string="Status"
    )
    created_at = fields.Datetime(string="Created At", default=fields.Datetime.now)
    updated_at = fields.Datetime(string="Updated At")
    owner_id = fields.Many2one(
        'food.owner',
        string="Owner",
        required=True
    )
    # New field to identify order type
    order_type = fields.Selection([
        ('in_store', 'In Store'),
        ('delivery', 'Delivery')
    ], string="Order Type", required=True, default='in_store')
