from odoo import models, fields

class HangSanXuat(models.Model):
    _name = "hang_san_xuat"
    _description = "Hãng Sản Xuất"

    phuong_tien_ids = fields.One2many('phuong_tien', 'manufacturer_id', string='🚗 Danh Sách Phương Tiện')



    name = fields.Char(string="Tên hãng sản xuất", required=True)
    country = fields.Char(string="Quốc gia")
    logo = fields.Binary(string="Logo")
    description = fields.Text(string="Mô tả ")
