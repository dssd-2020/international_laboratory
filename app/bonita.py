import json
import requests
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


class BonitaManager:
    process_id = None
    cookies = None
    uri = "http://localhost:8080/bonita"

    def __init__(self, request=None):
        if request is None:
            request = {}
        elif "user_logged" in request.session:
            self.login(request, request.session["username"], request.session["password"])
            self.process_id = self.get_process_id(request)

    def headers(self, request):
        return {
                "X-Bonita-API-Token": request.session["bonita_cookies"]["X-Bonita-API-Token"],
                "Content-Type": "application/json",
                "cache-control": "no-cache"
        }

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
            logging.info('El usuario %s ha iniciado sesión', request.session["user_logged"]['user_name'])
            request.session["username"] = username
            request.session["password"] = password
            request.session["user_membership"] = self.get_membership_by_user(request)
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
            del request.session["username"]
            del request.session["password"]
            del request.session["bonita_cookies"]
            return True
        return False

    def create_case(self, request):
        if request.GET.get("id"):
            return self.get_case_by_activity(request, request.GET.get("id"))
        else:
            url = "".join([self.uri, "/API/bpm/process/", self.get_process_id(request), "/instantiation"])

            response = requests.post(url, headers=self.headers(request), cookies=request.session["bonita_cookies"])
            if response.status_code != 200:
                raise Exception("HTTP STATUS: " + str(response))
            logging.info('Se creó el caso: N° %s', str(json.loads(response.content)["caseId"]))
            return str(json.loads(response.content)["caseId"])

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

    def get_case_by_activity(self, request, activity):
        url = "".join([self.uri, "/API/bpm/activity/", activity])
        logging.debug("Url a la que llama para obtener la actividad %s", url)
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)

    def get_users_by_role(self, request, name):
        group_id = self.get_group_by_name(request, name)
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
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)[0]["id"]

    def get_activities_by_case(self, request, case_id):
        url = "".join([self.uri, "/API/bpm/activity?f=processId=", self.process_id, "&f=parentCaseId=", case_id])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)[0]["id"]

    def check_task_assignment(self, request, activity):
        url = "".join([self.uri, "/API/bpm/activity/", activity])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))
        return json.loads(response.content)["assigned_id"]

    def check_task_state(self, request, activity):
        url = "".join([self.uri, "/API/bpm/activity/", activity])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))
        return json.loads(response.content)["state"]

    def update_task_assignment(self, request, activity):
        url = "".join([self.uri, "/API/bpm/humanTask/", activity])

        user = self.get_user_logged(request)
        data = {
            "assigned_id": user["user_id"]
        }

        response = requests.put(url, json=data, headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code) + '----' + str(response))

    def update_task_state(self, request, activity, state):
        url = "".join([self.uri, "/API/bpm/activity/", activity])

        data = {
            "state": state
        }

        response = requests.put(url, data=json.dumps(data), headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))

    def set_active_project(self, request, project):
        url = "".join([self.uri, "/API/bpm/caseVariable/", project.case_id, "/var_active_project"])

        data = {
            "type": "java.lang.String",
            "value": project.id
        }

        response = requests.put(url, json=data, headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))

        # VER EL VALOR DE LA VARIABLE ACTUALIZADA
        url = "".join([self.uri, "/API/bpm/caseVariable/", project.case_id, "/var_active_project"])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        logging.debug(response.content)

    def set_active_project_name(self, request, project):
        url = "".join([self.uri, "/API/bpm/caseVariable/", project.case_id, "/project_name"])

        data = {
            "type": "java.lang.String",
            "value": project.name
        }

        response = requests.put(url, json=data, headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))

        # VER EL VALOR DE LA VARIABLE ACTUALIZADA
        url = "".join([self.uri, "/API/bpm/caseVariable/", project.case_id, "/project_name"])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        logging.debug(response.content)

    def set_protocol_result(self, request, case_id, result):
        url = "".join([self.uri, "/API/bpm/caseVariable/", case_id, "/protocol_state_approved"])

        data = {
            "type": "java.lang.Boolean",
            "value": "true" if result else "false"
        }

        response = requests.put(url, json=data, headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))

        # VER EL VALOR DE LA VARIABLE ACTUALIZADA
        url = "".join([self.uri, "/API/bpm/caseVariable/", case_id, "/protocol_state_approved"])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        print(response.content)

    def set_resolution_failure(self, request, case_id, result):
        url = "".join([self.uri, "/API/bpm/caseVariable/", case_id, "/resolution_failure_var"])

        data = {
            "type": "java.lang.String",
            "value": result
        }

        response = requests.put(url, json=data, headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))

        # VER EL VALOR DE LA VARIABLE ACTUALIZADA
        # url = "".join([self.uri, "/API/bpm/caseVariable/", self.get_case(request), "/resolution_failure_var"])
        # response = requests.get(url, cookies=request.session["bonita_cookies"])
        # print(response.content)

    def get_membership_by_user(self, request):
        url = "".join(
            [self.uri, "/API/identity/membership?p=0&c=100&f=user_id=", request.session["user_logged"]['user_id'],
             "&d=role_id"])
        response = requests.get(url, cookies=request.session["bonita_cookies"])

        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        try:
            roles = [role['role_id']['displayName'] for role in json.loads(response.content)]
        except ():
            roles = {}
        return list(set(roles))

    def get_task_running(self, request, case_id):
        url = "".join([self.uri, "/API/bpm/activity?f=processId=", self.process_id, "&f=parentCaseId=", case_id])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        try:
            result = {
                "name": json.loads(response.content)[0]["displayName"],
                "state": json.loads(response.content)[0]["state"]
            }
            return result
        except:
            try:
                response = self.get_archived_case(request, case_id)

                result = {
                    "name": "caso archivado",
                    "state": response[0]["state"]
                }
                return result
            except:
                return "No hay información sobre este caso"

    def get_archived_case(self, request, case_id):
        url = "".join([self.uri, "/API/bpm/archivedCase/?p=0&c=100&f=sourceObjectId=", case_id])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return json.loads(response.content)

    def add_comment_case(self, request, case_id):
        url = "".join([self.uri, "/API/bpm/comment"])

        data = {
            "processInstanceId": case_id,
            "content": "cancelled",
            "userId": 102
        }

        response = requests.post(url, json=data, headers=self.headers(request), cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response.status_code))
        logging.debug(response.content)

    def get_user_names(self, request, user_id):
        url = "".join([self.uri, "/API/identity/user/", user_id])
        response = requests.get(url, cookies=request.session["bonita_cookies"])
        if response.status_code != 200:
            raise Exception("HTTP STATUS: " + str(response))
        return [json.loads(response.content)["firstname"], json.loads(response.content)["lastname"]]
