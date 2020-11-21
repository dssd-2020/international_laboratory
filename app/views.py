import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .bonita import BonitaManager
from .models import Activity, Protocol, ActivityProtocol, Project, ProtocolProject


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
        # (Alejo): Comenté la linea de abajo porque me rompe la conexión con Bonita ya que no me anda Bonita :'(
        # (Alejo): Espero no haber roto nada :$
        # (Yani): La proxima vez que toques mi codigo no respondo de mi.
        # (Yani): Yo te toqué tu código porque me la banco
        bonita_manager = BonitaManager(request=request)
        user_logged = bonita_manager.get_user_logged(request)
        users_protocol_responsible = bonita_manager.get_users_protocol_responsible(request)
        ctx = {
            "project_manager": {
                "id": user_logged['user_id'],
                "name": user_logged['user_name']
            },
            "users": users_protocol_responsible,
            #     [
            #     {
            #         "id": "alejo",
            #         "name": "Alejo"
            #     },
            #     {
            #         "id": "marianela",
            #         "name": "Marianela"
            #     },
            #     {
            #         "id": "yanina",
            #         "name": "Yanina"
            #     },
            # ],
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
