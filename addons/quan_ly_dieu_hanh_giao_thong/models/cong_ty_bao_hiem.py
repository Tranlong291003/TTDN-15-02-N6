from odoo import models, fields, api

class CongTyBaoHiem(models.Model):
    _name = 'cong_ty_bao_hiem'
    _description = 'Quản lý Công Ty & Gói Bảo Hiểm'

    name = fields.Char(string='🏦 Tên Công Ty', required=True)

    insurance_category = fields.Selection([
        ('personal', 'Thân Thể'),
        ('vehicle', 'Phương Tiện')
    ], string='🔖 Loại Bảo Hiểm', required=True)

    package_type = fields.Selection([
        ('basic', 'Gói Cơ Bản'),
        ('advanced', 'Gói Nâng Cao'),
        ('premium', 'Gói Premium')
    ], string='📜 Gói Bảo Hiểm', required=True)
    
    full_name = fields.Char(string='📜 Gói Bảo Hiểm', compute='_compute_full_name', store=True)
    insurance_price = fields.Float(string='💰 Số Tiền Bảo Hiểm', digits=(12, 2))

    @api.depends('name', 'package_type', 'insurance_category')
    def _compute_full_name(self):
        """ Tự động cập nhật tên đầy đủ của gói bảo hiểm """
        package_labels = {
            'basic': 'Gói Cơ Bản',
            'advanced': 'Gói Nâng Cao',
            'premium': 'Gói Premium'
        }
        category_labels = {
            'personal': 'Thân Thể',
            'vehicle': 'Phương Tiện'
        }
        for record in self:
            if record.name and record.package_type and record.insurance_category:
                record.full_name = f"{record.name} - {category_labels[record.insurance_category]} - {package_labels[record.package_type]}"
            else:
                record.full_name = record.name


    def name_get(self):
        """Hiển thị full_name thay vì name khi chọn gói bảo hiểm"""
        result = []
        for record in self:
            name = record.full_name if record.full_name else record.name  # Nếu có full_name thì hiển thị full_name
            result.append((record.id, name))
        return result