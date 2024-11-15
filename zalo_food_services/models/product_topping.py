from odoo import models, fields

class FoodTopping(models.Model):
    _name = 'food.topping'
    _description = 'Food Topping'

    name = fields.Char(required=True, string="Tên")
    price = fields.Float(default=0.0, string="Giá")
    status = fields.Selection([('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', string="Trạng thái")
    product_ids = fields.Many2many('food.product', string="Danh sách sản phẩm")