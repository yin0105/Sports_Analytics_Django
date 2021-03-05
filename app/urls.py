# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [
    path('', views.index, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('settings', views.settings, name='settings'),
    path('calculator', views.calculator, name='calculator'),
    path('kelly_calculator', views.kelly_calculator, name='kelly_calculator'),
    path('set_sports', views.set_sports, name='set_sports'),
    path('set_settings', views.set_settings, name='set_settings'),
]
