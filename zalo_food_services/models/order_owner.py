from odoo import models, fields, api

class FoodOwner(models.Model):
    _name = 'food.owner'
    _description = 'Owner'

    owner_id = fields.Char(string="Zalo ID", required=True, index=True, readonly=True)
    mini_app_id = fields.Char(string="APP-ID", readonly=True)
    owner_name = fields.Char(string="Tên", required=False)
    avatar = fields.Char(string="Avatar URL")
    phone = fields.Char(string="Số điện thoại")

    role = fields.Selection([
        ('admin', 'ADMIN'),
        ('staff', 'STAFF'),
        ('customer', 'CUSTOMER')
    ], string="Vai trò", required=True, default='customer')

    status = fields.Selection([
        ('active', 'ACTIVE'),
        ('inactive', 'INACTIVE')
    ], string="Tình trạng", required=True, default='active')

    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        default=lambda self: self.env.company,
        required=False
    )

    _sql_constraints = [
        ('unique_owner_id', 'UNIQUE(owner_id)', 'The Zalo ID must be unique.'),
    ]

    @api.model
    def create(self, vals):
        if 'mini_app_id' not in vals:
            current_company = self.env.company
            vals['mini_app_id'] = current_company.mini_app_id  # Gán mini_app_id từ công ty hiện tại
        return super(FoodOwner, self).create(vals)
