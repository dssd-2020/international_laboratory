import requests
import json

class BonitaManager:

    process_id = '8683566894292358083'

    def create_case(self, request):
        self.login(request)
        url = 'http://localhost:8080/bonita/API/bpm/case'
        headers = {
            'X-Bonita-API-Token': request.COOKIES['X-Bonita-API-Token'],
            # 'JSESSIONID': request.COOKIES['JSESSIONID'],
            'Content-Type': 'application/json'
        }

        response = requests.post(url, cookies=request.COOKIES, headers=headers)
        print('case', response.content)
        return response

    def get_process_id(self, request):
        self.login(request)
        url = 'http://localhost:8080/bonita/API/bpm/process?c=100&p=0'
        response = requests.get(url, cookies=request.COOKIES)
        response = json.loads(response.content)
        self.process_id = response[0]['id']
        return response

    def get_users(self, request):
        self.get_process_id(request)
        url = 'http://localhost:8080/bonita/API/bpm/actor?p=0&c=100&f=process_id=' + self.process_id
        # '&n=users&n=group&n=roles&n=memberships'
        response = requests.get(url, cookies=request.COOKIES)
        print(response.content)
        return response

    def login(self, request):
        url = 'http://localhost:8080/bonita/loginservice'
        data = {'username': 'walter.bates',
                'password': 'bpm',
                'redirect': 'false',
                'redirectURL': ''}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers)

        # if response.status_code == 200:
        #     request.session['X-Bonita-API-Token'] = request.COOKIES['X-Bonita-API-Token']
        #     request.session['JSESSIONID'] = request.COOKIES['JSESSIONID']
        #     # requests.session['csrftoken'] = request.COOKIES['csrftoken']

        return response

    def get_user_logged(self, request):
        url = 'http://localhost:8080/bonita/API/system/session/unusedid'
        response = requests.get(url, cookies=request.COOKIES)
        return json.loads(response.content)
