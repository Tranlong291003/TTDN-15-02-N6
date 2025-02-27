from odoo import models, fields, api
from datetime import timedelta

class HopDongBaoHiem(models.Model):
    _name = 'hop_dong_bao_hiem'
    _description = 'Quản lý Hợp Đồng & Bảo Hiểm'

    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)
    contract_start = fields.Date(string='📅 Ngày Bắt Đầu', required=True)
    contract_end = fields.Date(string='📅 Ngày Kết Thúc', compute='_compute_contract_end', store=True)

    insurance_package_id = fields.Many2one(
        'cong_ty_bao_hiem',
        string='📜 Gói Bảo Hiểm',
        required=True
    )

    insurance_package = fields.Char(
        string='📄 Gói Bảo Hiểm (Hiển Thị)',
        related='insurance_package_id.full_name',
        store=True,
        readonly=True
    )

    insurance_price = fields.Float(
        string='💰 Số Tiền Bảo Hiểm',
        related='insurance_package_id.insurance_price',
        store=True,
        readonly=True
    )

    @api.depends('contract_start')
    def _compute_contract_end(self):
        """Tự động tính ngày kết thúc hợp đồng = ngày bắt đầu + 365 ngày"""
        for record in self:
            if record.contract_start:
                record.contract_end = record.contract_start + timedelta(days=365)
            else:
                record.contract_end = False  # Tránh lỗi nếu không có ngày bắt đầu
