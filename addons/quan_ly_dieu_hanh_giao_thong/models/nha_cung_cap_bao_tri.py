from odoo import models, fields, api, _

class NhaCungCapBaoTri(models.Model):
    _name = 'nha_cung_cap_bao_tri'
    _description = 'Nhà Cung Cấp Dịch Vụ Bảo Trì'

    supplier_id = fields.Char(
        string='🆔 Mã Nhà Cung Cấp', 
        required=True, 
        copy=False, 
        readonly=True, 
        index=True, 
        default=lambda self: self._generate_supplier_id()
    )
    bao_tri_ids = fields.One2many('bao_tri', 'service_provider_id', string="Lịch Sử Bảo Trì")

    name = fields.Char(string='🏢 Nhà Cung Cấp', required=True)
    contact_person = fields.Char(string='👤 Người Liên Hệ')
    phone = fields.Char(string='📞 Số Điện Thoại')
    email = fields.Char(string='📧 Email')
    address = fields.Text(string='📍 Địa Chỉ')

    _sql_constraints = [
        ('unique_supplier_id', 'unique(supplier_id)', '🆔 Mã Nhà Cung Cấp không được trùng!'),
        ('unique_supplier_name', 'unique(name)', '🏢 Tên nhà cung cấp đã tồn tại! Vui lòng nhập tên khác.')
    ]

    @api.model
    def _generate_supplier_id(self):
        """ Tạo ID tự động cho nhà cung cấp (NC001, NC002, ...) """
        last_record = self.search([], order="supplier_id desc", limit=1)
        if last_record and last_record.supplier_id:
            last_number = int(last_record.supplier_id[2:])  # Bỏ "NC" lấy số
            new_id = f"NC{last_number + 1:03d}"  # Tạo ID mới
        else:
            new_id = "NC001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã nhà cung cấp tự động nếu chưa có """
        if 'supplier_id' not in vals or not vals['supplier_id']:
            vals['supplier_id'] = self._generate_supplier_id()
        return super(NhaCungCapBaoTri, self).create(vals)
