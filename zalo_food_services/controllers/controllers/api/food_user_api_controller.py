import json
from odoo import http
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)

class FoodUserController(http.Controller):

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
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')], status=status)

    @http.route('/api/food/owners', auth='public', methods=['GET'], type='http', csrf=False)
    def get_order_owners(self, **kwargs):
        """Lấy danh sách người dùng với điều kiện mini_app_id"""
        mini_app_id = kwargs.get('appId')
        domain = [('mini_app_id', '=', mini_app_id)] if mini_app_id else []
        owners = request.env['food.owner'].sudo().search(domain)
        result = [
            {
                'owner_id': owner.owner_id,
                'owner_name': owner.owner_name,
                'role': owner.role,
                'mini_app_id': owner.mini_app_id,
                'avatar': owner.avatar
            }
            for owner in owners
        ]
        return self.make_json_response(result)

    @http.route('/api/food/owner', auth='public', methods=['GET'], type='http', csrf=False)
    def get_order_owner(self, **kwargs):
        """Lấy thông tin chi tiết của một người dùng"""
        owner_id = kwargs.get('owner_id')
        mini_app_id = kwargs.get('appId')

        if not owner_id:
            return self.make_error_response('Missing owner_id parameter', status=400)

        domain = [('owner_id', '=', owner_id)]
        if mini_app_id:
            domain.append(('mini_app_id', '=', mini_app_id))

        owner = request.env['food.owner'].sudo().search(domain, limit=1)
        if not owner:
            return self.make_error_response('Owner not found', status=404)

        result = {
            'owner_id': owner.owner_id,
            'owner_name': owner.owner_name,
            'role': owner.role,
            'mini_app_id': owner.mini_app_id,
            'avatar': owner.avatar
        }
        return self.make_json_response(result)

    @http.route('/api/food/owner', auth='public', methods=['POST'], type='http', csrf=False)
    def create_or_update_order_owner(self):
        """Tạo mới hoặc cập nhật thông tin của một người dùng"""
        data = json.loads(request.httprequest.data.decode('utf-8'))
        _logger.info(f"Received data for create_or_update_order_item: {data}")

        owner_id = data.get('owner_id')
        mini_app_id = data.get('mini_app_id')
        owner_name = data.get('owner_name')
        avatar = data.get('avatar')
        role = data.get('role', 'customer')

        # Kiểm tra các trường bắt buộc
        if 'owner_id' not in data or 'mini_app_id' not in data:
            return self.make_error_response('Missing required parameters: owner_id and/or mini_app_id', status=400)

        # Tìm kiếm owner theo owner_id và mini_app_id
        owner = request.env['food.owner'].sudo().search([
            ('owner_id', '=', owner_id),
            ('mini_app_id', '=', mini_app_id)
        ], limit=1)

        if owner:
            # Nếu owner đã tồn tại, thực hiện cập nhật
            owner.sudo().write({
                'owner_name': owner_name,
                'avatar': avatar
            })
            message = 'Owner updated'
            status = 'updated'  # Đánh dấu trạng thái là updated
        else:
            # Nếu owner chưa tồn tại, thực hiện tạo mới
            owner = request.env['food.owner'].sudo().create({
                'owner_id': owner_id,
                'owner_name': owner_name,
                'role': role,
                'mini_app_id': mini_app_id,
                'avatar': avatar
            })
            message = 'Owner created'
            status = 'created'  # Đánh dấu trạng thái là created

        # Trả về phản hồi
        return self.make_json_response({'owner_id': owner.owner_id, 'message': message, 'status': status})

    @http.route('/api/food/owner', auth='public', methods=['PUT'], type='http', csrf=False)
    def update_order_owner(self, **kwargs):
        """Cập nhật thông tin của một người dùng"""
        owner_id = kwargs.get('owner_id')
        if not owner_id:
            return self.make_error_response('Missing owner_id parameter', status=400)

        owner = request.env['food.owner'].sudo().search([('owner_id', '=', owner_id)], limit=1)
        if not owner:
            return self.make_error_response('User not found', status=404)

        owner.sudo().write({
            'owner_name': kwargs.get('owner_name', owner.owner_name),
            'role': kwargs.get('role', owner.role),
            'mini_app_id': kwargs.get('mini_app_id', owner.mini_app_id),
            'avatar': kwargs.get('avatar', owner.avatar)
        })
        return self.make_json_response({'success': True})

    @http.route('/api/food/owner', auth='public', methods=['DELETE'], type='http', csrf=False)
    def delete_order_owner(self, **kwargs):
        """Xóa một người dùng"""
        owner_id = kwargs.get('owner_id')
        if not owner_id:
            return self.make_error_response('Missing owner_id parameter', status=400)

        owner = request.env['food.owner'].sudo().search([('owner_id', '=', owner_id)], limit=1)
        if not owner:
            return self.make_error_response('User not found', status=404)

        owner.sudo().unlink()
        return self.make_json_response({'success': True})
