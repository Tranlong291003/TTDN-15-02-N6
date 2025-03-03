from odoo import models, fields, api

class CongTyBaoHiem(models.Model):
    _name = 'cong_ty_bao_hiem'
    _description = '🏦 Quản lý Công Ty & Gói Bảo Hiểm'

    insurance_id = fields.Char(
        string='🆔 Mã Bảo Hiểm', 
        required=True, 
        copy=False, 
        readonly=True,  
        index=True, 
        default=lambda self: self._generate_insurance_id()
    )

    name = fields.Char(string='🏦 Tên Công Ty', required=True)

    insurance_category = fields.Selection([
        ('personal', '🧍 Thân Thể'),
        ('vehicle', '🚗 Phương Tiện')
    ], string='🔖 Loại Bảo Hiểm', required=True)

    package_type = fields.Selection([
        ('basic', '📜 Gói Cơ Bản'),
        ('advanced', '📜 Gói Nâng Cao'),
        ('premium', '📜 Gói Premium')
    ], string='📜 Gói Bảo Hiểm', required=True)

    full_name = fields.Char(string='📌 Tên Đầy Đủ', compute='_compute_full_name', store=True)
    insurance_price = fields.Float(string='💰 Giá bảo hiểm', digits=(12, 2))

    _sql_constraints = [
        ('insurance_id_uniq', 'unique(insurance_id)', '🆔 Mã Bảo Hiểm không được trùng! Vui lòng nhập lại.')
    ]

    @api.depends('name', 'package_type', 'insurance_category')
    def _compute_full_name(self):
        """ Cập nhật tên đầy đủ của gói bảo hiểm mà không bao gồm mã bảo hiểm """
        package_labels = {
            'basic': '📜 Gói Cơ Bản',
            'advanced': '📜 Gói Nâng Cao',
            'premium': '📜 Gói Premium'
        }
        category_labels = {
            'personal': '🧍 Thân Thể',
            'vehicle': '🚗 Phương Tiện'
        }
        for record in self:
            if record.name and record.package_type and record.insurance_category:
                record.full_name = f"{record.name} - {category_labels[record.insurance_category]} - {package_labels[record.package_type]}"
            else:
                record.full_name = record.name

    def name_get(self):
        """ Hiển thị full_name thay vì name khi chọn gói bảo hiểm """
        result = []
        for record in self:
            name = record.full_name if record.full_name else record.name
            result.append((record.id, name))
        return result

    @api.model
    def _generate_insurance_id(self):
        """ Tạo mã bảo hiểm tự động (BH001, BH002, ...) """
        last_record = self.search([], order="insurance_id desc", limit=1)
        if last_record and last_record.insurance_id:
            last_number = int(last_record.insurance_id[2:])  # Bỏ "BH" để lấy số
            new_id = f"BH{last_number + 1:03d}"
        else:
            new_id = "BH001"
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã bảo hiểm tự động nếu chưa có """
        if 'insurance_id' not in vals or not vals['insurance_id']:
            vals['insurance_id'] = self._generate_insurance_id()
        return super(CongTyBaoHiem, self).create(vals)
