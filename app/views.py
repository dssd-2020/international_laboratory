from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from .api import *
from .bonita import BonitaManager
from .models import Activity, Protocol, ActivityProtocol, Project, ProtocolProject


def session_complete(request):
    return "user_logged" in request.session and "bonita_cookies" in request.session


class HomeView(View):
    template_name = "home.html"

    def get(self, request, *args, **kwargs, ):
        if "logout" in request.GET:
            bonita_manager = BonitaManager(request=request)
            return JsonResponse({
                "error": bonita_manager.logout(request)
            })

        if session_complete(request):
            pass
        else:
            self.template_name = "login.html"

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        error = True
        if "username" in request.POST and "password" in request.POST:
            bonita_manager = BonitaManager(request=request)
            login = bonita_manager.login(request, request.POST.get("username"), request.POST.get("password"))
            if login:
                error = False
            pass
        return JsonResponse({
            "error": error
        })


class ActivityView(View):
    def get(self, request, *args, **kwargs):
        if session_complete(request):
            if "actividades" in request.path:
                activities = Activity.objects.all()
                if "s" in kwargs:
                    activities = activities.filter(pk=kwargs["s"])
                ctx = {
                    "activities": activities
                }
                return render(request, "activities_list.html", ctx)
            else:
                return render(request, "create_activity.html")
        return redirect("home")

    def post(self, request, *args, **kwargs):
        error = True
        if session_complete(request):
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
    def get(self, request, *args, **kwargs):
        if session_complete(request):
            ctx = {}
            if "protocolos" in request.path:
                protocols = Protocol.objects.all()
                if "s" in kwargs:
                    protocols = protocols.filter(pk=kwargs["s"])
                ctx["protocols"] = protocols
                return render(request, "protocols_list.html", ctx)
            else:
                ctx["activities"] = Activity.objects.all()
                return render(request, "create_protocol.html", ctx)

        return redirect("home")

    def post(self, request, *args, **kwargs):
        error = True
        if session_complete(request):
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
        if session_complete(request):
            bonita_manager = BonitaManager(request=request)
            user_logged = bonita_manager.get_user_logged(request)
            users_protocol_responsible = bonita_manager.get_users_protocol_responsible(request)
            ctx = {
                "project_manager": {
                    "id": user_logged["user_id"],
                    "name": user_logged["user_name"]
                },
                "users": users_protocol_responsible,
                "protocols": Protocol.objects.all(),
            }

            return render(request, self.template_name, ctx)
        return redirect("home")

    def post(self, request, *args, **kwargs):
        error = True
        if session_complete(request):
            if "name" in request.POST and "start_date" in request.POST and "end_date" in request.POST and "project_manager" in request.POST and "protocols_length" in request.POST:
                try:
                    bonita_manager = BonitaManager(request)
                    try:
                        case_id = bonita_manager.create_case(request)
                    except ():
                        return JsonResponse({
                            "error": error
                        })
                    project = Project.objects.create(
                        name=request.POST.get("name"),
                        start_date=request.POST.get("start_date"),
                        end_date=request.POST.get("end_date"),
                        project_manager=request.POST.get("project_manager"),
                        active=True,
                        case_id=case_id
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
                    try:
                        bonita_manager.set_active_project(request, project)
                        running_activity = bonita_manager.get_activities_by_case(request, case_id)
                        bonita_manager.update_task_assignment(request, running_activity)
                        logging.info('La tarea %s fue asignada al usuario con ID: %s', running_activity,
                                     bonita_manager.check_task_assignment(request, running_activity))
                        bonita_manager.update_task_state(request, running_activity, "completed", project)
                        logging.info('La tarea %s pasó al estado: %s', running_activity,
                                     bonita_manager.check_task_state(request, running_activity))
                    except Exception as e:
                        logging.error('ERROR: %s', str(e))
                    error = False
                except ():
                    pass
        return JsonResponse({
            "error": error
        })


class LocalExecutionView(View):
    template_name = "local_execution.html"

    def get(self, request, *args, **kwargs):
        if session_complete(request):
            protocol_project = ProtocolProject.objects.get(pk=request.GET.get("protocol_project"))
            protocol = Protocol.objects.get(pk=protocol_project.protocol.id)
            activities = protocol.activities.all()
            ctx = {
                "protocol_id": protocol.id,
                "activities": activities,
            }
            bonita_manager = BonitaManager(request=request)
            running_activity = bonita_manager.get_activities_by_case(request, protocol_project.project.case_id)
            try:
                check_assignment = bonita_manager.check_task_assignment(request, running_activity)
                if check_assignment == '':
                    bonita_manager.update_task_assignment(request, running_activity)
            except Exception as e:
                logging.error('ERROR: %s', str(e))
            return render(request, self.template_name, ctx)
        return redirect("home")

    def post(self, request, *args, **kwargs):
        error = True
        if session_complete(request):
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
                    protocol_project = ProtocolProject.objects.get(pk=request.GET.get("protocol_project"))
                    running_activity = bonita_manager.get_activities_by_case(request, protocol_project.project.case_id)
                    bonita_manager.update_task_state(request, running_activity, "completed")
                    bonita_manager.set_protocol_result(request, get_result_by_protocol(protocol, activities_checked))
                except ():
                    pass
        return JsonResponse({
            "error": error
        })


class FailureResolutionView(View):
    template_name = "failure_resolution.html"

    def get(self, request, *args, **kwargs):
        if session_complete(request):
            # (Alejo): El id es uno de un protocolo que tenía cargado en mi local y usé para probar, si se cargan algun protocolo usen ese id hasta que se vincule con Bonita
            protocol_id = 6
            ctx = {
                "protocol_id": protocol_id,
            }
            return render(request, self.template_name, ctx)
        return redirect("home")

    def post(self, request, *args, **kwargs):
        error = True
        if session_complete(request):
            if "protocol" in request.POST and "resolution" in request.POST:
                # (Alejo): Se simula un switch-case. Si el "resolution" recibido no coincide con ninguno, el default es "error"
                resolution = {
                    1: "continue",
                    2: "restart_protocol",
                    3: "restart_project",
                    4: "cancel_project"
                }.get(int(request.POST.get("resolution")), "error")

                bonita_manager = BonitaManager(request)
                bonita_manager.set_resolution_failure(request, request.POST.get("resolution"))

                # (Alejo): Acá quedará por hacer el procesamiento y la interacción con Bonita según lo que hayan seleccionado
                error = False
        return JsonResponse({
            "error": error
        })
