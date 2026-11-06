{
    'name': "Hotel management",
    'depends': ['base','mail'],
    'application': True,
    'version': '20.0.1.0.0',
    'author': "Ajnas P V",
    'license': 'LGPL-3',
    'data': [
        'seurity/ir.access.csv',
        'views/hotel_rooms_views.xml',
        'views/hotel_facilities_views.xml',
        'views/hotel_rooms_facilities_views.xml',
        'views/hotel_foods_views.xml',
        'views/hotel_foods_category_views.xml',
        'views/hotel_accommodation_views.xml',
        'data/ir_sequence_data.xml',
        'views/hotel_guests_views.xml',
        'data/demo_hotel_rooms.xml',
        'data/demo_hotel_rooms_facilities.xml',
        'data/demo_hotel_food_categories.xml',


        'views/hotel_menus.xml',
    ]
}