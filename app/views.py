from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
import requests
import json

from .forms import ActivityForm, ProtocolForm, ProjectForm


def getProcessId(request):
    headers = {
            "Cookie": loginFromBonita(request),
            "Content-Type": "application/json"
            }
    response = requests.get('http://localhost:8080/bonita/API/identity/user?p=0&c=10&o=lastname%20ASC&f=enabled%3dtrue', headers=headers)
    # response = requests.get(
    #     'http://localhost:8080/bonita/API/bpm/process?f=name=AprobacionDeMedicamentos&p=0&c=10')
        # , headers=headers)
    print(response)
    return response


def getUsersFromBonita(request):
    headers = {'X-Bonita-API-Token': loginFromBonita(request)}
    response = requests.get(
        'http://localhost:8080/bonita/API/identity/user?p=0&c10')
        # 'http://localhost:8080/bonita/API/identity/group/Grupo1')
    # print(request.session['taskId'])
    return response


def loginFromBonita(request):
    url = 'http://localhost:8080/bonita/loginservice'
    data = {'username': 'walter.bates',
            'password': 'bpm',
            'redirect': 'false'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    requests.post(url, data=data, headers=headers)

    return request.COOKIES['JSESSIONID']


class ActivityView(View):
    form_class = ActivityForm
    initial = {'key': '1'}
    template_name = 'create_activity.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            activity = form.save()
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class ProtocolView(View):
    form_class = ProtocolForm
    initial = {'key': '1'}
    template_name = 'create_protocol.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            protocol = form.save()
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class ProjectView(View):
    form_class = ProjectForm
    initial = {'key': '1'}
    template_name = 'create_project.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        users = getProcessId(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            activity = form.save()
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
