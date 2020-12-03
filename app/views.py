from django.shortcuts import render, redirect
from django.views import View

from .api import *
from .bonita import BonitaManager
from .decorators import login_required
from .models import *
from .monitor import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


class HomeView(View):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if "login" in request.path:
            return self.login(request, *args, **kwargs)

        if "logout" in request.path:
            self.logout(request, *args, **kwargs)

        return self.home(request, *args, **kwargs)

    @login_required
    def home(self, request, *args, **kwargs):
        ctx = {}
        user_logged_id = request.session["user_logged"]["user_id"]
        if "Jefe de proyecto" in request.session["user_membership"]:
            # rpta = bonita_manager.get_task_running(request, project.case_id)
            # devuelve un json con name y state
            managed_projects = Project.objects.filter(project_manager=user_logged_id)
            ctx["managed_projects_in_execution"] = managed_projects.filter(approved__isnull=True)
            ctx["managed_projects"] = managed_projects.filter(approved__isnull=False)
        if "Responsable de protocolo" in request.session["user_membership"]:
            protocols_project = ProtocolProject.objects.filter(responsible=user_logged_id)
            
            for protocol_project in protocols_project:
                state = self.state_protocol_project(request, protocol_project=protocol_project)
                print("state...")
                print(state)
            ctx["responsible_protocols"] = protocols_project
        return render(request, "home.html", ctx)

    @login_required
    def login(self, request, *args, **kwargs):
        return render(request, "login.html")

    @login_required
    def logout(self, request, *args, **kwargs):
        bonita_manager = BonitaManager(request=request)
        return JsonResponse({
            "error": bonita_manager.logout(request)
        })

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

    def protocol_project_run(self, request, case_id):
        bonita_manager = BonitaManager(request=request)
        protocol_project = bonita_manager.get_case_variable(request, case_id, "protocol_project")
        return protocol_project

    def state_protocol_project(self, request, protocol_project):
        if protocol_project.result and protocol_project.approved:
            result = {"state": "Protocolo aprobado"}
            return result
        elif protocol_project.result and not protocol_project.approved:
            result = {"state": "En resolución ante falla"}
            return result
        elif protocol_project.project.active:
            protocol_project_run = self.protocol_project_run(request, protocol_project.project.case_id)
            if protocol_project_run:
                if int(protocol_project_run) == int(protocol_project.id):
                    # bonita_manager.get_task_running(request, project.case_id)
                    result = {"state": "Protocolo listo para ejecutarse"}
                    return result
            elif not protocol_project.running_task:
                result = {"state": "El protocolo se encuentra en preparación"}
                return result


class ActivityView(View):
    @login_required
    def get(self, request, *args, **kwargs):
        if "actividades" in request.path:
            activities = Activity.objects.all()
            if "s" in kwargs:
                activities = activities.filter(pk=kwargs["s"])
            ctx = {
                "activities": activities
            }
            return render(request, "activities_list.html", ctx)
        else:
            if "Jefe de proyecto" in request.session["user_membership"]:
                return render(request, "create_activity.html")
            else:
                return redirect("actividades")

    @login_required
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
    @login_required
    def get(self, request, *args, **kwargs):
        ctx = {}
        if "protocolos" in request.path:
            protocols = Protocol.objects.all()
            if "s" in kwargs:
                protocols = protocols.filter(pk=kwargs["s"])
            ctx["protocols"] = protocols
            return render(request, "protocols_list.html", ctx)
        else:
            if "Jefe de proyecto" in request.session["user_membership"]:
                ctx["activities"] = Activity.objects.all()
                return render(request, "create_protocol.html", ctx)
            else:
                return redirect("protocolos")

    @login_required
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

    @login_required
    def get(self, request, *args, **kwargs):
        bonita_manager = BonitaManager(request=request)

        if "s" in kwargs:
            if "Jefe de proyecto" in bonita_manager.get_membership_by_user(request):
                try:
                    ctx = {
                        "project": Project.objects.get(pk=kwargs["s"])
                    }
                    return render(request, "project_detail.html", ctx)
                except Project.DoesNotExist:
                    pass
            return redirect("home")

        user_logged = bonita_manager.get_user_logged(request)
        users_protocol_responsible = bonita_manager.get_users_by_role(request, "Responsable de protocolo")
        ctx = {
            "project_manager": {
                "id": user_logged["user_id"],
                "name": user_logged["user_name"]
            },
            "users": users_protocol_responsible,
            "protocols": Protocol.objects.all(),
        }
        return render(request, self.template_name, ctx)

    @login_required
    def post(self, request, *args, **kwargs):
        error = True
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
                    logging.info("La tarea %s fue asignada al usuario con ID: %s", running_activity,
                                 bonita_manager.check_task_assignment(request, running_activity))
                    bonita_manager.update_task_state(request, running_activity, "completed")
                    logging.info("La tarea %s pasó al estado: %s", running_activity,
                                 bonita_manager.check_task_state(request, running_activity))
                except Exception as e:
                    logging.error("ERROR: %s", str(e))
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class LocalExecutionView(View):
    template_name = "local_execution.html"

    @login_required
    def get(self, request, *args, **kwargs):
        protocol_project = ProtocolProject.objects.get(pk=kwargs["protocol_project"])
        protocol = protocol_project.protocol
        activities = protocol.activities.all()
        ctx = {
            "activities": activities,
        }
        bonita_manager = BonitaManager(request=request)
        running_activity = bonita_manager.get_activities_by_case(request, protocol_project.project.case_id)
        try:
            check_assignment = bonita_manager.check_task_assignment(request, running_activity)
            if check_assignment == "":
                bonita_manager.update_task_assignment(request, running_activity)
        except Exception as e:
            logging.error("ERROR: %s", str(e))
        return render(request, self.template_name, ctx)

    @login_required
    def post(self, request, *args, **kwargs):
        error = True
        if "protocol_project" in kwargs:
            protocol_project = ProtocolProject.objects.get(pk=kwargs["protocol_project"])
            protocol = protocol_project.protocol
            activities = protocol.activities.all()
            try:
                activities_checked = 0
                for activity in activities:
                    if "activities[{}]".format(activity.id) in request.POST:
                        activity_protocol = ActivityProtocol.objects.get(
                            protocol=protocol,
                            activity=activity
                        )
                        activity_protocol.approved = True
                        activity_protocol.save()
                        activities_checked += 1
                bonita_manager = BonitaManager(request)
                running_activity = bonita_manager.get_activities_by_case(request, protocol_project.project.case_id)
                get_result_by_protocol(protocol_project, activities_checked)
                bonita_manager.set_protocol_result(request, protocol_project.project.case_id, protocol_project.approved)
                bonita_manager.update_task_state(request, running_activity, "completed")
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class FailureResolutionView(View):
    template_name = "failure_resolution.html"

    @login_required
    def get(self, request, *args, **kwargs):
        protocol_project_id = kwargs["protocol_project"]
        protocol_project = ProtocolProject.objects.get(pk=protocol_project_id)
        ctx = {
            "protocol_project_id": protocol_project_id,
        }
        bonita_manager = BonitaManager(request=request)
        running_activity = bonita_manager.get_activities_by_case(request, protocol_project.project.case_id)
        bonita_manager.update_task_assignment(request, running_activity)

        return render(request, self.template_name, ctx)

    @login_required
    def post(self, request, *args, **kwargs):
        error = True
        if "protocol_project" in kwargs and "resolution" in request.POST:
            protocol_project_id = kwargs["protocol_project"]
            protocol_project = ProtocolProject.objects.get(pk=protocol_project_id)
            resolution_case = int(request.POST.get("resolution"))
            resolution = {
                1: "continue",
                2: "restart_protocol",
                3: "restart_project",
                4: "cancel_project"
            }.get(resolution_case, False)
            if resolution:
                bonita_manager = BonitaManager(request)
                if resolution == "continue":
                    protocol_project.approved = False
                elif resolution == "restart_protocol":
                    protocol_project.approved = None
                    protocol_project.result = None
                elif resolution == "cancel_project":
                    protocol_project.project.active = False
                    protocol_project.project.approved = False
                    bonita_manager.add_comment_case(request, protocol_project.project.case_id)
                    protocol_project.project.save()
                protocol_project.save()
                try:
                    running_activity = bonita_manager.get_activities_by_case(request,
                                                                             protocol_project.project.case_id)
                    bonita_manager.set_resolution_failure(request, protocol_project.project.case_id, resolution_case)
                    bonita_manager.update_task_state(request, running_activity, "completed")
                    error = False
                except ():
                    pass
        return JsonResponse({
            "error": error
        })


class NotificationsView(View):
    template_name = "notifications.html"

    @login_required
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user_id=request.session["user_logged"]["user_id"])
        not_view_notifications = notifications.filter(view=False)
        view_notifications = notifications.filter(view=True)
        if "get_notifications_count" in request.GET:
            return JsonResponse({
                "notifications_count": not_view_notifications.count()
            })
        ctx = {
            "not_view_notifications": not_view_notifications,
            "view_notifications": view_notifications,
        }
        return render(request, self.template_name, ctx)

    @login_required
    def post(self, request, *args, **kwargs):
        error = True
        if "notification_id" in request.POST:
            try:
                notification = Notification.objects.get(pk=request.POST.get("notification_id"))
                notification.view = True
                notification.save()
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })


class InquiriesView(View):
    template_name = "inquiries.html"

    @login_required
    def get(self, request, *args, **kwargs):
        bonita_manager = BonitaManager(request=request)
        if "Jefe de proyecto" not in bonita_manager.get_membership_by_user(request):
            return redirect("home")
        ctx = {}
        # Inquirie_1 Jefes de proyecto con mayor cantidad de proyectos en espera de toma de decisión ante falla
        ctx["inquirie_1"] = [
            {
                "user_name": "walter.bates",
                "count": 5
            },
            {
                "user_name": "alejo.marin",
                "count": 2
            },
        ]
        # Inquirie_2 Tiempo promedio de ejecución completa del caso en el proceso de negocio
        ctx["inquirie_2"] = 12.45
            # Se puede contemplar tambien mandar cada proyecto con su tiempo de ejecución para listar (pero no sé)
        # Inquirie_3 Cantidad de casos cancelados ante el fallo de un protocolo
        cancelled_projects = get_cases_cancelled(bonita_manager, request)
        ctx["inquirie_3"] = len(cancelled_projects)
        print(cancelled_projects)
            # Se puede contemplar tambien mandar cada proyecto cancelado para listar (pero no sé)

        return render(request, self.template_name, ctx)

    @login_required
    def post(self, request, *args, **kwargs):
        error = True
        if "notification_id" in request.POST:
            try:
                notification = Notification.objects.get(pk=request.POST.get("notification_id"))
                notification.view = True
                notification.save()
                error = False
            except ():
                pass
        return JsonResponse({
            "error": error
        })
