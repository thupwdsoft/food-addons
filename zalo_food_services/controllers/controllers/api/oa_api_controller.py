from odoo import http
from odoo.http import request
import json

class ZaloOAController(http.Controller):

    # Endpoint kiểm tra trạng thái endpoint `/api/oa`
    @http.route('/api/oa', auth='public', type='http', methods=['GET'])
    def get_oa_root(self):
        return request.make_response(
            json.dumps({'error': 0, 'message': 'API root endpoint active'}),
            headers=[('Content-Type', 'application/json')]
        )

    # Endpoint lấy thông tin OA theo `oa_id` và `company_id`
    @http.route('/api/oa/<int:oa_id>', auth='public', type='http', methods=['GET'])
    def get_oa_info(self, oa_id, **kwargs):
        mini_app_id = kwargs.get('appId')
        if not mini_app_id:
            return request.make_response(
                json.dumps({'error': 1, 'message': 'Mini App ID is required'}),
                headers=[('Content-Type', 'application/json')]
            )

        oa = request.env['oa.account'].sudo().search([('id', '=', oa_id), ('company_id', '=', int(company_id))], limit=1)
        if not oa:
            return request.make_response(
                json.dumps({'error': 1, 'message': 'OA not found for this company'}),
                headers=[('Content-Type', 'application/json')]
            )

        data = {
            'id': oa.id,
            'name': oa.name,
            'avatarUrl': oa.avatar_url or '',
            'coverUrl': oa.cover_url or '',
            'phone': oa.phone or '',
        }
        return request.make_response(
            json.dumps({'error': 0, 'message': 'Successful', 'data': {'oa': data, 'followed': False}}),
            headers=[('Content-Type', 'application/json')]
        )

    # Kiểm tra trạng thái follow theo `oa_id`, `user_id`, và `company_id`
    @http.route('/api/oa/<int:oa_id>/followed', auth='public', type='http', methods=['GET'])
    def check_follow_status(self, oa_id, user_id=None, **kwargs):
        mini_app_id = kwargs.get('company_id')

        if not user_id or not mini_app_id:
            return request.make_response(
                json.dumps({'error': 1, 'message': 'User ID and App ID are required'}),
                headers=[('Content-Type', 'application/json')]
            )

        follower = request.env['oa.follower'].sudo().search([
            ('oa_id', '=', oa_id),
            ('user_id', '=', user_id),
            ('mini_app_id', '=', mini_app_id)
        ], limit=1)
        followed = bool(follower and follower.followed)

        return request.make_response(
            json.dumps({'error': 0, 'message': 'Successful', 'data': {'followed': followed}}),
            headers=[('Content-Type', 'application/json')]
        )

    # Đặt trạng thái follow cho `oa_id`, `user_id`, và `company_id`
    @http.route('/api/oa/<int:oa_id>/follow', auth='public', type='http', methods=['POST'], csrf=False)
    def follow_oa(self, oa_id, **kwargs):
        user_id = kwargs.get('user_id')
        mini_app_id = kwargs.get('appId')

        if not user_id or not mini_app_id:
            return request.make_response(
                json.dumps({'error': 1, 'message': 'User ID and App ID are required'}),
                headers=[('Content-Type', 'application/json')]
            )

        follower = request.env['oa.follower'].sudo().search([
            ('oa_id', '=', oa_id),
            ('user_id', '=', user_id),
            ('mini_app_id', '=', mini_app_id)
        ], limit=1)

        if not follower:
            request.env['oa.follower'].sudo().create({
                'oa_id': oa_id,
                'user_id': user_id,
                'mini_app_id': mini_app_id,
                'followed': True
            })
        else:
            follower.sudo().write({'followed': True})

        return request.make_response(
            json.dumps({'error': 0, 'message': 'Follow successful'}),
            headers=[('Content-Type', 'application/json')]
        )

    # Đặt trạng thái unfollow cho `oa_id`, `user_id`, và `company_id`
    @http.route('/api/oa/<int:oa_id>/unfollow', auth='public', type='http', methods=['POST'], csrf=False)
    def unfollow_oa(self, oa_id, **kwargs):
        user_id = kwargs.get('user_id')
        mini_app_id = kwargs.get('appId')

        if not user_id or not mini_app_id:
            return request.make_response(
                json.dumps({'error': 1, 'message': 'User ID and App ID are required'}),
                headers=[('Content-Type', 'application/json')]
            )

        follower = request.env['oa.follower'].sudo().search([
            ('oa_id', '=', oa_id),
            ('user_id', '=', user_id),
            ('mini_app_id', '=', mini_app_id)
        ], limit=1)

        if follower:
            follower.sudo().write({'followed': False})

        return request.make_response(
            json.dumps({'error': 0, 'message': 'Unfollow successful'}),
            headers=[('Content-Type', 'application/json')]
        )
