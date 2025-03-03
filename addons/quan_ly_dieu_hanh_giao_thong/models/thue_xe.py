from odoo import models, fields, api
from datetime import datetime, timedelta

class ThueXe(models.Model):
    _name = 'thue_xe'
    _description = '📅 Quản Lý Đơn Thuê Xe'

    rental_id = fields.Char(
        string='🆔 Mã Thuê Xe',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._generate_rental_id()
    )

    customer_name = fields.Char(string="👤 Tên Khách Hàng", required=True)
    customer_phone = fields.Char(string="📞 SĐT Khách Hàng", required=True)
    
    vehicle_id = fields.Many2one('phuong_tien', string="🚗 Phương Tiện", required=True)
    driver_id = fields.Many2one('tai_xe', string="👨‍✈️ Tài Xế (Nếu Có)")
    
    rental_start = fields.Datetime(string="📅 Ngày Bắt Đầu", required=True)
    rental_end = fields.Datetime(string="📅 Ngày Kết Thúc", required=True)
    
    rental_days = fields.Integer(string="📆 Số Ngày Thuê", compute="_compute_rental_days", store=True)
    deposit = fields.Float(string="💰 Đặt Cọc", required=True)
    total_price = fields.Float(string="💵 Tổng Tiền", compute="_compute_total_price", store=True)

    status = fields.Selection([
        ('pending', '🕒 Chờ Xác Nhận'),
        ('confirmed', '✅ Đã Xác Nhận'),
        ('in_use', '🚗 Đang Thuê'),
        ('completed', '🎉 Hoàn Thành'),
        ('cancelled', '❌ Hủy')
    ], string="📌 Trạng Thái", default='pending', tracking=True)

    notes = fields.Text(string="📝 Ghi Chú")

    _sql_constraints = [
        ('unique_rental_id', 'unique(rental_id)', '🆔 Mã Thuê Xe không được trùng!')
    ]

    @api.depends('rental_start', 'rental_end')
    def _compute_rental_days(self):
        """ Tính số ngày thuê dựa vào ngày bắt đầu và ngày kết thúc """
        for record in self:
            if record.rental_start and record.rental_end:
                delta = record.rental_end - record.rental_start
                record.rental_days = delta.days if delta.days > 0 else 1
            else:
                record.rental_days = 1

    @api.depends('rental_days', 'vehicle_id')
    def _compute_total_price(self):
        """ Tính tổng tiền thuê = số ngày thuê * giá xe/ngày """
        for record in self:
            if record.vehicle_id and record.rental_days:
                record.total_price = record.rental_days * record.vehicle_id.daily_rental_rate
            else:
                record.total_price = 0

    @api.model
    def _generate_rental_id(self):
        """ Tạo mã thuê xe tự động (TX001, TX002, ...) """
        last_record = self.search([], order="rental_id desc", limit=1)
        if last_record and last_record.rental_id:
            last_number = int(last_record.rental_id[2:])
            new_id = f"TX{last_number + 1:03d}"
        else:
            new_id = "TX001"
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã thuê xe tự động nếu chưa có """
        if 'rental_id' not in vals or not vals['rental_id']:
            vals['rental_id'] = self._generate_rental_id()
        return super(ThueXe, self).create(vals)
