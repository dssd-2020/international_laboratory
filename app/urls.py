from django.urls import path
from app.views import ProtocolView, ActivityView, ProjectView

urlpatterns = [
    path('protocolo', ProtocolView.as_view()),
    path('actividad', ActivityView.as_view()),
    path('proyecto', ProjectView.as_view()),
]