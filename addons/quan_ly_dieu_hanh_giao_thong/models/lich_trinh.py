from odoo import models, fields

class LichTrinh(models.Model):
    _name = 'lich_trinh'
    _description = 'Quản lý Lịch Trình'

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
