from odoo import models, fields, api

class ViPham(models.Model):
    _name = 'vi_pham'
    _description = 'Quản lý Vi Phạm Giao Thông'

    violation_id = fields.Char(
        string='🆔 Mã Vi Phạm', 
        required=True, 
        copy=False, 
        readonly=True,  
        index=True, 
        default=lambda self: self._generate_violation_id()
    )
    vehicle_name = fields.Char(related='vehicle_id.name', store=True, string="Tên Phương Tiện")
    vehicle_license_plate = fields.Char(related='vehicle_id.license_plate', store=True, string="Biển Số")
    vehicle_type = fields.Selection(related='vehicle_id.vehicle_type', store=True, string="Loại Xe")
    vehicle_status = fields.Selection(related='vehicle_id.status', store=True, string="Trạng Thái")
    vehicle_manufacturer = fields.Many2one(related='vehicle_id.manufacturer_id', store=True, string="Hãng Sản Xuất")
    vehicle_mileage = fields.Float(related='vehicle_id.mileage', store=True, string="Số Km Đã Đi")
    driver_id = fields.Many2one('tai_xe', string='Tài xế', required=True)
    vehicle_id = fields.Many2one('phuong_tien', string='Phương tiện', required=True)
    violation_type = fields.Selection([
        ('speeding', 'Vượt tốc độ'),
        ('wrong_lane', 'Đi sai làn'),
        ('lights_off', 'Không bật đèn')
    ], string='Loại vi phạm', required=True)
    violation_date = fields.Date(string='Ngày vi phạm', required=True)
    fine_amount = fields.Float(string='Số tiền phạt')
    status = fields.Selection([
        ('pending', 'Chưa đóng phạt'),
        ('paid', 'Đã đóng phạt')
    ], string='Trạng thái', default='pending')

    _sql_constraints = [
        ('violation_id_uniq', 'unique(violation_id)', '🆔 Mã Vi Phạm không được trùng! Vui lòng nhập lại.')
    ]

    @api.model
    def _generate_violation_id(self):
        """ Tạo mã vi phạm tự động (VP001, VP002, ...) """
        last_record = self.search([], order="violation_id desc", limit=1)
        if last_record and last_record.violation_id:
            last_number = int(last_record.violation_id[2:])  # Bỏ "VP" lấy số
            new_id = f"VP{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "VP001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id

        
    @api.model
    def create(self, vals):
        """ Gán mã vi phạm tự động nếu chưa có """
        if 'violation_id' not in vals or not vals['violation_id']:
            vals['violation_id'] = self._generate_violation_id()
        
        # Tạo bản ghi vi phạm mới
        new_violation = super(ViPham, self).create(vals)

        # Ghi lại thao tác vào lịch sử
        self.env['lich_su_thao_tac'].create({
            'model_name': 'vi_pham',
            'record_id': new_violation.id,
            'action_type': 'create',
            'action_details': f"Thêm vi phạm mới: {new_violation.violation_id}",
            'user_id': self.env.user.id,
            'action_date': fields.Datetime.now(),
        })

        return new_violation

    def write(self, vals):
        """ Ghi lại thao tác sửa vi phạm vào lịch sử """
        result = super(ViPham, self).write(vals)

        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'vi_pham',
                'record_id': record.id,
                'action_type': 'update',
                'action_details': f"Cập nhật vi phạm: {record.violation_id}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return result

    def unlink(self):
        """ Ghi lại thao tác xóa vi phạm vào lịch sử """
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'vi_pham',
                'record_id': record.id,
                'action_type': 'delete',
                'action_details': f"Xóa vi phạm: {record.violation_id}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return super(ViPham, self).unlink()