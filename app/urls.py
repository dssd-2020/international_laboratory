from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import HomeView, ProtocolView, ActivityView, ProjectView, LocalExecutionView, FailureResolutionView
from .views import get_protocols_by_project

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("actividad", ActivityView.as_view(), name="actividad"),
    path("protocolo", ProtocolView.as_view(), name="protocolo"),
    path("proyecto", ProjectView.as_view(), name="proyecto"),
    path("ejecucion_local", LocalExecutionView.as_view(), name="ejecucion_local"),
    path("resolucion_falla", FailureResolutionView.as_view(), name="resolucion_falla"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("get-protocols-by-project/", get_protocols_by_project, name="get_protocols_by_project"),
]
