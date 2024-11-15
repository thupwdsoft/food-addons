from odoo import models, fields, api

class FoodProduct(models.Model):
    _name = 'food.product'
    _description = 'Food Product'

    name = fields.Char(required=True, string="Tên")
    price = fields.Float(required=True, string="Giá")  # Trường price cần có ở đây để sử dụng trong order line
    sku = fields.Char()
    description = fields.Text(string="Mô tả")
    image_url = fields.Char(string="Hình ảnh", required=False)
    #image_url = fields.Binary("Image", attachment=True)
    status = fields.Selection([('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', string="Trạng thái")
    category_id = fields.Many2one('food.category', string="Danh mục")
    topping_ids = fields.Many2many('food.topping', string="Toppings")  # Many2many to link toppings
