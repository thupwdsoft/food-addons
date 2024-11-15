from odoo import http
from odoo.http import request
import json

class FoodCategoryController(http.Controller):
    def make_json_response(self, data, status=200):
        response_data = {
            "error": 0 if status == 200 else 1,
            "message": "Successful" if status == 200 else "Failed",
            "data": data
        }
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')])

    def make_error_response(self, message, status=400):
        response_data = {
            "error": 1,
            "message": message,
            "data": None
        }
        return request.make_response(json.dumps(response_data), headers=[('Content-Type', 'application/json')])

    @http.route('/api/food/categories', type='http', auth='public', methods=['GET'])
    def get_categories_by_company(self, **kwargs):
        try:
            mini_app_id = kwargs.get('appId')

            if not mini_app_id:
                return self.make_error_response("Missing App ID", status=422)

            # Lọc danh mục theo `mini_app_id`
            categories = request.env['food.category'].sudo().search([('mini_app_id', '=', mini_app_id)])

            # Xây dựng dữ liệu trả về theo cấu trúc yêu cầu
            category_data = [{
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description or '',
                    "merchantId": category.mini_app_id if category.mini_app_id else None,
                    "status": "ACTIVE"
                },
                "products": [{
                    "id": product.id,
                    "name": product.name,
                    "description": product.description or '',
                    "price": product.price,
                    "imageUrl": product.image_url,
                    "status": product.status,
                    "toppings": [{
                        "id": topping.id,
                        "name": topping.name,
                        "price": topping.price
                    } for topping in product.topping_ids]
                    # Giả sử mỗi sản phẩm có mối quan hệ nhiều-nhiều với topping qua field `topping_ids`
                } for product in category.product_ids]
            } for category in categories]

            return self.make_json_response(category_data)
        except Exception as e:
            return self.make_error_response(f"Failed to retrieve categories: {str(e)}")

    @http.route('/api/food/category/<int:category_id>', type='http', auth='public', methods=['GET'])
    def get_category_by_id(self, category_id):
        try:
            category = request.env['food.category'].sudo().search([('id', '=', category_id)], limit=1)
            if not category:
                return self.make_error_response("Category not found", status=404)

            category_data = {
                "id": category.id,
                "name": category.name,
                "description": category.description or '',
                "merchantId": category.mini_app_id if category.mini_app_id else None,
                "status": "ACTIVE",
                "products": [{
                    "id": product.id,
                    "name": product.name,
                    "description": product.description or '',
                    "price": product.price,
                    "imageUrl": product.image_url,
                    "status": product.status
                } for product in category.product_ids]
            }
            return self.make_json_response(category_data)
        except Exception as e:
            return self.make_error_response(f"Failed to retrieve category: {str(e)}")

    @http.route('/api/food/category', type='http', auth='public', methods=['POST'], csrf=False)
    def create_category(self, **kwargs):
        try:
            name = kwargs.get('name')
            description = kwargs.get('description', '')
            mini_app_id = kwargs.get('mini_app_id')

            if not name:
                return self.make_error_response("Missing required field 'name'", status=422)

            category = request.env['food.category'].create({
                'name': name,
                'description': description,
                'mini_app_id': mini_app_id
            })

            category_data = {
                "id": category.id,
                "name": category.name,
                "description": category.description or '',
                "mini_app_id": category.mini_app_id if category.mini_app_id else None,
                "status": "ACTIVE"
            }
            return self.make_json_response(category_data)
        except Exception as e:
            return self.make_error_response(f"Failed to create category: {str(e)}")

    @http.route('/api/food/tables', type='http', auth='public', methods=['GET'])
    def get_all_tables_by_company(self, **kwargs):
        try:
            mini_app_id = kwargs.get('appId')

            if not mini_app_id:
                return self.make_error_response("Missing mini_app_id", status=422)

            # Query tables based on company_id
            tables = request.env['food.table'].sudo().search([('mini_app_id', '=', mini_app_id)])
            table_list = [{
                'table_id': table.id,
                'table_name': table.table_name,
            } for table in tables]

            # Return JSON response
            return self.make_json_response(table_list)
        except Exception as e:
            return self.make_error_response(f"Error: {str(e)}", status=500)
