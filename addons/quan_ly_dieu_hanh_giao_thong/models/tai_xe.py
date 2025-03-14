from odoo import models, fields, api
from datetime import datetime

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
    
    phuong_tien_ids = fields.One2many('phuong_tien', 'driver_id', string="Quản lý phương tiện")

    # Gộp firstName và lastName thành name
    name = fields.Char(string='👤 Tên tài xế', required=True)
    
    # Các trường còn lại
    dob = fields.Date(string='Ngày sinh', required=True)
    license_number = fields.Char(string='Số giấy phép lái xe', required=True, unique=True)
    hire_date = fields.Date(string='Ngày tuyển dụng', required=True)
    
    phone = fields.Char(string='Số điện thoại')
    email = fields.Char(string='Email')

    # Kinh nghiệm lái xe (Selection) - Thêm lựa chọn logic cho khoảng thời gian kinh nghiệm
    experience = fields.Selection(
        [('0', '<1 năm'), 
         ('1-2', '1-2 năm'),
         ('2-3', '2-3 năm'),
         ('3+', '3 năm trở lên')],
        string='🏎️ Kinh nghiệm',
        required=True
    )

    # Đánh giá tài xế (Selection)
    rating = fields.Selection(
        [('1', '1 ⭐'),
         ('2', '2 ⭐'),
         ('3', '3 ⭐'),
         ('4', '4 ⭐'),
         ('5', '5 ⭐')],
        string='⭐ Đánh Giá',
        required=True
    )

    image = fields.Binary(string='Ảnh tài xế')

    # Liên kết với phương tiện
    vehicle_id = fields.Many2one('phuong_tien', string='Phương tiện phụ trách')

    # Thêm trường ngày tạo và ngày cập nhật
    created_at = fields.Datetime(
        string='Ngày tạo tài xế', 
        default=fields.Datetime.now, 
        readonly=True
    )
    
    updated_at = fields.Datetime(
        string='Ngày cập nhật tài xế', 
        default=fields.Datetime.now, 
        track_visibility='onchange'
    )

    # Trạng thái tài xế
    status = fields.Selection([
        ('active', 'Đang làm việc'),
        ('onLeave', 'Nghỉ phép'),
        ('retired', 'Đã nghỉ việc')
    ], string='Trạng thái', default='active')

    _sql_constraints = [
        ('driver_id_uniq', 'unique(driver_id)', '🆔 Mã Tài Xế không được trùng! Vui lòng nhập lại.'),
        ('license_number_uniq', 'unique(license_number)', 'Số giấy phép lái xe không được trùng!')
    ]

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
