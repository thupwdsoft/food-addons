from odoo import models, fields, api

class OAAccount(models.Model):
    _name = 'oa.account'
    _description = 'OA Account'

    oa_id = fields.Char(string="Mã tài khoản OA", required=True)
    name = fields.Char(string="Tên OA", required=True)
    avatar_url = fields.Char(string="Avatar URL")
    cover_url = fields.Char(string="Cover URL")
    phone = fields.Char(string="Số điện thoại")

    # Liên kết với bảng công ty
    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        default=lambda self: self.env.company,
        required=True
    )

    # APP-ID tự động lấy từ mini_app_id của công ty
    mini_app_id = fields.Char(
        string="APP-ID",
        compute='_compute_mini_app_id',
        store=True,
        readonly=True
    )

    follower_ids = fields.One2many('oa.follower', 'oa_id', string="Danh sách theo dõi")

    @api.depends('company_id')
    def _compute_mini_app_id(self):
        for record in self:
            record.mini_app_id = record.company_id.mini_app_id if record.company_id else False
