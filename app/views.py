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
    print(data)
    try:
        protocols = ProtocolProject.objects.filter(project=data['project'], project__active=True)
        if len(protocols) > 0:
            protocols_list = [protocol.id for protocol in protocols]
            return JsonResponse(
                {'data': {'protocols': protocols_list}, 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'error': 'El proyecto no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except ProtocolProject.DoesNotExist:
        return JsonResponse({'error': 'El proyecto no existe o no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


def get_result_by_protocol(protocol, activities_checked):
    # activities_checked = 0
    total = protocol.activities.count()
    # for activity in protocol.activityprotocol_set.all():
    #     print(activity.approved)
    #     activities_checked += 1 if activity.approved else 0

    points = activities_checked * 100 / total
    return protocol.points <= points


class HomeView(View):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if "logout" in request.GET:
            bonita_manager = BonitaManager(request=request)
            return JsonResponse({
                "error": bonita_manager.logout(request)
            })

        try:
            if request.session["user_logged"]:
                pass
            else:
                self.template_name = "login.html"
        except KeyError:
            self.template_name = "login.html"

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        error = True
        if "username" in request.POST and "password" in request.POST:
            bonita_manager = BonitaManager(request=request)
            login = bonita_manager.login(request, request.POST.get("username"), request.POST.get("password"))
            if login:
                # print(request.session["bonita_cookies"])
                # print("userlogged", bonita_manager.get_user_logged(request))
                error = False
            pass
        return JsonResponse({
            "error": error
        })


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
        # bonita_manager.login(request)
        # print("userlogged", bonita_manager.get_user_logged(request))
        # bonita_manager.create_case(request)
        # return pepe
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
                    if bonita_manager.check_activity_assignment(request, running_activity) == '':
                        bonita_manager.update_activity_assignment(request, running_activity)
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
        protocol_id = 4
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
                activities_checked = 0
                for activity in activities:
                    if "activities[{}]".format(activity.id) in request.POST:
                        activity_protocol = ActivityProtocol.objects.get(
                            protocol=protocol,
                            activity=activity
                        )
                        activities_checked += 1
                        activity_protocol.approved = request.POST.get("activities[{}]".format(activity.id))
                        activity_protocol.save()
                error = False
                bonita_manager = BonitaManager(request)
                running_activity = bonita_manager.get_activities_by_case(request)
                if bonita_manager.check_activity_assignment(request, running_activity) == '':
                    bonita_manager.update_activity_assignment(request, running_activity)
                bonita_manager.update_activity_state(request, running_activity, "completed")
                bonita_manager.set_protocol_result(request, get_result_by_protocol(protocol, activities_checked))
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
