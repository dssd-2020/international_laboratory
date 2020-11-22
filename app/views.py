import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .bonita import BonitaManager
from .models import Activity, Protocol, ActivityProtocol, Project, ProtocolProject
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def get_protocols_by_project(request):
    """
    :param request: user, protocol, project
    :return: message, state
    """
    data = request.data
    protocols = ProtocolProject.objects.get(project=data['project'])
    print(type(protocols))
    try:
        protocols = list(ProtocolProject.objects.filter(project=data['project']).values())
        if len(protocols) > 0:
            print(protocols)
            protocols_list = [protocol.id for protocol in protocols]
            print(protocols_list)
            # return JsonResponse(
            #     {'data': {'protocols': protocols_list}, 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'data': {'protocols': []}, 'status': status.HTTP_200_OK})
    except ProtocolProject.DoesNotExist:
        return JsonResponse({'error': 'El proyecto no existe o no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})



class ActivityView(View):
    template_name = "create_activity.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        error = True
        if "name" in request.POST:
            try:
                Activity.objects.create(
                    name=request.POST.get("name")
                )
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class ProtocolView(View):
    template_name = "create_protocol.html"

    def get(self, request, *args, **kwargs):
        ctx = {
            "activities": Activity.objects.all()
        }
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        error = True
        if "name" in request.POST and "start_date" in request.POST and "end_date" in request.POST and "order" in request.POST and "local" in request.POST and "points" in request.POST and "activities_length" in request.POST:
            try:
                protocol = Protocol.objects.create(
                    name=request.POST.get("name"),
                    start_date=request.POST.get("start_date"),
                    end_date=request.POST.get("end_date"),
                    order=request.POST.get("order"),
                    is_local=request.POST.get("local"),
                    points=request.POST.get("points"),
                )
                for activity in request.POST.getlist("activities[]"):
                    ActivityProtocol.objects.create(
                        protocol=protocol,
                        activity=Activity.objects.get(pk=activity)
                    )
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class ProjectView(View):
    template_name = "create_project.html"

    def get(self, request, *args, **kwargs):
        bonita_manager = BonitaManager(request=request)
        running_activity = bonita_manager.get_activities_by_case(request)
        user_logged = bonita_manager.get_user_logged(request)
        users_protocol_responsible = bonita_manager.get_users_protocol_responsible(request)
        ctx = {
            "running_activity": running_activity,
            "project_manager": {
                "id": user_logged['user_id'],
                "name": user_logged['user_name']
            },
            "users": users_protocol_responsible,
            "protocols": Protocol.objects.all(),
        }

        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        error = True
        if "name" in request.POST and "start_date" in request.POST and "end_date" in request.POST and "project_manager" in request.POST and "active" in request.POST and "protocols_length" in request.POST:
            try:
                project = Project.objects.create(
                    name=request.POST.get("name"),
                    start_date=request.POST.get("start_date"),
                    end_date=request.POST.get("end_date"),
                    project_manager=request.POST.get("project_manager"),
                    active=request.POST.get("active"),
                )
                for index in range(0, int(request.POST.get("protocols_length"))):
                    protocol_responsible = request.POST.getlist("protocols[{}][]".format(index))
                    protocol = protocol_responsible[0]
                    responsible = protocol_responsible[1]
                    if not protocol == "-1" and not responsible == "-1":
                        ProtocolProject.objects.create(
                            protocol=Protocol.objects.get(pk=protocol),
                            project=project,
                            responsible=responsible
                        )
                    bonita_manager = BonitaManager(request)
                    bonita_manager.set_active_project(request, project)
                    running_activity = bonita_manager.get_activities_by_case(request)
                    bonita_manager.update_activity_state(request, running_activity, "completed", project)
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class LocalExecutionView(View):
    template_name = "local_execution.html"

    def get(self, request, *args, **kwargs):
        # (Alejo): El id es uno de un protocolo que tenía cargado en mi local y usé para probar, si se cargan algun protocolo usen ese id hasta que se vincule con Bonita
        protocol_id = 6
        protocol = Protocol.objects.get(pk=protocol_id)
        activities = protocol.activities.all()
        ctx = {
            "protocol_id": protocol_id,
            "activities": activities,
        }
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        error = True
        if "protocol" in request.POST:
            protocol = Protocol.objects.get(pk=request.POST.get("protocol"))
            activities = protocol.activities.all()
            try:
                for activity in activities:
                    if "activities[{}]".format(activity.id) in request.POST:
                        activity_protocol = ActivityProtocol.objects.get(
                            protocol=protocol,
                            activity=activity
                        )
                        activity_protocol.approved = request.POST.get("activities[{}]".format(activity.id))
                        activity_protocol.save()
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class FailureResolutionView(View):
    template_name = "failure_resolution.html"

    def get(self, request, *args, **kwargs):
        # (Alejo): El id es uno de un protocolo que tenía cargado en mi local y usé para probar, si se cargan algun protocolo usen ese id hasta que se vincule con Bonita
        protocol_id = 6
        ctx = {
            "protocol_id": protocol_id,
        }
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        error = True

        if "protocol" in request.POST and "resolution" in request.POST:
            # (Alejo): Se simula un switch-case. Si el "resolution" recibido no coincide con ninguno, el default es "error"
            resolution = {
                1: "continue",
                2: "restart_protocol",
                3: "restart_project",
                4: "cancel_project"
            }.get(int(request.POST.get("resolution")), "error")

            # (Alejo): Acá quedará por hacer el procesamiento y la interacción con Bonita según lo que hayan seleccionado
            error = False

        return JsonResponse({
            "error": error
        })
