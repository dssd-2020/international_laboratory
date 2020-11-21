import requests
import json


class BonitaManager:
    process_id = ''
    case_id = ''

    def __init__(self, request=None):
        if request is None:
            request = {}
        else:
            self.process_id = self.get_process_id(request)
            self.case_id = self.get_case(request)

    def login(self, request):
        url = 'http://localhost:8080/bonita/loginservice'
        data = {'username': 'alejo.marin',
                'password': 'bpm',
                'redirect': 'false',
                'redirectURL': ''}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers)
        return response

    def create_case(self, request):
        # url = 'http://localhost:8080/bonita/API/bpm/case?p=0&c=100&f=processDefinitionId=' + self.get_process_id(request)
        url = 'http://localhost:8080/bonita/API/bpm/case'
        headers = {
            "X-Bonita-API-Token": request.COOKIES['X-Bonita-API-Token'],
            "JSESSIONID": request.COOKIES['JSESSIONID'],
            "csrftoken": request.COOKIES['csrftoken'],
            "Content-Type": "application/json",
            "cache-control": "no-cache"
        }
        data = {
            "processDefinitionId": self.get_process_id(request)
        }
        response = requests.post(url, headers=headers, cookies=request.COOKIES)
        print('case', response.content)
        return response

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
