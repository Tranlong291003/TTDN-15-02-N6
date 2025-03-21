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
    ], string='📌 Trạng Thái', default='available')

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        default=lambda self: self.env.company.currency_id
    )
    daily_rental_rate = fields.Monetary(
        string="💵 Giá Thuê/Ngày", 
        required=True, 
        default=0.0, 
        currency_field='currency_id'
    )
    
    mileage = fields.Float(string='📏 Số km đã đi', digits=(12, 0))

    manufacturer_id = fields.Many2one('hang_san_xuat', string='🏭 Hãng sản xuất', required=True)
    manufacturer_name = fields.Char(related='manufacturer_id.name', string='Tên hãng sản xuất', store=True, readonly=True)

    image = fields.Binary(string='🖼 Hình ảnh PT')

    
    
    engine_capacity = fields.Selection(
    [
        ('1', '1 Tấn'),
        ('1.5', '1.5 Tấn'),
        ('2', '2 Tấn'),
        ('2.5', '2.5 Tấn'),
        ('3', '3 Tấn'),
    ],
    string="🔋 Trọng Lượng",

)


    seats = fields.Selection(
        [
            ('2', '2 chỗ'),
            ('4', '4 chỗ'),
            ('5', '5 chỗ'),
            ('7', '7 chỗ'),
            ('15', '15 chỗ'),
            ('30', '30 chỗ'),
            ('50', '50 chỗ'),
        ],
        string="🪑 Số chỗ ngồi", 
    )

    created_at = fields.Datetime(
        string='📅 Ngày tạo phương tiện', 
        default=fields.Datetime.now,
        readonly=True
    )

    updated_at = fields.Datetime(
        string='📅 Ngày cập nhật phương tiện', 
        default=fields.Datetime.now, 
        track_visibility='onchange'
    )

    thue_xe_ids = fields.One2many('thue_xe', 'vehicle_id', string="📜 Hợp Đồng Thuê Xe")
    lich_trinh_ids = fields.One2many('lich_trinh', 'vehicle_id', string="📅 Lịch Trình")
    bao_tri_ids = fields.One2many('bao_tri', 'vehicle_id', string="🛠️ Lịch Sử Bảo Trì")
    nhien_lieu_ids = fields.One2many('nhien_lieu', 'vehicle_id', string="⛽ Lịch Sử Đổ Nhiên Liệu")
    hop_dong_bao_hiem_ids = fields.One2many('hop_dong_bao_hiem', 'vehicle_id', string="📜 Hợp Đồng Bảo Hiểm")
    vi_pham_ids = fields.One2many('vi_pham', 'vehicle_id', string="⚠️ Vi phạm")
    pending_in_progress_schedule_ids = fields.One2many(
        'lich_trinh', 
        'vehicle_id', 
        string="Lịch Trình Đang Xử Lý và Chưa Bắt Đầu", 
        compute="_compute_pending_in_progress_schedules", 
        store=True
    )

    completed_schedule_ids = fields.One2many(
        'lich_trinh', 
        'vehicle_id', 
        string="📅 Lịch Trình Đã Hoàn Thành", 
        compute='_compute_completed_schedules'
    )

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
    @api.depends('lich_trinh_ids.status')
    def _compute_completed_schedules(self):
        for record in self:
            # Lọc các lịch trình có trạng thái "completed"
            completed_schedules = self.env['lich_trinh'].search([('status', '=', 'completed'), ('vehicle_id', '=', record.id)])
            record.completed_schedule_ids = completed_schedules
    @api.depends('lich_trinh_ids.status')
    def _compute_pending_in_progress_schedules(self):
        for record in self:
        # Lọc các lịch trình có trạng thái "pending" hoặc "in_progress"
            pending_in_progress_schedules = self.env['lich_trinh'].search([
            ('status', 'in', ['pending', 'in_progress']),
            ('vehicle_id', '=', record.id)
        ])
        # Gán kết quả cho trường completed_schedule_ids (hoặc tạo trường riêng cho pending và in_progress)
        record.pending_in_progress_schedule_ids = pending_in_progress_schedules

    @api.model
    def create(self, vals):
        """ Ghi lại thao tác tạo phương tiện vào lịch sử """
        new_vehicle = super(PhuongTien, self).create(vals)

        # Ghi lại thao tác tạo phương tiện vào lịch sử
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
        """ Ghi lại thao tác sửa phương tiện vào lịch sử """
        result = super(PhuongTien, self).write(vals)

        # Cập nhật trường updated_at khi có sự thay đổi
        for record in self:
            # Cập nhật ngày giờ hiện tại vào trường updated_at
            if 'updated_at' not in vals:
              # Cập nhật trường 'updated_at' mà không gọi lại 'write'
                record.updated_at = fields.Datetime.now()

            # Ghi lại thao tác sửa phương tiện vào lịch sử
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
        """ Ghi lại thao tác xóa phương tiện vào lịch sử """
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