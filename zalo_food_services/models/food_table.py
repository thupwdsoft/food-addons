from odoo import models, fields, api

class FoodTable(models.Model):
    _name = 'food.table'
    _description = 'Food Table'

    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        default=lambda self: self.env.company,
        required=True
    )

    mini_app_id = fields.Char(
        string="APP-ID",
        related='company_id.mini_app_id',
        store=True,
        readonly=True
    )

    table_name = fields.Char(string="Tên bàn", required=True)

    @api.depends('company_id')
    def some_dependent_method(self):
        # Implementation here
        pass

    def name_get(self):
        result = []
        for record in self:
            name = record.table_name
            result.append((record.id, name))
        return result
