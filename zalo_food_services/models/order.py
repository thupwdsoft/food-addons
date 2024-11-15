from odoo import models, fields, api

class FoodOrder(models.Model):
    _name = 'food.order'
    _description = 'Order'

    zalo_id = fields.Char(string="Mã ID Zalo", readonly=True)
    owner_name = fields.Char(string='Tên người đặt')
    order_number = fields.Char(string='Mã số đơn', required=True, copy=False, readonly=True, default='New')
    customer_phone = fields.Char(string='Số điện thoại')
    table_id = fields.Many2one('food.table', string='Tên bàn')

    # Liên kết với bảng công ty để lấy APP-ID
    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        default=lambda self: self.env.company,
        required=True
    )

    # APP-ID tự động lấy từ công ty
    mini_app_id = fields.Char(
        string="APP-ID",
        store=True,
        readonly=True
    )

    status = fields.Selection([
        ('PENDING', 'pending'),
        ('DELIVERING', 'delivering'),
        ('CONFIRMED', 'confirmed'),
        ('CANCELLED', 'cancelled')
    ], string='Tình trạng', default='PENDING', required=True)

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('zalo_pay', 'Zalo Pay')
    ], string='Phương thức thanh toán', default='cash')

    order_item_ids = fields.One2many('food.order.item', 'order_id', string="Danh sách sản phẩm")
    total_amount = fields.Float(string='Tổng tiền', compute='_compute_total_amount', store=True)

    @api.model
    def create(self, vals):
        if vals.get('order_number', 'New') == 'New':
            vals['order_number'] = self.env['ir.sequence'].next_by_code('food.order') or 'New'
        return super(FoodOrder, self).create(vals)

    @api.depends('order_item_ids.price_subtotal')
    def _compute_total_amount(self):
        for order in self:
            # Tổng tiền là tổng của price_subtotal của tất cả order items
            order.total_amount = sum(item.price_subtotal for item in order.order_item_ids)
