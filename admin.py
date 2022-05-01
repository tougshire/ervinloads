from django.contrib import admin
from .models import (Location, Completion, NotificationGroup, Status, Load, LoadHistory)

admin.site.register(Location)

admin.site.register(Status)

class LoadAdmin(admin.ModelAdmin):
    list_display=('po_number', 'job_name', 'status', 'completion')

admin.site.register(Load, LoadAdmin)

admin.site.register(LoadHistory)

class CompletionAdmin(admin.ModelAdmin):
    list_display=('name', 'is_active')

admin.site.register(Completion, CompletionAdmin)

class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_addresses', 'is_default')

admin.site.register(NotificationGroup, NotificationGroupAdmin)
