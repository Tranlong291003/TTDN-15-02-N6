from odoo import models, fields, api

class LichTrinh(models.Model):
    _name = 'lich_trinh'
    _description = '📅 Quản lý Lịch Trình'

    schedule_id = fields.Char(
        string='🆔 Mã Lịch Trình',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._generate_schedule_id()
    )

    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)
    driver_id = fields.Many2one('tai_xe', string='👨‍✈️ Tài Xế', required=True)
    start_time = fields.Datetime(string='⏰ Thời Gian Xuất Phát', required=True)
    end_time = fields.Datetime(string='🏁 Thời Gian Về')
    start_location = fields.Char(string='📍 Địa Điểm Xuất Phát', required=True)
    end_location = fields.Char(string='📌 Đích Đến', required=True)
    status = fields.Selection([
        ('pending', '⏳ Chưa Bắt Đầu'),
        ('in_progress', '🚗 Đang Thực Hiện'),
        ('completed', '✅ Đã Hoàn Thành')
    ], string='📊 Trạng Thái', default='pending')
    notes = fields.Text(string='📝 Ghi Chú Hành Trình')

    _sql_constraints = [
        ('schedule_id_uniq', 'unique(schedule_id)', '🆔 Mã Lịch Trình không được trùng! Vui lòng nhập lại.')
    ]

    @api.model
    def _generate_schedule_id(self):
        """ Tạo mã lịch trình tự động (LT001, LT002, ...) """
        last_record = self.search([], order="schedule_id desc", limit=1)
        if last_record and last_record.schedule_id:
            last_number = int(last_record.schedule_id[2:])  # Bỏ "LT" lấy số
            new_id = f"LT{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "LT001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã lịch trình tự động nếu chưa có """
        if 'schedule_id' not in vals or not vals['schedule_id']:
            vals['schedule_id'] = self._generate_schedule_id()
        return super(LichTrinh, self).create(vals)
