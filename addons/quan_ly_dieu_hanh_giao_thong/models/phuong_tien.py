from odoo import models, fields, api
from datetime import datetime

class PhuongTien(models.Model):
    _name = 'phuong_tien'
    _description = 'Quản lý Phương Tiện'

    driver_id = fields.Many2one('tai_xe', string='Tài xế phụ trách')
    bao_tri_ids = fields.One2many('bao_tri', 'vehicle_id', string="Lịch Sử Bảo Trì")
    lich_trinh_ids = fields.One2many('lich_trinh', 'vehicle_id', string="Lịch Trình")
    nhien_lieu_ids = fields.One2many('nhien_lieu', 'vehicle_id', string="⛽ Lịch Sử Đổ Nhiên Liệu")
    hop_dong_bao_hiem_ids = fields.One2many('hop_dong_bao_hiem', 'vehicle_id', string="📜 Hợp Đồng Bảo Hiểm")


    name = fields.Char(string='Tên phương tiện', required=True)
    license_plate = fields.Char(string='Biển số xe', required=True)
    vehicle_type = fields.Selection([
        ('truck', 'Xe tải'),
        ('bus', 'Xe buýt'),
        ('car', 'Xe con'),
        ('motobike', 'Xe máy'),
    ], string='Loại phương tiện', required=True)
    status = fields.Selection([
        ('available', 'Sẵn sàng'),
        ('in_use', 'Đang sử dụng'),
        ('maintenance', 'Bảo trì'),
        ('broken', 'Hỏng hóc')
    ], string='Trạng thái', default='available')
    mileage = fields.Float(string='Số km đã đi')

    # Chỉnh sửa manufacture_year thành Selection
    manufacture_year = fields.Selection(
        [(str(year), str(year)) for year in range(datetime.now().year, 1979, -1)],
        string='Năm sản xuất',
        required=True
    )

    manufacturer_id = fields.Many2one('hang_san_xuat', string='Hãng sản xuất', required=True)
    manufacturer_name = fields.Char(related='manufacturer_id.name', string='Tên hãng sản xuất', store=True, readonly=True)

    image = fields.Binary(string='Hình ảnh phương tiện')
