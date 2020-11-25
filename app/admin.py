from django.contrib import admin

from .models import *

admin.site.register(Activity)
admin.site.register(Protocol)
admin.site.register(ActivityProtocol)
admin.site.register(Project)
admin.site.register(ProtocolProject)
admin.site.register(Notification)
