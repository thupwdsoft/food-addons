from odoo import models, fields, api

class FoodCategory(models.Model):
    _name = 'food.category'
    _description = 'Food Category'

    name = fields.Char(required=True, string="Tên danh mục")
    description = fields.Text(string="Mô tả")
    mini_app_id = fields.Char(string="ID Mini App", readonly=True)  # Đặt readonly để ngăn chỉnh sửa trực tiếp
    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        default=lambda self: self.env.company
    )  # Liên kết tới bảng res.company
    status = fields.Selection(
        [('ACTIVE', 'active'), ('INACTIVE', 'inactive')],
        default='ACTIVE',
        string="Trạng thái"
    )
    product_ids = fields.One2many(
        'food.product',
        'category_id',
        string="Sản phẩm"
    )  # One2many tới bảng food.product

    @api.model
    def create(self, vals):
        if 'mini_app_id' not in vals or not vals.get('mini_app_id'):
            company = self.env['res.company'].browse(vals.get('company_id')) if 'company_id' in vals else self.env.company
            vals['mini_app_id'] = company.mini_app_id  # Gán mini_app_id từ công ty liên kết
        return super(FoodCategory, self).create(vals)
