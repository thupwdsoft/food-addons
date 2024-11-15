from odoo import models, fields, api

class OAFollower(models.Model):
    _name = 'oa.follower'
    _description = 'OA Follower'

    name = fields.Char(required=False, string="Tên người theo dõi")
    zalo_id = fields.Char(required=False, string="Mã ID Zalo follow")
    oa_id = fields.Many2one('oa.account', string="Tên tài khoản OA", required=False, ondelete='cascade')
    follow_status = fields.Selection([('FOLLOWING', 'Following'), ('NOT_FOLLOWING', 'Not Following')], default='FOLLOWING')
    user_id = fields.Many2one('res.users', string="Người dùng")  # Thêm trường user_id nếu cần thiết
    followed = fields.Boolean(string="Đã theo dõi", default=True)

    _sql_constraints = [
        ('zalo_id_unique', 'unique(zalo_id)', 'Zalo ID must be unique!'),
    ]
