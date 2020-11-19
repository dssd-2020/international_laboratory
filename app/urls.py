from django.urls import path

from app.views import ProtocolView, ActivityView, ProjectView

urlpatterns = [
    path("actividad", ActivityView.as_view(), name="actividad"),
    path("protocolo", ProtocolView.as_view(), name="protocolo"),
    path("proyecto", ProjectView.as_view(), name="proyecto"),
]
