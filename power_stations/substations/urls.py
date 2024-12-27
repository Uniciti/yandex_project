# substations/urls.py

from django.urls import path
from . import views

app_name = 'substations'

urlpatterns = [
    path('', views.substation_list, name='substation_list'),
    path('create/', views.substation_create, name='substation_create'),
    path('<int:substation_id>/', views.substation_detail, name='substation_detail'),
    path('<int:substation_id>/edit/', views.substation_edit, name='substation_edit'),
    path('<int:substation_id>/delete/', views.substation_delete, name='substation_delete'),  # новый URL
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('type/<int:type_id>/', views.substation_type_detail, name='substation_type_detail'),
    path('maintenance/record/<int:record_id>/', views.maintenance_record_detail, name='maintenance_record_detail'),
    path('maintenance/status/<int:status_id>/', views.maintenance_status_detail, name='maintenance_status_detail'),
    path('type/<int:type_id>/delete/', views.substation_type_delete, name='substation_type_delete'),
    path('group/<int:group_id>/delete/', views.substation_group_delete, name='substation_group_delete'),
    path('maintenance/record/<int:record_id>/delete/', views.maintenance_record_delete, name='maintenance_record_delete'),
]