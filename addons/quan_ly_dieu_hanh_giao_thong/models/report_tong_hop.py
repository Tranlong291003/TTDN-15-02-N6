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

    chart_pie_vehicles = fields.Char(string="Chart Pie")
    chart_bar_types = fields.Char(string="Chart Bar")

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
                    (SELECT COUNT(*) FROM tai_xe) AS total_drivers,
                    '{}' AS chart_pie_vehicles,  -- Placeholder for pie chart data
                    '{}' AS chart_bar_types  -- Placeholder for bar chart data
            )
        """)
        # Update chart fields after initializing the data
        self.update_charts()

    def update_charts(self):
        """ Update pie and bar chart data with dynamic values. """
        # Create data for Pie Chart: Available, Rented, and Maintenance vehicles
        pie_chart_data = {
            'available': self.available_vehicles,
            'rented': self.rented_vehicles,
            'maintenance': self.maintenance_vehicles,
        }

        # Create data for Bar Chart: Type 1 for Total Vehicles, Type 2 for Total Drivers
        bar_chart_data = {
            'Type 1': self.total_vehicles,
            'Type 2': self.total_drivers,
        }

        # Convert dictionary data to string (could use JSON or a custom format)
        self.chart_pie_vehicles = str(pie_chart_data)
        self.chart_bar_types = str(bar_chart_data)

