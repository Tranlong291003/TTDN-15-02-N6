from odoo import models, fields, api

class BaoCaoTongHop(models.Model):
    _name = 'bao_cao.tong_hop'
    _description = '📊 Báo Cáo Tổng Hợp'
    _auto = False  # Không tạo bảng trong database, chỉ dùng cho báo cáo

    total_rentals = fields.Integer(string="📅 Tổng Số Đơn Thuê Xe")
    total_revenue = fields.Float(string="💵 Tổng Doanh Thu")
    total_vehicles = fields.Integer(string="🚗 Tổng Số Xe")
    available_vehicles = fields.Integer(string="✅ Xe Có Sẵn")
    rented_vehicles = fields.Integer(string="🚗 Xe Đang Thuê")
    maintenance_vehicles = fields.Integer(string="🛠️ Xe Bảo Trì")
    total_violations = fields.Integer(string="⚠️ Tổng Vi Phạm")
    total_maintenance_cost = fields.Float(string="💰 Chi Phí Bảo Trì")
    total_drivers = fields.Integer(string="👨‍✈️ Tổng Số Tài Xế")

    @api.model
    def init(self):
        """ Tạo view SQL để tổng hợp dữ liệu báo cáo """
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW bao_cao_tong_hop AS (
                SELECT
                    1 AS id,  -- Báo cáo tổng hợp chỉ có một dòng
                    (SELECT COUNT(*) FROM thue_xe WHERE status != 'cancelled') AS total_rentals,
                    (SELECT SUM(total_price) FROM thue_xe WHERE status IN ('confirmed', 'completed')) AS total_revenue,
                    (SELECT COUNT(*) FROM phuong_tien) AS total_vehicles,
                    (SELECT COUNT(*) FROM phuong_tien WHERE status = 'available') AS available_vehicles,
                    (SELECT COUNT(*) FROM phuong_tien WHERE status = 'rented') AS rented_vehicles,
                    (SELECT COUNT(*) FROM phuong_tien WHERE status = 'maintenance') AS maintenance_vehicles,
                    (SELECT COUNT(*) FROM vi_pham) AS total_violations,
                    (SELECT SUM(cost) FROM bao_tri) AS total_maintenance_cost,
                    (SELECT COUNT(*) FROM tai_xe) AS total_drivers
            )
        """)
