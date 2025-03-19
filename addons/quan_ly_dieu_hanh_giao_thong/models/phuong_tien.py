from odoo import models, fields, api
from datetime import datetime

class PhuongTien(models.Model):
    _name = 'phuong_tien'
    _description = 'Quản lý Phương Tiện'

    vehicle_id = fields.Char(
        string='🆔 Mã Phương Tiện', 
        required=True, 
        copy=False, 
        index=True,
        unique=True
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

    # Cập nhật giá thuê ngày với tiền tệ VNĐ
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    daily_rental_rate = fields.Monetary(string="💵 Giá Thuê/Ngày", required=True, default=0.0, currency_field='currency_id')

    mileage = fields.Float(string='📏 Số km đã đi')
    manufacturer_id = fields.Many2one('hang_san_xuat', string='🏭 Hãng sản xuất', required=True)
    manufacturer_name = fields.Char(related='manufacturer_id.name', string='Tên hãng sản xuất', store=True, readonly=True)

    image = fields.Binary(string='🖼 Hình ảnh phương tiện')

    # Các trường mới
    color = fields.Selection([('red', 'Đỏ'), ('blue', 'Xanh dương'), ('green', 'Xanh lá'), 
                              ('black', 'Đen'), ('white', 'Trắng'), ('yellow', 'Vàng')],
                             string='🎨 Màu sắc phương tiện', required=True)

    engine_capacity = fields.Selection([('1000', '1.0L'), ('1500', '1.5L'), ('2000', '2.0L'), 
                                        ('2500', '2.5L'), ('3000', '3.0L')],
                                       string="🔋 Dung tích động cơ (CC)", required=True)

    seats = fields.Selection([('2', '2 chỗ'), ('4', '4 chỗ'), ('5', '5 chỗ'), ('7', '7 chỗ'),
                              ('15', '15 chỗ'), ('30', '30 chỗ'), ('50', '50 chỗ')],
                             string="🪑 Số chỗ ngồi", required=True)

    created_at = fields.Datetime(string='📅 Ngày tạo phương tiện', default=fields.Datetime.now, readonly=True)
    updated_at = fields.Datetime(string='📅 Ngày cập nhật phương tiện', default=fields.Datetime.now, track_visibility='onchange')

    # Các trường liên kết với các model khác
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

    driver_id = fields.Many2one(
        'tai_xe', 
        string="👨‍✈️ Tài Xế",
        compute="_compute_driver",
        store=True
    )

    @api.depends('lich_trinh_ids.start_time', 'thue_xe_ids.rental_start')
    def _compute_driver(self):
        """ Ưu tiên lấy tài xế từ lịch trình mới nhất. Nếu không có lịch trình, lấy tài xế từ hợp đồng thuê xe gần nhất. """
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
            valid_rentals = record.thue_xe_ids.filtered(lambda r: r.rental_start)
            last_rental = valid_rentals.sorted(lambda r: r.rental_start, reverse=True)[:1]
            record.last_rental_id = last_rental.id if last_rental else False

    _sql_constraints = [
        ('vehicle_id_uniq', 'unique(vehicle_id)', '🆔 Mã Phương Tiện không được trùng!'),
        ('license_plate_uniq', 'unique(license_plate)', '🚗 Biển số xe không được trùng!')
    ]

    def create(self, vals):
        # Tạo phương tiện mới
        new_vehicle = super(PhuongTien, self).create(vals)

        # Ghi lại thao tác vào lịch sử
        self.env['lich_su_thao_tac'].create({
            'model_name': 'phuong_tien',
            'record_id': new_vehicle.id,
            'action_type': 'create',
            'action_details': f"Thêm phương tiện mới: {new_vehicle.name}",
            'user_id': self.env.user.id,
            'action_date': fields.Datetime.now(),
        })

        return new_vehicle

    def write(self, vals):
        # Ghi lại thao tác vào lịch sử khi sửa phương tiện
        result = super(PhuongTien, self).write(vals)

        # Ghi lại thao tác sửa phương tiện vào lịch sử
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'phuong_tien',
                'record_id': record.id,
                'action_type': 'update',
                'action_details': f"Cập nhật phương tiện: {record.name}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })
        return result

    def unlink(self):
        # Ghi lại thao tác vào lịch sử khi xóa phương tiện
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'phuong_tien',
                'record_id': record.id,
                'action_type': 'delete',
                'action_details': f"Xóa phương tiện: {record.name}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })
        
        return super(PhuongTien, self).unlink()