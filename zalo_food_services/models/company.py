from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    logo_url = fields.Char('Logo URL')
    cover_url = fields.Char('Cover URL')
    description = fields.Text(string="Mô tả")
    is_active = fields.Selection([
        ('ENABLE', 'enable'),
        ('DISABLE', 'disable')
    ], default='ENABLE', string="Tình trạng")
    is_visible_order = fields.Boolean('Hiển thị đặt hàng', default=True)
    mini_app_id = fields.Char('Mini App ID')  # Thêm trường Mini App ID
