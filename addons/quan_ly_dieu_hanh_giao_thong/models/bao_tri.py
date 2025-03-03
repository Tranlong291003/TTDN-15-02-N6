from odoo import models, fields, api
from datetime import timedelta

class BaoTri(models.Model):
    _name = 'bao_tri'
    _description = 'Quản lý Bảo Trì'

    maintenance_id = fields.Char(
        string='🆔 Mã Bảo Trì', 
        required=True, 
        copy=False, 
        readonly=True,  
        index=True, 
        default=lambda self: self._generate_maintenance_id()
    )

    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)
    maintenance_date = fields.Date(string='📅 Ngày Bảo Trì', required=True, default=fields.Date.today)
    maintenance_type = fields.Selection([
        ('repair', '🔧 Sửa chữa'),
        ('replacement', '🛠️ Thay thế linh kiện')
    ], string='📑 Loại Bảo Trì', required=True)

    details = fields.Text(string='📄 Chi Tiết Sửa Chữa')
    service_provider_id = fields.Many2one('nha_cung_cap_bao_tri', string='🏢 Nhà Cung Cấp Dịch Vụ', required=True)
    cost = fields.Float(string='💰 Chi Phí Bảo Trì')

    next_maintenance = fields.Date(string='📅 Lịch Bảo Trì Tiếp Theo', compute='_compute_next_maintenance', store=True)

    _sql_constraints = [
        ('maintenance_id_uniq', 'unique(maintenance_id)', '🆔 Mã Bảo Trì không được trùng! Vui lòng nhập lại.')
    ]

    vehicle_name = fields.Char(related='vehicle_id.name', store=True, string="Tên Phương Tiện")
    vehicle_license_plate = fields.Char(related='vehicle_id.license_plate', store=True, string="Biển Số")
    vehicle_type = fields.Selection(related='vehicle_id.vehicle_type', store=True, string="Loại Xe")
    vehicle_status = fields.Selection(related='vehicle_id.status', store=True, string="Trạng Thái")
    vehicle_manufacturer = fields.Many2one(related='vehicle_id.manufacturer_id', store=True, string="Hãng Sản Xuất")
    vehicle_mileage = fields.Float(related='vehicle_id.mileage', store=True, string="Số Km Đã Đi")


    @api.depends('maintenance_date')
    def _compute_next_maintenance(self):
        """ Tự động tính ngày bảo trì tiếp theo (mặc định sau 6 tháng) """
        for record in self:
            if record.maintenance_date:
                record.next_maintenance = record.maintenance_date + timedelta(days=180)  # 6 tháng
            else:
                record.next_maintenance = False  

    @api.model
    def _generate_maintenance_id(self):
        """ Tạo mã bảo trì tự động (MT001, MT002, ...) """
        last_record = self.search([], order="maintenance_id desc", limit=1)
        if last_record and last_record.maintenance_id:
            last_number = int(last_record.maintenance_id[2:])  # Bỏ "MT" lấy số
            new_id = f"MT{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "MT001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã bảo trì tự động nếu chưa có """
        if 'maintenance_id' not in vals or not vals['maintenance_id']:
            vals['maintenance_id'] = self._generate_maintenance_id()
        return super(BaoTri, self).create(vals)
