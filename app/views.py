from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from .bonita import BonitaManager
from .forms import ActivityForm, ProtocolForm, ProjectForm


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
    bonita = BonitaManager()

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        users = self.bonita.get_process_id(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            activity = form.save()
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
