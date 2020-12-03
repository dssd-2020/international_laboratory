import logging
import requests
import json

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
