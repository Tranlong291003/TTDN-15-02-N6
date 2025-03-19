from odoo import models, fields, api

class LichSuThaoTac(models.Model):
    _name = 'lich_su_thao_tac'
    _description = 'Lịch Sử Thao Tác'

    action_id = fields.Char(
        string='🆔 Mã Thao Tác', 
        required=True, 
        copy=False, 
        readonly=True,  
        index=True, 
        default=lambda self: self._generate_action_id()
    )

    model_name = fields.Char(string='Mô Hình', required=True)  # Tên model thao tác (Phương Tiện, Tài Xế, Lịch Trình,...)
    record_id = fields.Integer(string='ID Bản Ghi', required=True)  # ID bản ghi thao tác
    action_type = fields.Selection([ 
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa')
    ], string='Loại Thao Tác', required=True)  # Loại thao tác (tạo, cập nhật, xóa)
    
    action_details = fields.Text(string='Chi Tiết Thao Tác')  # Mô tả chi tiết thao tác
    user_id = fields.Many2one('res.users', string='Người Thực Hiện', required=True)  # Người thực hiện thao tác
    action_date = fields.Datetime(string='Ngày Thực Hiện', default=fields.Datetime.now, readonly=True)  # Thời gian thực hiện

    _sql_constraints = [
        ('action_id_uniq', 'unique(action_id)', '🆔 Mã Thao Tác không được trùng! Vui lòng nhập lại.')
    ]

    @api.model
    def _generate_action_id(self):
        """ Tạo mã thao tác tự động (TT001, TT002, ...) """
        last_record = self.search([], order="action_id desc", limit=1)
        if last_record and last_record.action_id:
            last_number = int(last_record.action_id[2:])  # Bỏ "TT" lấy số
            new_id = f"TT{last_number + 1:03d}"  # Định dạng ID mới
        else:
            new_id = "TT001"  # Nếu chưa có bản ghi nào thì bắt đầu từ 001
        return new_id
