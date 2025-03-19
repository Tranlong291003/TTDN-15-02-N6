from odoo import models, fields, api

class HangSanXuat(models.Model):
    _name = "hang_san_xuat"
    _description = "Hãng Sản Xuất"

    # Quan hệ với bảng phương tiện
    phuong_tien_ids = fields.One2many('phuong_tien', 'manufacturer_id', string='🚗 Danh Sách Phương Tiện')

    # Các trường thông tin về hãng sản xuất
    name = fields.Char(string="Tên hãng sản xuất", required=True)
    country = fields.Char(string="Quốc gia")
    logo = fields.Binary(string="Logo")
    description = fields.Text(string="Mô tả")

    @api.model
    def create(self, vals):
        """ Tạo bản ghi hãng sản xuất mới và ghi lại thao tác vào lịch sử """
        new_record = super(HangSanXuat, self).create(vals)

        # Ghi lại thao tác vào lịch sử
        self.env['lich_su_thao_tac'].create({
            'model_name': 'hang_san_xuat',
            'record_id': new_record.id,
            'action_type': 'create',
            'action_details': f"Thêm hãng sản xuất mới: {new_record.name}",
            'user_id': self.env.user.id,
            'action_date': fields.Datetime.now(),
        })

        return new_record

    def write(self, vals):
        """ Ghi lại thao tác sửa hãng sản xuất vào lịch sử """
        result = super(HangSanXuat, self).write(vals)

        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'hang_san_xuat',
                'record_id': record.id,
                'action_type': 'update',
                'action_details': f"Cập nhật hãng sản xuất: {record.name}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return result

    def unlink(self):
        """ Ghi lại thao tác xóa hãng sản xuất vào lịch sử """
        for record in self:
            self.env['lich_su_thao_tac'].create({
                'model_name': 'hang_san_xuat',
                'record_id': record.id,
                'action_type': 'delete',
                'action_details': f"Xóa hãng sản xuất: {record.name}",
                'user_id': self.env.user.id,
                'action_date': fields.Datetime.now(),
            })

        return super(HangSanXuat, self).unlink()
