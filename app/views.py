import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .models import Activity, Protocol, ActivityProtocol, Project, ProtocolProject


def createCase():
    loginFromBonita()
    headers = {
        "X-Bonita-API-Token": requests.COOKIES["X-Bonita-API-Token"],
        "JSESSIONID": requests.COOKIES["JSESSIONID"],
        "csrftoken": requests.COOKIES["csrftoken"],
        "Content-Type": "application/json"
    }

    response = requests.post("http://localhost:8080/bonita/API/bpm/case?f=processDefinitionId=40004", headers=headers)
    # response = requests.get(
    #     "http://localhost:8080/bonita/API/bpm/process?f=name=AprobacionDeMedicamentos&p=0&c=10")
    # , headers=headers)
    print("case", response)
    return response


def getProcessId(request):
    request = loginFromBonita(request)
    url = "http://localhost:8080/bonita/API/bpm/process?c=100&p=0"
    # url = "http://localhost:8080/cookies"
    headers = {
        "X-Bonita-API-Token": request.COOKIES["X-Bonita-API-Token"],
        # "Content-Type": "application/json",
        "Cookie": request.COOKIES["JSESSIONID"],
        # "cache-control": "no-cache",
    }
    # response = requests.post(url, headers=headers)
    response = requests.get(url, cookies=request.COOKIES)
    print(response)
    return response


def getUsersFromBonita():
    headers = {"X-Bonita-API-Token": loginFromBonita()}
    response = requests.get(
        "http://localhost:8080/bonita/API/identity/group/Grupo1")
    # print(request.session["taskId"])
    return response


def loginFromBonita(request):
    url = "http://localhost:8080/bonita/loginservice"
    data = {"username": "walter.bates",
            "password": "bpm",
            "redirect": "false",
            "redirectURL": ""}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        request.session["X-Bonita-API-Token"] = request.COOKIES["X-Bonita-API-Token"]
        request.session["JSESSIONID"] = request.COOKIES["JSESSIONID"]
        # requests.session["csrftoken"] = request.COOKIES["csrftoken"]

    return request


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
        # users = getProcessId(request)

        ctx = {
            "project_manager": {
                "id": "userlogged",
                "name": "Usuario logueado"
            },
            "users": [
                {
                    "id": "alejo",
                    "name": "Alejo"
                },
                {
                    "id": "marianela",
                    "name": "Marianela"
                },
                {
                    "id": "yanina",
                    "name": "Yanina"
                },
            ],
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
