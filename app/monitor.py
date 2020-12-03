import logging
import requests
import json
import pytz
from datetime import timedelta, datetime

from .bonita import BonitaManager
from .models import Project

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


def get_cases_cancelled(bonita_manager, request):
    cancelled_projects = []
    projects = Project.objects.filter(active=False)
    for project in projects:
        if case_cancelled(bonita_manager, request, project.case_id):
            cancelled_projects.append(project)
    return cancelled_projects


def case_cancelled(bonita_manager, request, case_id):
    url = "".join([bonita_manager.uri, "/API/bpm/archivedComment?&f=processInstanceId=", case_id])
    response = requests.get(url, cookies=request.session["bonita_cookies"])
    if response.status_code != 200:
        raise Exception("HTTP STATUS: " + str(response))

    if response.content:
        if "'content': 'cancelled'" in str(json.loads(response.content)):
            return True
    return False


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
