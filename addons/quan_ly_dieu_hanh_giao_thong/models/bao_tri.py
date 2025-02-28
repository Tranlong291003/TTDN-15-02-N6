from odoo import models, fields, api
from datetime import timedelta

class BaoTri(models.Model):
    _name = 'bao_tri'
    _description = 'Quản lý Bảo Trì'

    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)
    maintenance_date = fields.Date(string='📅 Ngày Bảo Trì', required=True, default=fields.Date.today)
    maintenance_type = fields.Selection([
        ('repair', '🔧 Sửa chữa'),
        ('replacement', '🛠️ Thay thế linh kiện')
    ], string='📑 Loại Bảo Trì', required=True)
    
    details = fields.Text(string='📄 Chi Tiết Sửa Chữa')
    service_provider = fields.Char(string='🏢 Nhà Cung Cấp Dịch Vụ')
    cost = fields.Float(string='💰 Chi Phí Bảo Trì')

    next_maintenance = fields.Date(string='📅 Lịch Bảo Trì Tiếp Theo', compute='_compute_next_maintenance', store=True)

    @api.depends('maintenance_date')
    def _compute_next_maintenance(self):
        """ Tự động tính ngày bảo trì tiếp theo (mặc định sau 6 tháng) """
        for record in self:
            if record.maintenance_date:
                record.next_maintenance = record.maintenance_date + timedelta(days=180)  # 6 tháng
            else:
                record.next_maintenance = False  # Tránh lỗi nếu không có ngày bảo trì
