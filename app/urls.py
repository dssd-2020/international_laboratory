from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .api import get_protocols_by_project
from .views import *

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("actividad/", ActivityView.as_view(), name="actividad"),
    path("actividades/", ActivityView.as_view(), name="actividades"),
    path("actividades/<int:s>/", ActivityView.as_view(), name="actividades_buscar"),
    path("protocolo/", ProtocolView.as_view(), name="protocolo"),
    path("protocolos/", ProtocolView.as_view(), name="protocolos"),
    path("protocolos/<int:s>/", ProtocolView.as_view(), name="protocolos_buscar"),
    path("proyecto/", ProjectView.as_view(), name="proyecto"),
    path("ejecucion_local/", LocalExecutionView.as_view(), name="ejecucion_local"),
    path("resolucion_falla/", FailureResolutionView.as_view(), name="resolucion_falla"),
    path("notificaciones/", NotificationsView.as_view(), name="notificaciones"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path("get-protocols-by-project/", get_protocols_by_project, name="get_protocols_by_project"),
    path("get-protocol/", get_protocol_to_run, name="get_protocol_to_run"),
]
