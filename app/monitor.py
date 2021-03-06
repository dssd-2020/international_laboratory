import json
import logging
from datetime import timedelta, datetime

import requests

from .models import Project

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


def get_cases_cancelled(bonita_manager, request):
    cancelled_projects = []
    projects = Project.objects.filter(active=False)
    for project in projects:
        if bonita_manager.case_cancelled(request, project.case_id):
            cancelled_projects.append(project)
    return cancelled_projects


def get_cases_average_time(bonita_manager, request):
    projects = []
    query = Project.objects.filter(active=False)
    for project in query:
        response = bonita_manager.get_archived_case(request, project.case_id)
        if response:
            try:
                end_date = response[0]['end_date'].split('.')
                start_date = response[0]['start'].split('.')
                projects.append({'project': project,
                                 'end_date': datetime.strptime(end_date[0], "%Y-%m-%d %H:%M:%S"),
                                 'start_date': datetime.strptime(start_date[0], "%Y-%m-%d %H:%M:%S")})
            except:
                continue

    average = timedelta(0)
    if len(projects) > 0:
        dates = [(project['end_date'] - project['start_date']) for project in projects]
        for date in dates:
            average += date
        average = average / len(projects)
    return [projects, average]


def get_on_failure(bonita_manager, request):
    managers = {}
    query = Project.objects.filter(active=True)
    for project in query:
        try:
            result = bonita_manager.get_task_running(request, project.case_id)
            if result and "No hay información sobre este caso" not in result:
                try:
                    if result['name'] == "Resolución ante falla":
                        if project.project_manager not in managers.keys():
                            managers[project.project_manager] = {'count': 0}
                        managers[project.project_manager]['count'] += 1
                except:
                    continue
        except:
            continue
    for manager in managers.keys():
        try:
            firstname, lastname = bonita_manager.get_user_names(request, manager)
        except:
            firstname = "Usuario"
            lastname = "desconocido"
        managers[manager]['firstname'] = firstname
        managers[manager]['lastname'] = lastname
    return managers
