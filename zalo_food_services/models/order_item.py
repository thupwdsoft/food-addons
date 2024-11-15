from odoo import models, fields, api

class FoodOrderItem(models.Model):
    _name = 'food.order.item'
    _description = 'Order Item'

    order_id = fields.Many2one('food.order', string='Mã đơn hàng', required=True)
    product_id = fields.Many2one('food.product', string='Sản phẩm', required=True)
    quantity = fields.Integer(string='Số lượng', default=1)
    price_unit = fields.Float(string='Giá')  # Giá sản phẩm
    price_subtotal = fields.Float(string='Thành tiền', compute='_compute_subtotal', store=True)
    owner_name = fields.Char(string='Người đặt')
    status = fields.Selection([
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled')
    ], string='Tình trạng', default='PENDING')
    notes = fields.Text(string='Ghi chú')
    topping_ids = fields.Many2many('food.topping', string="Toppings")  # Many2many to link toppings

    @api.depends('quantity', 'price_unit', 'topping_ids.price')
    def _compute_subtotal(self):
        for item in self:
            # Tính tổng giá topping đã chọn
            topping_total = sum(topping.price for topping in item.topping_ids)
            # Thành tiền bao gồm giá sản phẩm và topping
            item.price_subtotal = item.quantity * (item.price_unit + topping_total)
