import requests
import httplib2
import json
import urllib


class BonitaManager:
    cookie = ''
    process_id = ''
    case_id = ''
    bonita_token = ''

    def __init__(self, request=None):
        if request is None:
            request = {}
        else:
            self.process_id = self.get_process_id(request)
        # self.case_id = self.get_case(request)

    def login(self, request):
        http = httplib2.Http()
        url = 'http://localhost:8080/bonita/loginservice'
        data = {'username': 'alejo.marin',
                'password': 'bpm',
                'redirect': 'false',
                'redirectURL': ''
                }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response, content = http.request(url, 'POST', headers=headers, body=urllib.parse.urlencode(data))
        if response.status != 200:
            raise Exception("HTTP STATUS: " + str(response.status))
        return response['set-cookie']

    def bonita_token(self, request):
        result = self.login(request).split("X-Bonita-API-Token=")
        result = result[1].split(";")
        return result[0]

    def get_process_id(self, request):
        http = httplib2.Http()
        url = 'http://localhost:8080/bonita/API/bpm/process?s=Aprobacion de medicamentos'
        headers = {
            "Content-type": "application/json",
            # "Content-type": "application/x-www-form-urlencoded",
            "Cookie": self.login(request),
            "X-Bonita-API-Token": self.bonita_token(request),
            # "Cache-control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            # "Connection": "keep-alive"
        }
        response, content = http.request(url, 'GET', headers=headers)
        data = json.loads(content)
        try:
            return data[0]['id']
        except Exception as e:
            return str(e)

    def create_case(self, request):
        url = 'http://localhost:8080/bonita/API/bpm/process/' + self.process_id + '/instantiation'
        headers = {
            "X-Bonita-API-Token": request.COOKIES['X-Bonita-API-Token'],
        }
        response = requests.post(url, headers=headers, cookies=request.COOKIES)
        return response

    def get_case(self, request):
        url = 'http://localhost:8080/bonita/API/bpm/case?p=0&c=100&f=processDefinitionId=' + self.process_id
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)[0]['id']

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
        print(response)
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
