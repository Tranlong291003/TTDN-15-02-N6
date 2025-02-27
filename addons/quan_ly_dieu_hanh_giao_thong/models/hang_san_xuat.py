from odoo import models, fields

class HangSanXuat(models.Model):
    _name = "hang_san_xuat"
    _description = "Hãng Sản Xuất"

    name = fields.Char(string="Tên hãng sản xuất", required=True)
    country = fields.Char(string="Quốc gia")
    logo = fields.Binary(string="Logo")
    description = fields.Text(string="Mô tả ")
