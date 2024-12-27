# substations/admin.py
from django.contrib import admin
from .models import (
    Substation,
    SubstationGroup,
    SubstationType,
    MaintenanceStatus,
    MaintenanceRecord
)

@admin.register(SubstationType)
class SubstationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(MaintenanceStatus)
class MaintenanceStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(SubstationGroup)
class SubstationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'responsible_person', 'created_at', 'updated_at')
    search_fields = ('name', 'responsible_person')
    list_filter = ('created_at',)

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'substation',
        'status',
        'scheduled_date',
        'completed_date',
        'is_active'
    )
    list_filter = ('status', 'is_active', 'scheduled_date')
    search_fields = ('substation__name', 'description')
    date_hierarchy = 'scheduled_date'

@admin.register(Substation)
class SubstationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'substation_type',
        'power',
        'voltage',
        'city',
        'group',
        'is_active'
    )
    list_filter = (
        'is_active',
        'substation_type',
        'city',
        'group',
    )
    search_fields = ('name', 'address')
    filter_horizontal = ('connected_substations',)
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'substation_type',
                'power',
                'voltage',
                'is_active'
            )
        }),
        ('Расположение', {
            'fields': ('city', 'address')
        }),
        ('Группировка и связи', {
            'fields': ('group', 'connected_substations')
        }),
        ('Обслуживание', {
            'fields': (
                'last_maintenance',
                'next_maintenance',
                'notes'
            )
        }),
    )