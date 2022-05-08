from django.contrib import admin
from .models import (Location, CompletionStatus, NotificationGroup, DeliveryStatus, Load, LoadHistory)

admin.site.register(Location)

class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display=('name', 'is_active', 'is_default')

admin.site.register(DeliveryStatus, DeliveryStatusAdmin)

class LoadAdmin(admin.ModelAdmin):
    list_display=('po_number', 'job_name', 'delivery_status', 'completion_status')

admin.site.register(Load, LoadAdmin)

admin.site.register(LoadHistory)

class CompletionStatusAdmin(admin.ModelAdmin):
    list_display=('name', 'is_active', 'is_default')

admin.site.register(CompletionStatus, CompletionStatusAdmin)

class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_addresses', 'is_default')

admin.site.register(NotificationGroup, NotificationGroupAdmin)

