from odoo import models, fields, api
from datetime import date

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_va_ten = fields.Char("Họ và tên", required=True)
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    tuoi = fields.Integer(string="Tuổi", compute="_compute_tuoi", store=True)
    so_luong = fields.Integer(string="Số lượng", compute="_compute_so_luong", store=True)

    # Quan hệ One2many với bảng lịch sử làm việc
    history_ids = fields.One2many('lich_su_lam_viec', 'nhan_vien_id', string="Lịch sử làm việc")

    # Thêm phương thức name_get để hiển thị họ và tên thay vì ID
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.ho_va_ten))
        return result

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        today = date.today()
        for rec in self:
            if rec.ngay_sinh:
                rec.tuoi = today.year - rec.ngay_sinh.year - ((today.month, today.day) < (rec.ngay_sinh.month, rec.ngay_sinh.day))
            else:
                rec.tuoi = 0

    @api.depends('tuoi')
    def _compute_so_luong(self):
        """ Đếm số lượng nhân viên có tuổi lớn hơn 18 """
        for rec in self:
            rec.so_luong = self.env['nhan_vien'].search_count([('tuoi', '>', 18)])
        
