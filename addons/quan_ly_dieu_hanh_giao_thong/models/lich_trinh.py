from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class LichTrinh(models.Model):
    _name = 'lich_trinh'
    _description = '📅 Quản lý Lịch Trình'

    # Thông tin lịch trình
    schedule_id = fields.Char(
        string='🆔 Mã Lịch Trình',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._generate_schedule_id()
    )

    # Liên kết với phương tiện và tài xế
    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)
    driver_id = fields.Many2one('tai_xe', string='👨‍✈️ Tài Xế', required=True)

    # Các thông tin liên quan đến phương tiện
    vehicle_name = fields.Char(related='vehicle_id.name', store=True, string="Tên Phương Tiện")
    vehicle_license_plate = fields.Char(related='vehicle_id.license_plate', store=True, string="Biển Số")
    vehicle_type = fields.Selection(related='vehicle_id.vehicle_type', store=True, string="Loại Xe")
    vehicle_status = fields.Selection(related='vehicle_id.status', store=True, string="Trạng Thái")
    vehicle_manufacturer = fields.Many2one(related='vehicle_id.manufacturer_id', store=True, string="Hãng Sản Xuất")
    vehicle_mileage = fields.Float(related='vehicle_id.mileage', store=True, string="Số Km Đã Đi")

    # Thời gian và địa điểm
    start_time = fields.Datetime(string='⏰ Thời Gian Xuất Phát', required=True)
    end_time = fields.Datetime(string='🏁 Thời Gian Về', required=True)

    start_location = fields.Char(string='📍 Địa Điểm Xuất Phát', required=True)
    end_location = fields.Char(string='📌 Đích Đến', required=True)

    # Mục đích sử dụng phương tiện (Selection)
    purpose = fields.Selection([
        ('work', 'Công việc'),
        ('transportation', 'Vận chuyển'),
        ('other', 'Khác')
    ], string='Mục Đích Sử Dụng', required=True)

    # Trạng thái lịch trình
    status = fields.Selection([
        ('pending', '⏳ Chưa Bắt Đầu'),
        ('in_progress', '🚗 Đang Thực Hiện'),
        ('completed', '✅ Đã Hoàn Thành')
    ], string='📊 Trạng Thái', default='pending')

    # Ghi chú
    notes = fields.Text(string='📝 Ghi Chú Hành Trình')

    # Tự động điền thời gian tạo và cập nhật
    created_at = fields.Datetime(
        string='Ngày tạo lịch trình',
        default=fields.Datetime.now,
        readonly=True
    )
    updated_at = fields.Datetime(
        string='Ngày cập nhật lịch trình',
        default=fields.Datetime.now,
        track_visibility='onchange'
    )

    _sql_constraints = [
        ('schedule_id_uniq', 'unique(schedule_id)', '🆔 Mã Lịch Trình không được trùng! Vui lòng nhập lại.')
    ]

    @api.constrains('start_time', 'end_time')
    def _check_schedule_dates(self):
        """ ✅ Kiểm tra ngày bắt đầu phải nhỏ hơn ngày kết thúc và không trùng lịch trình xe """
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError("🚫 Thời gian xuất phát phải nhỏ hơn thời gian kết thúc!")

            # Kiểm tra xe có bị trùng lịch trình không
            overlapping_schedules = self.env['lich_trinh'].search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('id', '!=', record.id),  # Loại trừ chính bản ghi hiện tại
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time)
            ])
            if overlapping_schedules:
                raise ValidationError("🚗 Phương tiện này đã có lịch trình khác trong khoảng thời gian này!")

    @api.model
    def _generate_schedule_id(self):
        """ ✅ Tạo mã lịch trình tự động (LT001, LT002, ...) """
        last_record = self.search([], order="schedule_id desc", limit=1)
        if last_record and last_record.schedule_id:
            last_number = int(last_record.schedule_id[2:])  # Bỏ "LT" lấy số
            new_id = f"LT{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "LT001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id


    @api.model
    def create(self, vals):
        # Tạo lịch trình mới
        new_schedule = super(LichTrinh, self).create(vals)

        # Ghi lại thao tác vào lịch sử
        self.env['lich_su_thao_tac'].create({
            'model_name': 'lich_trinh',
            'record_id': new_schedule.id,
            'action_type': 'create',
            'action_details': f"Thêm lịch trình mới: {new_schedule.schedule_id}",
            'user_id': self.env.user.id,
            'action_date': fields.Datetime.now(),
        })

        return new_schedule

    # Phương thức cập nhật lịch trình
    def write(self, vals):
        # Cập nhật lịch trình
        result = super(LichTrinh, self).write(vals)

        # Ghi lại thao tác sửa lịch trình vào lịch sử
        for record in self:

            if 'updated_at' not in vals:
              # Cập nhật trường 'updated_at' mà không gọi lại 'write'
                record.updated_at = fields.Datetime.now()


            self.env['lich_su_thao_tac'].create({
                'model_name': 'lich_trinh',
                'record_id': record.id,
                'action_type': 'update',
                'action_details': f"Cập nhật lịch trình: {record.schedule_id}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return result

    # Phương thức xóa lịch trình
    def unlink(self):
        # Ghi lại thao tác vào lịch sử khi xóa lịch trình
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'lich_trinh',
                'record_id': record.id,
                'action_type': 'delete',
                'action_details': f"Xóa lịch trình: {record.schedule_id}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return super(LichTrinh, self).unlink()