from odoo import http
from odoo.http import request
import json
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

class CompanyController(http.Controller):
    @http.route('/api/food/company', type='http', auth='public', methods=['GET'], csrf=False)
    def get_company_info_by_app_id(self, **kwargs):
        # Giả sử bạn nhận được `mini_app_id` từ query string
        mini_app_id = request.httprequest.args.get('appId')
        _logger.info('Received mini_app_id: %s', mini_app_id)

        if not mini_app_id:
            _logger.warning('mini_app_id is missing')
            return request.make_response(json.dumps({
                'error': 1,
                'message': 'Missing mini_app_id'
            }), headers=[('Content-Type', 'application/json')])

        # Tìm công ty dựa trên `oa_id`
        company = request.env['res.company'].sudo().search([('mini_app_id', '=', mini_app_id)], limit=1)
        if not company:
            _logger.warning('Company with mini_app_id %s not found', mini_app_id)
            return request.make_response(json.dumps({
                'error': 1,
                'message': 'Company not found'
            }), headers=[('Content-Type', 'application/json')])

        # Chuẩn bị dữ liệu phản hồi
        response_data = {
            'error': 0,
            'message': 'Successful',
            'data': {
                'oa': {
                    'oa_id': company.id,
                    'name': company.name,
                    'avatarUrl': getattr(company, 'logo_url', ''),
                    'coverUrl': getattr(company, 'cover_url', ''),
                    'phone': company.phone or '',
                    'address': {
                        'street': company.street or '',
                        'city': company.city or '',
                        'zip': company.zip or '',
                        'country': company.country_id.name if company.country_id else ''
                    }
                },
                'followed': False
            }
        }
        _logger.info('Response data for mini_app_id %s: %s', mini_app_id, response_data)
        return request.make_response(
            json.dumps(response_data),
            headers=[('Content-Type', 'application/json')]
        )


