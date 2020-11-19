from django.urls import path
from django.views.generic import TemplateView

from app.views import ProtocolView, ActivityView, ProjectView, LocalExecutionView, FailureResolutionView

urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html"), name="index"),
    path("actividad", ActivityView.as_view(), name="actividad"),
    path("protocolo", ProtocolView.as_view(), name="protocolo"),
    path("proyecto", ProjectView.as_view(), name="proyecto"),
    path("ejecucion_local", LocalExecutionView.as_view(), name="ejecucion_local"),
    path("resolucion_falla", FailureResolutionView.as_view(), name="resolucion_falla"),
]
