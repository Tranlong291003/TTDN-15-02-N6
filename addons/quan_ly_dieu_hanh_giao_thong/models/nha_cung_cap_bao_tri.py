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
        """ Kiểm tra điều kiện trước khi tạo nhà cung cấp bảo trì """
        new_record = super(NhaCungCapBaoTri, self).create(vals)

        # Ghi lại thao tác vào lịch sử
        self.env['lich_su_thao_tac'].create({
            'model_name': 'nha_cung_cap_bao_tri',
            'record_id': new_record.id,
            'action_type': 'create',
            'action_details': f"Thêm nhà cung cấp bảo trì: {new_record.name} (Mã nhà cung cấp: {new_record.supplier_id})",
            'user_id': self.env.user.id,
            'action_date': fields.Datetime.now(),
        })

        return new_record

    def write(self, vals):
        """ Ghi lại thao tác sửa nhà cung cấp bảo trì vào lịch sử """
        result = super(NhaCungCapBaoTri, self).write(vals)

        # Ghi lại thao tác sửa vào lịch sử
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'nha_cung_cap_bao_tri',
                'record_id': record.id,
                'action_type': 'update',
                'action_details': f"Cập nhật nhà cung cấp bảo trì: {record.name} (Mã nhà cung cấp: {record.supplier_id})",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return result

    def unlink(self):
        """ Ghi lại thao tác xóa nhà cung cấp bảo trì vào lịch sử """
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'nha_cung_cap_bao_tri',
                'record_id': record.id,
                'action_type': 'delete',
                'action_details': f"Xóa nhà cung cấp bảo trì: {record.name} (Mã nhà cung cấp: {record.supplier_id})",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return super(NhaCungCapBaoTri, self).unlink()