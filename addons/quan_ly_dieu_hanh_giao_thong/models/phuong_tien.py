from odoo import models, fields, api
from datetime import datetime

class PhuongTien(models.Model):
    _name = 'phuong_tien'
    _description = 'Quản lý Phương Tiện'

    vehicle_id = fields.Char(
        string='🆔 Mã Phương Tiện', 
        required=True, 
        copy=False, 
        index=True
    )
    
    name = fields.Char(string='🚘 Tên Phương Tiện', required=True)
    license_plate = fields.Char(string='🏷 Biển Số', required=True, unique=True)

    vehicle_type = fields.Selection([
        ('truck', 'Xe tải'),
        ('bus', 'Xe buýt'),
        ('car', 'Xe con'),
        ('motobike', 'Xe máy'),
    ], string='🚖 Loại Xe', required=True)

    status = fields.Selection([
        ('available', 'Sẵn sàng'),
        ('in_use', 'Đang sử dụng'),
        ('maintenance', 'Bảo trì'),
        ('broken', 'Hỏng hóc')
    ], string='📌 Trạng Thái', default='available')

    daily_rental_rate = fields.Float(string="💵 Giá Thuê/Ngày", required=True, default=0.0)
    mileage = fields.Float(string='📏 Số km đã đi')

    manufacturer_id = fields.Many2one('hang_san_xuat', string='🏭 Hãng sản xuất', required=True)
    manufacturer_name = fields.Char(related='manufacturer_id.name', string='Tên hãng sản xuất', store=True, readonly=True)

    image = fields.Binary(string='🖼 Hình ảnh phương tiện')

    thue_xe_ids = fields.One2many('thue_xe', 'vehicle_id', string="📜 Hợp Đồng Thuê Xe")
    lich_trinh_ids = fields.One2many('lich_trinh', 'vehicle_id', string="📅 Lịch Trình")
    bao_tri_ids = fields.One2many('bao_tri', 'vehicle_id', string="🛠️ Lịch Sử Bảo Trì")
    nhien_lieu_ids = fields.One2many('nhien_lieu', 'vehicle_id', string="⛽ Lịch Sử Đổ Nhiên Liệu")
    hop_dong_bao_hiem_ids = fields.One2many('hop_dong_bao_hiem', 'vehicle_id', string="📜 Hợp Đồng Bảo Hiểm")
    vi_pham_ids = fields.One2many('vi_pham', 'vehicle_id', string="⚠️ Vi phạm")

    manufacture_year = fields.Selection(
        [(str(year), str(year)) for year in range(datetime.now().year, 1979, -1)],
        string='🏭 Năm sản xuất',
        required=True
    )

    last_rental_id = fields.Many2one(
        'thue_xe', 
        string="📄 Đơn Thuê Gần Nhất", 
        compute="_compute_last_rental",
        store=True
    )


    last_customer_name = fields.Char(
        string="👤 Khách Hàng Gần Nhất",
        related="last_rental_id.customer_name",
        store=True
    )

    # ✅ Tự động cập nhật tài xế từ lịch trình mới nhất hoặc hợp đồng thuê xe mới nhất
    driver_id = fields.Many2one(
        'tai_xe', 
        string="👨‍✈️ Tài Xế",
        compute="_compute_driver",
        store=True
    )

    @api.depends('lich_trinh_ids.start_time', 'thue_xe_ids.rental_start')
    def _compute_driver(self):
        """ 
        ✅ Ưu tiên lấy tài xế từ lịch trình mới nhất.
        ✅ Nếu không có lịch trình, lấy tài xế từ hợp đồng thuê xe gần nhất.
        """
        for record in self:
            last_schedule = record.lich_trinh_ids.sorted(lambda r: r.start_time, reverse=True)[:1]
            if last_schedule:
                record.driver_id = last_schedule.driver_id
            else:
                last_rental = record.thue_xe_ids.sorted(lambda r: r.rental_start, reverse=True)[:1]
                record.driver_id = last_rental.driver_id if last_rental else False

    @api.depends('thue_xe_ids.rental_start')
    def _compute_last_rental(self):
        for record in self:
            valid_rentals = record.thue_xe_ids.filtered(lambda r: r.rental_start)  # Lọc các bản ghi có rental_start hợp lệ
            last_rental = valid_rentals.sorted(lambda r: r.rental_start, reverse=True)[:1]
            record.last_rental_id = last_rental.id if last_rental else False


    _sql_constraints = [
        ('vehicle_id_uniq', 'unique(vehicle_id)', '🆔 Mã Phương Tiện không được trùng!'),
        ('license_plate_uniq', 'unique(license_plate)', '🚗 Biển số xe không được trùng!')
    ]
