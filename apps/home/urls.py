# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('add_sensor_data', views.add_sensor_data, name='add_sensor_data'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('sensor_data_list/<str:sensor_name>/', views.sensor_data_list, name='sensor_data_list'),
    # 獲取感測器數據
    path('get_sensors/', views.get_sensors, name='get_sensors'),
    path('get_sensor_data/<str:sensor_name>/', views.get_sensor_data, name='get_sensor_data'),

    #API介面
    path('api/get_counts/', views.get_counts, name='get_counts'),
    path('api/get_sensor_names/', views.get_sensor_names, name='get_sensor_names'),
    path('api/get_sensor_data_by_id/<str:sensor_name>/<int:count>/', views.get_sensor_data_by_name, name='get_sensor_data_by_name'),
    path('api/get_product_ids/', views.get_product_ids, name='get_product_ids'),
    path('api/get_product_details/<str:product_id>/', views.get_product_details, name='get_product_details'),
    # Matches any html file
    re_path(r'^.*\.html$', views.pages, name='pages'),
]