from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
import requests
import json

from .forms import ActivityForm, ProtocolForm, ProjectForm


def createCase():
    loginFromBonita()
    headers = {
            'X-Bonita-API-Token': requests.COOKIES['X-Bonita-API-Token'],
            'JSESSIONID': requests.COOKIES['JSESSIONID'],
            'csrftoken': requests.COOKIES['csrftoken'],
            'Content-Type': 'application/json'
            }

    response = requests.post('http://localhost:8080/bonita/API/bpm/case?f=processDefinitionId=40004', headers=headers)
    # response = requests.get(
    #     'http://localhost:8080/bonita/API/bpm/process?f=name=AprobacionDeMedicamentos&p=0&c=10')
        # , headers=headers)
    print('case', response)
    return response


def getProcessId(request):
    request = loginFromBonita(request)
    url = 'http://localhost:8080/bonita/API/bpm/process?c=100&p=0'
    # url = 'http://localhost:8080/cookies'
    headers = {
            'X-Bonita-API-Token': request.COOKIES['X-Bonita-API-Token'],
            # 'Content-Type': 'application/json',
            'Cookie': request.COOKIES['JSESSIONID'],
            # 'cache-control': 'no-cache',
            }
    # response = requests.post(url, headers=headers)
    response = requests.get(url, cookies=request.COOKIES)
    print(response)
    return response


def getUsersFromBonita():
    headers = {'X-Bonita-API-Token': loginFromBonita()}
    response = requests.get(
        'http://localhost:8080/bonita/API/identity/group/Grupo1')
    # print(request.session['taskId'])
    return response


def loginFromBonita(request):
    url = 'http://localhost:8080/bonita/loginservice'
    data = {'username': 'walter.bates',
            'password': 'bpm',
            'redirect': 'false',
            'redirectURL': ''}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        request.session['X-Bonita-API-Token'] = request.COOKIES['X-Bonita-API-Token']
        request.session['JSESSIONID'] = request.COOKIES['JSESSIONID']
        # requests.session['csrftoken'] = request.COOKIES['csrftoken']

    return request

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
