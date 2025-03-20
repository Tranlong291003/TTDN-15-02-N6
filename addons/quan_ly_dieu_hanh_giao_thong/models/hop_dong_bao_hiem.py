from odoo import models, fields, api
from datetime import timedelta

class HopDongBaoHiem(models.Model):
    _name = 'hop_dong_bao_hiem'
    _description = 'Quản lý Hợp Đồng & Bảo Hiểm'

    contract_id = fields.Char(
        string='🆔 Mã Hợp Đồng', 
        required=True, 
        copy=False, 
        readonly=True,  
        index=True, 
        default=lambda self: self._generate_contract_id()
    )

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
        readonly=True,
        digits=(12, 0)
    )

    _sql_constraints = [
        ('contract_id_uniq', 'unique(contract_id)', '🆔 Mã Hợp Đồng không được trùng! Vui lòng nhập lại.')
    ]
    vehicle_id = fields.Many2one('phuong_tien', string='🚗 Phương Tiện', required=True)
    contract_start = fields.Date(string='📅 Ngày Bắt Đầu', required=True)
    contract_end = fields.Date(string='📅 Ngày Kết Thúc', compute='_compute_contract_end', store=True)
    
    # Liên kết với cong_ty_bao_hiem
    insurance_package_id = fields.Many2one('cong_ty_bao_hiem', string='📜 Gói Bảo Hiểm', required=True)

    insurance_package = fields.Char(related='insurance_package_id.full_name', store=True, readonly=True)
    insurance_price = fields.Float(related='insurance_package_id.insurance_price', store=True, readonly=True)

    vehicle_name = fields.Char(related='vehicle_id.name', store=True, string="Tên Phương Tiện")
    vehicle_license_plate = fields.Char(related='vehicle_id.license_plate', store=True, string="Biển Số")
    vehicle_type = fields.Selection(related='vehicle_id.vehicle_type', store=True, string="Loại Xe")
    vehicle_status = fields.Selection(related='vehicle_id.status', store=True, string="Trạng Thái")
    vehicle_manufacturer = fields.Many2one(related='vehicle_id.manufacturer_id', store=True, string="Hãng Sản Xuất")
    vehicle_mileage = fields.Float(related='vehicle_id.mileage', store=True, string="Số Km Đã Đi")
    
    @api.depends('contract_start')
    def _compute_contract_end(self):
        """Tự động tính ngày kết thúc hợp đồng = ngày bắt đầu + 365 ngày"""
        for record in self:
            if record.contract_start:
                record.contract_end = record.contract_start + timedelta(days=365)
            else:
                record.contract_end = False  # Tránh lỗi nếu không có ngày bắt đầu

    @api.model
    def _generate_contract_id(self):
        """ Tạo mã hợp đồng tự động (HD001, HD002, ...) """
        last_record = self.search([], order="contract_id desc", limit=1)
        if last_record and last_record.contract_id:
            last_number = int(last_record.contract_id[2:])  # Bỏ "HD" lấy số
            new_id = f"HD{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "HD001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id

    @api.model
    def create(self, vals):
        """ Gán mã hợp đồng tự động nếu chưa có """
        if 'contract_id' not in vals or not vals['contract_id']:
            vals['contract_id'] = self._generate_contract_id()
        
        # Tạo bản ghi mới
        new_contract = super(HopDongBaoHiem, self).create(vals)

        # Ghi lại thao tác vào lịch sử
        self.env['lich_su_thao_tac'].create({
            'model_name': 'hop_dong_bao_hiem',
            'record_id': new_contract.id,
            'action_type': 'create',
            'action_details': f"Thêm hợp đồng bảo hiểm mới: {new_contract.contract_id}",
            'user_id': self.env.user.id,
            'action_date': fields.Datetime.now(),
        })

        return new_contract

    def write(self, vals):
        """ Ghi lại thao tác sửa hợp đồng vào lịch sử """
        result = super(HopDongBaoHiem, self).write(vals)

        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'hop_dong_bao_hiem',
                'record_id': record.id,
                'action_type': 'update',
                'action_details': f"Cập nhật hợp đồng bảo hiểm: {record.contract_id}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return result

    def unlink(self):
        """ Ghi lại thao tác xóa hợp đồng vào lịch sử """
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'hop_dong_bao_hiem',
                'record_id': record.id,
                'action_type': 'delete',
                'action_details': f"Xóa hợp đồng bảo hiểm: {record.contract_id}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return super(HopDongBaoHiem, self).unlink()