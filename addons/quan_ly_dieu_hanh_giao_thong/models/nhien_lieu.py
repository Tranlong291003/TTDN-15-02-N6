from odoo import models, fields, api

class NhienLieu(models.Model):
    _name = 'nhien_lieu'
    _description = '⛽ Quản lý Nhiên Liệu'

    RON95_PRICE = 23000  # Giá xăng Ron95 hiện tại (VND/lít)
    DEFAULT_EFFICIENCY = 10  # Hiệu suất tiêu hao mặc định (km/lít)
    TANK_CAPACITY = 50  # Dung tích bình xăng mặc định (nếu không có thông tin từ phương tiện)

    fuel_id = fields.Char(
        string='🆔 Mã Nhiên Liệu',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._generate_fuel_id()
    )

    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)

    # Chỉ liên kết related với biển số xe và số km trước khi đổ
    previous_km = fields.Float(
        string="📏 Số Km Trước Khi Đổ",
        related='vehicle_id.mileage',
        readonly=True
    )
    
    license_plate = fields.Char(
        string="🔤 Biển Số Xe",
        related='vehicle_id.license_plate',
        readonly=True
    )

    date = fields.Date(string='📅 Ngày Đổ Nhiên Liệu', required=True)
    current_km = fields.Float(string='📏 Odometer (km)', required=True)
    fuel_price = fields.Float(string='💰 Giá Xăng (nghìn VND)', required=True)
    fuel_liters = fields.Float(string='⛽ Số Lít Nhiên Liệu', readonly=True)
    driven_km = fields.Float(string='📏 Km Đã Đi Được', readonly=True)
    fuel_efficiency = fields.Float(string='📉 Hiệu Suất (km/lít)', readonly=True)
    estimated_range = fields.Float(string='🚀 Km Dự Kiến Đổ Lại', readonly=True)
    notes = fields.Text(string="📝 Ghi Chú")

    _sql_constraints = [
        ('fuel_id_uniq', 'unique(fuel_id)', '🆔 Mã Nhiên Liệu không được trùng! Vui lòng nhập lại.')
    ]

    @api.model
    def _generate_fuel_id(self):
        """Tạo mã nhiên liệu tự động (NL001, NL002, ...)"""
        last_record = self.search([], order="fuel_id desc", limit=1)
        if last_record and last_record.fuel_id:
            last_number = int(last_record.fuel_id[2:])  # Bỏ "NL" để lấy số
            new_id = f"NL{last_number + 1:03d}"
        else:
            new_id = "NL001"
        return new_id

    @api.model
    def create(self, vals):
        """
        Khi tạo bản ghi đổ xăng:
        1. Tính số lít nhiên liệu từ số tiền (VND) và giá xăng.
        2. Tính số km đã đi từ lần đổ xăng trước (nếu có dữ liệu hợp lệ).
        3. Tính hiệu suất tiêu hao nhiên liệu (km/lít) nếu có dữ liệu hợp lệ.
        4. Ước tính số km dự kiến đổ lại: current_km + (fuel_liters * fuel_efficiency).
        5. Cập nhật số km mới nhất vào phương tiện.
        """
        ron95_price = self.RON95_PRICE

        # 1. Tính số lít nhiên liệu đã đổ vào
        amount_vnd = vals.get('fuel_price', 0) * 1000  # Đổi từ nghìn VND sang VND
        computed_liters = amount_vnd / ron95_price if ron95_price > 0 else 0
        vals['fuel_liters'] = computed_liters

        # 2. Lấy số km hiện tại
        new_km = vals.get('current_km', 0)

        # 3. Lấy phương tiện và số km lần đổ trước
        vehicle = self.env['phuong_tien'].browse(vals.get('vehicle_id'))
        old_mileage = vehicle.mileage if vehicle and vehicle.mileage else 0

        # 4. Tính số km đã đi được
        if new_km > old_mileage:
            driven_km = new_km - old_mileage
        else:
            driven_km = 0  # Nếu số km hiện tại không lớn hơn km cũ, bỏ qua tính toán
        vals['driven_km'] = driven_km

        # 5. Tính hiệu suất tiêu hao (km/lít)
        if computed_liters > 0 and driven_km > 0:
            efficiency = driven_km / computed_liters
        else:
            efficiency = self.DEFAULT_EFFICIENCY  # Nếu không có đủ dữ liệu, dùng mặc định
        vals['fuel_efficiency'] = efficiency

        # 6. Dự báo số km dự kiến đổ lại
        estimated_range = new_km + (computed_liters * efficiency)
        vals['estimated_range'] = estimated_range

        # 7. Tạo bản ghi đổ nhiên liệu
        record = super(NhienLieu, self).create(vals)

        # 8. Cập nhật mileage của phương tiện nếu số km hiện tại hợp lệ
        if vehicle and new_km > old_mileage:
            vehicle.mileage = new_km

        return record
