from django.contrib import admin
from .models import *

admin.site.register(Activity)
admin.site.register(Notification)


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'order', 'is_local', 'points')


@admin.register(ActivityProtocol)
class ActivityProtocolAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'activity', 'approved')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'project_manager', 'active', 'case_id', 'approved')


@admin.register(ProtocolProject)
class ProtocolProjectAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'project', 'result', 'approved', 'responsible', 'running_task')
