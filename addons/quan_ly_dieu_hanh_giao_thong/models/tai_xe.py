from odoo import models, fields, api

class TaiXe(models.Model):
    _name = 'tai_xe'
    _description = '🚛 Quản lý Tài Xế'

    driver_id = fields.Char(
        string='🆔 Mã Tài Xế',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._generate_driver_id()
    )

    name = fields.Char(string='👤 Họ Tên', required=True)
    phone = fields.Char(string='📞 Số Điện Thoại')
    email = fields.Char(string='📧 Email')
    license_number = fields.Char(string='🚘 Số Bằng Lái')
    license_issue_date = fields.Date(string='📅 Ngày Cấp')
    license_expiry_date = fields.Date(string='⏳ Ngày Hết Hạn')
    experience = fields.Integer(string='🏎️ Kinh Nghiệm Lái Xe (Năm)')
    rating = fields.Float(string='⭐ Đánh Giá Tài Xế')
    image = fields.Binary(string='📸 Ảnh Tài Xế')
    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện Phụ Trách')

    _sql_constraints = [
        ('driver_id_uniq', 'unique(driver_id)', '🆔 Mã Tài Xế không được trùng! Vui lòng nhập lại.')
    ]

    @api.model
    def _generate_driver_id(self):
        """ Tạo mã tài xế tự động (TX001, TX002, ...) """
        last_record = self.search([], order="driver_id desc", limit=1)
        if last_record and last_record.driver_id:
            last_number = int(last_record.driver_id[2:])  # Bỏ "TX" lấy số
            new_id = f"TX{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "TX001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã tài xế tự động nếu chưa có """
        if 'driver_id' not in vals or not vals['driver_id']:
            vals['driver_id'] = self._generate_driver_id()
        return super(TaiXe, self).create(vals)
