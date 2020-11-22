import requests
import json


class BonitaManager:
    process_id = ''
    case_id = ''
    uri = 'http://localhost:8080/bonita'

    def __init__(self, request=None):
        if request is None:
            request = {}
        else:
            self.process_id = self.get_process_id(request)
            self.case_id = self.get_case(request)

    def login(self, request):
        url = ''.join([self.uri, '/loginservice'])
        data = {'username': 'alejo.marin',
                'password': 'bpm',
                'redirect': 'false',
                'redirectURL': ''}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, json=data, headers=headers)
        return response

    def create_case(self, request):
        url = ''.join([self.uri, '/API/bpm/process/', self.get_process_id(request), '/instantiation'])
        headers = {
            "X-Bonita-API-Token": request.COOKIES['X-Bonita-API-Token'],
            "JSESSIONID": request.COOKIES['JSESSIONID'],
            "csrftoken": request.COOKIES['csrftoken'],
            "Content-Type": "application/json",
            "cache-control": "no-cache"
        }
        response = requests.post(url, headers=headers, cookies=request.COOKIES)
        self.case_id = json.loads(response.content)[0]['id']
        return self.case_id

    def get_case(self, request):
        url = 'http://localhost:8080/bonita/API/bpm/case?p=0&c=100&f=processDefinitionId=' + self.process_id
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)[0]['id']

    def get_process_id(self, request):
        url = 'http://localhost:8080/bonita/API/bpm/process?c=100&p=0&f=name=Aprobacion de medicamentos'
        response = requests.get(url, cookies=request.COOKIES)
        response = json.loads(response.content)
        self.process_id = response[0]['id']
        return self.process_id

    def get_users_protocol_responsible(self, request):
        group_id = BonitaManager().get_group_by_name(request, "Responsable de protocolo")
        url = 'http://localhost:8080/bonita/API/identity/user?p=0&c=100&o=firstname%20ASC&f=enabled%3dtrue&f=group_id=' + group_id
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)

    def get_role_by_name(self, request, name):
        url = 'http://localhost:8080/bonita/API/identity/role?p=0&c=100&f=name=' + name
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)[0]['id']

    def get_user_logged(self, request):
        url = 'http://localhost:8080/bonita/API/system/session/unusedid'
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)

    def get_human_task_by_name(self, request, name):
        name = "Configuración del proyecto"
        url = 'http://localhost:8080/bonita/API/bpm/humanTask?p=0&c=100&f=name=' + name
        response = requests.get(url, cookies=request.COOKIES)
        print(json.loads(response.content))
        return json.loads(response.content)

    def get_group_by_name(self, request, name):
        url = 'http://localhost:8080/bonita/API/identity/group?p=0&c=100&f=displayName=' + name
        response = requests.get(url, cookies=request.COOKIES)

        return json.loads(response.content)[0]['id']

    def get_activities_by_case(self, request):
        url = ''.join([self.uri, '/API/bpm/activity?f=processId=', self.process_id, '&f=parentCaseId=', self.case_id])
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)[0]['id']

    def update_activity_assignment(self, request, activity):
        url = ''.join([self.uri, '/API/bpm/humanTask/', activity])
        headers = {
            "X-Bonita-API-Token": request.COOKIES['X-Bonita-API-Token'],
            "Content-type": "application/json"
        }
        user = self.get_user_logged(request)
        data = {
            "assigned_id": user['user_id']
        }

        response = requests.put(url, json=data, headers=headers, cookies=request.COOKIES)
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))

    def update_activity_state(self, request, activity, state, project):
        url = ''.join([self.uri, '/API/bpm/activity/', activity])
        headers = {
            "X-Bonita-API-Token": request.COOKIES['X-Bonita-API-Token'],
            "Content-type": "application/json"
        }
        data = {
            "state": state,
            # "dueDate": project.end_date
        }

        response = requests.put(url, data=json.dumps(data), headers=headers, cookies=request.COOKIES)
        print(response)
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.content))

    def set_active_project(self, request, project):
        # url = ''.join([self.uri, '/API/bpm/caseVariable?p=0&c=100&f=case_id%3d', self.get_case(request)])
        # response = requests.get(url, cookies=request.COOKIES)

        url = ''.join([self.uri, '/API/bpm/caseVariable/', self.get_case(request), "/active_project"])
        headers = {
            "X-Bonita-API-Token": request.COOKIES['X-Bonita-API-Token'],
            "Content-type": "application/json"
        }
        data = {
            'type': "java.lang.String",
            'value':  project.id
        }

        response = requests.put(url, json=data, headers=headers, cookies=request.COOKIES)
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
