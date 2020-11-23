import json

import requests


class BonitaManager:
    process_id = None
    case_id = None
    cookies = None
    uri = "http://localhost:8080/bonita"

    def __init__(self, request=None):
        if request is None:
            request = {}
        elif "user_logged" in request.session:
            self.process_id = self.get_process_id(request)
            self.case_id = self.get_case(request)

    def login(self, request, username, password):
        url = "".join([self.uri, "/loginservice"])
        data = {
            "username": username,
            "password": password,
            "redirect": "false"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=data, headers=headers)
        if len(response.cookies):
            request.session["bonita_cookies"] = {
                "BOS_Locale": response.cookies["BOS_Locale"],
                "JSESSIONID": response.cookies["JSESSIONID"],
                "X-Bonita-API-Token": response.cookies["X-Bonita-API-Token"],
                "bonita.tenant": response.cookies["bonita.tenant"],
            }
            request.session["user_logged"] = self.get_user_logged(request)
        else:
            return False
        return response

    def logout(self, request):
        if "user_logged" in request.session:
            url = "".join([self.uri, "/logoutservice"])
            data = {"redirect": "false"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            requests.get(url, data=data, headers=headers)
            del request.session["user_logged"]
            del request.session["bonita_cookies"]
            return True
        return False

    def create_case(self, request):
        url = "".join([self.uri, "/API/bpm/process/", self.get_process_id(request), "/instantiation"])
        headers = {
            "X-Bonita-API-Token": request.session["bonita_cookies"]["X-Bonita-API-Token"],
            "Content-Type": "application/json",
            "cache-control": "no-cache"
        }
        response = requests.post(url, headers=headers, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        print(response)
        self.case_id = json.loads(response.content)[0]["id"]
        return self.case_id

    def get_case(self, request):
        url = "".join([self.uri, "/API/bpm/case?p=0&c=100&f=processDefinitionId=", self.process_id])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        elif json.loads(response.content):
            return json.loads(response.content)[0]["id"]
        else:
            return self.create_case(request)

    def get_process_id(self, request):
        url = "".join([self.uri, "/API/bpm/process?c=100&p=0&f=name=Aprobacion de medicamentos"])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        response = json.loads(response.content)
        self.process_id = response[0]["id"]
        return self.process_id

    def get_users_protocol_responsible(self, request):
        group_id = self.get_group_by_name(request, "Responsable de protocolo")
        url = "".join(
            [self.uri, "/API/identity/user?p=0&c=100&o=firstname%20ASC&f=enabled%3dtrue&f=group_id=", group_id])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)

    def get_role_by_name(self, request, name):
        url = "".join([self.uri, "/API/identity/role?p=0&c=100&f=name=", name])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)[0]["id"]

    def get_user_logged(self, request):
        url = "".join([self.uri, "/API/system/session/unusedid"])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)

    def get_human_task_by_name(self, request, name):
        name = "Configuración del proyecto"
        url = "".join([self.uri, "/API/bpm/humanTask?p=0&c=100&f=name=", name])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        print(json.loads(response.content))
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)

    def get_group_by_name(self, request, name):
        url = "".join([self.uri, "/API/identity/group?p=0&c=100&f=displayName=", name])
        response = requests.get(url, cookies=request.COOKIES)
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)[0]["id"]

    def get_activities_by_case(self, request):
        if request.GET.get("id"):
            return request.GET.get("id")
        else:
            url = "".join(
                [self.uri, "/API/bpm/activity?f=processId=", self.process_id, "&f=parentCaseId=", self.case_id])
            response = requests.get(url, cookies=request.session["bonita_cookies"])

            if response.status_code != 200:
                raise Exception("HTTP STATUS: " + str(response))
            return json.loads(response.content)[0]["id"]

    def check_activity_assignment(self, request, activity):
        url = "".join([self.uri, "/API/bpm/activity/", activity])
        print(activity)
        print(url)
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))

        print(json.loads(response.content))
        print(json.loads(response.content)["assigned_id"])
        return json.loads(response.content)["assigned_id"]

    def update_activity_assignment(self, request, activity):
        url = "".join([self.uri, "/API/bpm/humanTask/", activity])
        headers = {
            "X-Bonita-API-Token": request.session["bonita_cookies"]["X-Bonita-API-Token"],
            "Content-type": "application/json"
        }
        user = self.get_user_logged(request)
        data = {
            "assigned_id": user["user_id"]
        }

        response = requests.put(url, json=data, headers=headers, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))

    def update_activity_state(self, request, activity, state, project=None):
        url = "".join([self.uri, "/API/bpm/activity/", activity])
        headers = {
            "X-Bonita-API-Token": request.session["bonita_cookies"]["X-Bonita-API-Token"],
            "Content-type": "application/json"
        }
        data = {
            "state": state,
            # "dueDate": project.end_date
        }

        response = requests.put(url, data=json.dumps(data), headers=headers, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.content))

    def set_active_project(self, request, project):
        # Esto es para ver todas las variables que tiene el caso, con el tipo de cada una
        # url = "".join([self.uri, "/API/bpm/caseVariable?p=0&c=100&f=case_id%3d", self.get_case(request)])
        # response = requests.get(url, cookies=request.COOKIES)
        url = "".join([self.uri, "/API/bpm/caseVariable/", self.get_case(request), "/var_active_project"])

        headers = {
            "X-Bonita-API-Token": request.session["bonita_cookies"]["X-Bonita-API-Token"],
            "Content-type": "application/json"
        }
        data = {
            "type": "java.lang.String",
            "value": project.id
        }

        response = requests.put(url, json=data, headers=headers, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))

    def set_protocol_result(self, request, result):
        url = "".join([self.uri, "/API/bpm/caseVariable/", self.get_case(request), "/protocol_result"])
        headers = {
            "X-Bonita-API-Token": request.session["bonita_cookies"]["X-Bonita-API-Token"],
            "Content-type": "application/json"
        }
        data = {
            "type": "java.lang.Boolean",
            "value": "true" if result else "false"
        }

        response = requests.put(url, json=data, headers=headers, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))

        # Esto es para ver todas las variables que tiene el caso, con el tipo de cada una
        # url = "".join([self.uri, "/API/bpm/caseVariable?p=0&c=100&f=case_id%3d", self.get_case(request)])
        # response = requests.get(url, cookies=request.COOKIES)
        # print(response.content)
