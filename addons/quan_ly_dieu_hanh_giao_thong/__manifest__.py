# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Điều Hành Giao Thông",
    'summary': "Module quản lý điều hành phương tiện giao thông",
    'description': """
        Module giúp quản lý phương tiện, tài xế, lịch trình, bảo trì và nhiên liệu
        trong hệ thống điều hành giao thông.
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Operations',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/phuong_tien.xml',
        'views/bao_tri.xml',
        'views/lich_trinh.xml',
        'views/nhien_lieu.xml',
        'views/tai_xe.xml',
        'views/vi_pham.xml',
        'views/hop_dong_bao_hiem.xml',
        'views/hang_san_xuat.xml',
        'views/cong_ty_bao_hiem.xml',
        'views/nha_cung_cap_bao_tri.xml',
        'views/thue_xe.xml',
        'views/report_tong_hop.xml',
        'views/lich_su_thao_tac.xml',




        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    

    'installable': True,
    'application': True,
    'auto_install': True,
}
