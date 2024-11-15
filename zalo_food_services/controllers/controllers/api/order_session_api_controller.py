from odoo import http
from odoo.http import request
from datetime import datetime
import json
import logging

_logger = logging.getLogger(__name__)

class OrderSessionAPIController(http.Controller):

    # Helper function to parse ISO datetime strings
    def parse_datetime(self, iso_string):
        try:
            return datetime.strptime(iso_string.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(iso_string.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")

    # Helper function to create a JSON response
    def make_json_response(self, data, status=200, response_key="data"):
        response_data = {
            "error": 0 if status == 200 else 1,
            "message": "Successful" if status == 200 else "Failed",
            response_key: data
        }
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')])

    # Helper function to create an error response
    def make_error_response(self, message, status=400):
        response_data = {
            "error": 1,
            "message": message,
            "data": None
        }
        _logger.error(f"Error response: {response_data}")  # Log error response
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')])

    # Endpoint to create an order session for a specific company
    @http.route('/api/order/create_order_session', type='http', auth='public', methods=['POST'], csrf=False)
    def create_order_session(self, **kwargs):
        try:
            raw_data = request.httprequest.data
            data = json.loads(raw_data)
            _logger.info(f"Received data: {data}")  # Log input data

            # Extract data from request
            order_session_data = data.get('orderSession')
            owner_data = data.get('owner')
            company_id = data.get('company_id')

            # Validate required fields
            if not order_session_data or not owner_data or not company_id:
                return self.make_error_response('Missing required session, owner, or company_id', status=422)

            # Find the company by company_id
            company = request.env['res.company'].sudo().browse(int(company_id))
            if not company.exists():
                return self.make_error_response("Company not found", status=404)

            # Parse datetime fields
            created_at = self.parse_datetime(order_session_data['createdAt'])
            updated_at = self.parse_datetime(order_session_data['updatedAt'])

            # Find or create owner
            owner = request.env['food.owner'].sudo().search([('owner_id', '=', owner_data['zalo_id'])], limit=1)
            if not owner:
                owner = request.env['food.owner'].sudo().create({
                    'owner_id': owner_data['zalo_id'],
                    'name': owner_data['name'],
                    'avatar': owner_data['avatar'],
                })

            # Create order session with the integer ID of the company
            order_session = request.env['food.order_session'].sudo().create({
                'status': order_session_data['status'],
                'created_at': created_at,
                'updated_at': updated_at,
                'owner_id': owner.id,
                'company_id': company.id,
                'order_type': order_session_data.get('order_type', 'in_store'),
            })

            response_data = {
                'orderSession': {
                    'id': order_session.session_id,
                    'status': order_session.status,
                    'createdAt': order_session.created_at.isoformat(),
                    'updatedAt': order_session.updated_at.isoformat(),
                },
                'owner': {
                    'id': owner.id,
                    'name': owner.name,
                    'avatar': owner.avatar,
                    'zalo_id': owner.owner_id,
                }
            }

            _logger.info(f"Response data: {response_data}")  # Log output data
            return self.make_json_response(response_data)

        except Exception as e:
            _logger.exception("Exception occurred while creating order session")  # Log exception with traceback
            return self.make_error_response(f"Error creating order session: {str(e)}", status=500)

    # Endpoint to retrieve an order session based on company_id and session_id
    @http.route('/api/order/get_order_session', type='http', auth='public', methods=['GET', 'OPTIONS'])
    def get_order_session(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                status=200,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': 'http://localhost:3000',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Credentials': 'true',
                }
            )

        session_id = kwargs.get('orderSessionId')
        company_id = kwargs.get('company_id')

        if not session_id or not company_id:
            return self.make_error_response('Missing orderSessionId or companyId in query string', status=422)

        # Log session and company ID values to verify input
        _logger.info(f"Received session_id: {session_id}, company_id: {company_id}")

        # Search for the order session
        order_session = request.env['food.order_session'].sudo().search([
            ('session_id', '=', session_id),
            ('company_id', '=', int(company_id))
        ], limit=1)

        if not order_session:
            return self.make_error_response('Order session not found or session is empty', status=404)

        # Prepare response with session data
        owner = order_session.owner_id
        response_data = {
            'orderSession': {
                'id': order_session.session_id,
                'status': order_session.status,
                'createdAt': order_session.created_at.isoformat(),
                'updatedAt': order_session.updated_at.isoformat(),
            },
            'owner': {
                'id': owner.id,
                'name': owner.name,
                'avatar': owner.avatar,
                'zalo_id': owner.owner_id,
            }
        }

        _logger.info(f"Response data for get_order_session: {response_data}")  # Log output data for retrieval
        return self.make_json_response(response_data)
