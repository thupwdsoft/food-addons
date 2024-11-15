from odoo import http
from odoo.http import request
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class FoodOrderController(http.Controller):
    def make_json_response(self, data, status=200, response_key="data"):
        response_data = {
            "error": 0 if status == 200 else 1,
            "message": "Successful" if status == 200 else "Failed",
            response_key: data
        }
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')])

    def make_error_response(self, message, status=400):
        response_data = {
            "error": 1,
            "message": message,
            "data": None
        }
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')])

    def serialize_datetime(self, dt):
        if isinstance(dt, datetime):
            return dt.isoformat()
        return dt

    @http.route('/api/order/order_item', type='http', auth='public', methods=['POST'], csrf=False)
    def create_or_update_order_item(self):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Received data for create_or_update_order_item: {data}")

            table_id = data.get('table_id')
            zalo_id = data.get('zalo_id')
            mini_app_id = data.get('mini_app_id')
            order_items = data.get('order_items', [])
            owner_name = data.get('owner_name', 'Guest')
            customer_phone = data.get('customer_phone', '')
            payment_method = data.get('payment_method', 'cash')
            item_status = data.get('status', 'PENDING')

            if not table_id or not mini_app_id or not order_items:
                _logger.error("Missing table name, company_id, or order items")
                return self.make_error_response("Missing table name, mini_app_id, or order items", status=422)

            # Kiểm tra xem Zalo ID có tồn tại trong bảng food.owner không
            owner = request.env['food.owner'].sudo().search([('owner_id', '=', zalo_id)], limit=1)
            if not owner:
                _logger.error(f"Owner with Zalo ID {zalo_id} not found.")
                return self.make_error_response("Owner not found", status=404)

            # Tìm order đang chờ (PENDING) với table_id và company_id tương ứng
            existing_order = request.env['food.order'].sudo().search([
                ('table_id', '=', table_id),
                ('mini_app_id', '=', mini_app_id),
                ('status', '=', 'PENDING')
            ], limit=1)

            if existing_order:
                _logger.info(f"Existing order found: {existing_order.id}")
                # Thêm các order items vào order đang chờ
                for item in order_items:
                    request.env['food.order.item'].sudo().create({
                        'order_id': existing_order.id,
                        'owner_name': owner_name,
                        'product_id': item.get('product_id'),
                        'quantity': item.get('quantity', 1),
                        'price_unit': item.get('price', 0.0),
                        'notes': item.get('notes', ''),
                        'status': item_status,
                        'topping_ids': [(6, 0, item.get('topping_ids', []))] if item.get('topping_ids') else []
                    })
            else:
                _logger.info("No existing pending order found. Creating a new order.")
                # Tạo order mới nếu không tìm thấy order đang chờ
                new_order = request.env['food.order'].sudo().create({
                    'table_id': table_id,
                    'mini_app_id': mini_app_id,  # Gán trực tiếp mini_app_id từ dữ liệu đầu vào
                    'owner_name': owner_name,
                    'zalo_id': zalo_id,
                    'customer_phone': customer_phone,
                    'payment_method': payment_method,
                    'status': item_status,
                })

                # Thêm các order items vào order mới tạo
                for item in order_items:
                    request.env['food.order.item'].sudo().create({
                        'order_id': new_order.id,
                        'owner_name': owner_name,
                        'product_id': item.get('product_id'),
                        'quantity': item.get('quantity', 1),
                        'price_unit': item.get('price', 0.0),
                        'notes': item.get('notes', ''),
                        'status': item_status,
                        'topping_ids': [(6, 0, item.get('topping_ids', []))] if item.get('topping_ids') else []
                    })

            _logger.info("Order items created or updated successfully")
            return self.make_json_response({"message": "Order items created or updated successfully"})

        except Exception as e:
            _logger.error(f"Error in create_or_update_order_item: {str(e)}", exc_info=True)
            return self.make_error_response(f"Error in create_or_update_order_item: {str(e)}", status=500)

    @http.route('/api/order/confirm_order', type='http', auth='public', methods=['POST'], csrf=False)
    def confirm_order(self):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            order_id = data.get('order_id')
            mini_app_id = data.get('mini_app_id')
            payment_method = data.get('payment_method', 'cash')

            if not order_id or not mini_app_id:
                return self.make_error_response("Missing order_id or mini_app_id", status=422)

            order = request.env['food.order'].sudo().search([
                ('id', '=', order_id),
                ('mini_app_id', '=', mini_app_id)
            ], limit=1)

            if not order:
                return self.make_error_response(f"Order with ID {order_id} for company {mini_app_id} not found",
                                                status=404)

            order.write({
                'status': 'CONFIRMED',
                'payment_method': payment_method
            })

            return self.make_json_response({"message": "Order confirmed successfully with updated payment method"})

        except Exception as e:
            _logger.error(f"Failed to confirm order: {str(e)}")
            return self.make_error_response(f"Failed to confirm order: {str(e)}", status=500)

    @http.route('/api/order/orders', auth='public', methods=['GET'], type='http', csrf=False)
    def get_orders_by_role(self, **kwargs):
        mini_app_id = kwargs.get('appId')
        zalo_id = kwargs.get('zalo_id')  # Đổi thành zalo_id

        # Kiểm tra xem company_id và zalo_id có được truyền vào không
        if not mini_app_id:
            return self.make_error_response("Missing mini_app_id", status=422)
        if not zalo_id:
            return self.make_error_response("Missing zalo_id", status=422)

        # Tìm kiếm role của owner dựa trên zalo_id
        owner = request.env['food.owner'].sudo().search([('owner_id', '=', zalo_id)], limit=1)
        if not owner:
            return self.make_error_response("Owner not found", status=404)

        role = owner.role

        # Định nghĩa domain mặc định cho các orders với status là PENDING và thuộc về company_id cụ thể
        domain = [
            ('mini_app_id', '=', mini_app_id),
            ('status', '=', 'PENDING')
        ]

        # Kiểm tra role để xác định các orders nào sẽ được trả về
        if role == 'customer':
            # Nếu role là customer, chỉ lấy các orders thuộc về zalo_id này
            domain.append(('zalo_id', '=', zalo_id))  # Thay đổi thành zalo_id
        elif role not in ['staff', 'admin']:
            return self.make_error_response("Invalid role", status=403)

        # Thực hiện truy vấn với domain đã xác định
        orders = request.env['food.order'].sudo().search(domain)

        # Chuẩn bị dữ liệu để trả về
        orders_data = [{
            'order_id': order.id,
            'order_number': order.order_number,
            'table_name': order.table_id.table_name if order.table_id else '',
            'owner_name': order.owner_name,
            'status': order.status,
            'payment_method': order.payment_method,
            'total_amount': order.total_amount,
            'order_items': [{
                'order_item_id': item.id,
                'product_id': item.product_id.id,
                'product_name': item.product_id.name,
                'image_url': item.product_id.image_url,
                'quantity': item.quantity,
                'price_unit': item.price_unit,
                'price_subtotal': item.price_subtotal,
                'notes': item.notes,
                'status': item.status,
                'toppings': [{
                    'id': topping.id,
                    'name': topping.name,
                    'price': topping.price
                } for topping in item.topping_ids]
            } for item in order.order_item_ids]
        } for order in orders]

        return self.make_json_response({"orders": orders_data})

