from odoo import http
from odoo.http import request
import json

class FoodProductController(http.Controller):
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

    @http.route('/api/food/products', type='http', auth='public', methods=['GET'])
    def get_products(self, **kwargs):
        try:
            company_id = kwargs.get('company_id')
            if not company_id:
                return self.make_error_response("Missing company ID", status=422)

            category_id = kwargs.get('category_id')
            domain = [('company_id', '=', int(company_id))]
            if category_id:
                domain.append(('category_id', '=', int(category_id)))

            products = request.env['food.product'].sudo().search(domain)
            product_data = [self._get_product_data(product) for product in products]
            return self.make_json_response(product_data)
        except Exception as e:
            return self.make_error_response(f"Failed to retrieve products: {str(e)}")

    @http.route('/api/food/product/<int:product_id>', type='http', auth='public', methods=['GET'])
    def get_product_by_id(self, product_id, **kwargs):
        try:
            company_id = kwargs.get('company_id')
            if not company_id:
                return self.make_error_response("Missing company ID", status=422)

            product = request.env['food.product'].sudo().search([
                ('id', '=', product_id),
                ('company_id', '=', int(company_id))
            ], limit=1)

            if not product:
                return self.make_error_response("Product not found", status=404)

            product_data = self._get_product_data(product)
            return self.make_json_response(product_data)
        except Exception as e:
            return self.make_error_response(f"Failed to retrieve product: {str(e)}")

    @http.route('/api/food/product', type='http', auth='public', methods=['POST'], csrf=False)
    def create_product(self, **kwargs):
        try:
            company_id = kwargs.get('company_id')
            if not company_id:
                return self.make_error_response("Missing company ID", status=422)

            name = kwargs.get('name')
            price = kwargs.get('price')
            category_id = kwargs.get('category_id')
            description = kwargs.get('description', '')
            image_url = kwargs.get('imageUrl', '')
            sku = kwargs.get('sku', '')

            if not name or not price or not category_id:
                return self.make_error_response("Missing required fields", status=422)

            product = request.env['food.product'].sudo().create({
                'name': name,
                'price': price,
                'category_id': category_id,
                'description': description,
                'image_url': image_url,
                'sku': sku,
                'company_id': int(company_id)  # Thêm `company_id` vào khi tạo mới
            })

            product_data = self._get_product_data(product)
            return self.make_json_response(product_data)
        except Exception as e:
            return self.make_error_response(f"Failed to create product: {str(e)}")

    def _get_product_data(self, product):
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "sku": product.sku or None,
            "description": product.description or '',
            "imageUrl": product.image_url or '',
            "status": product.status,
            "category": product.category_id.id if product.category_id else None,
            "toppings": [{
                "id": topping.id,
                "name": topping.name,
                "price": topping.price,
                "status": "ACTIVE"
            } for topping in product.topping_ids]
        }
