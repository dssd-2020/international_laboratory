import requests


class BonitaManager:

    process_id = ''

    def create_case(self, request):
        self.login(request)
        self.get_process_id(request)
        print(self.process_id)
        url = 'http://localhost:8080/bonita/API/bpm/case?p=0&c=100&f=processDefinitionId=' + self.process_id
        # headers = {
        #     'X-Bonita-API-Token': request.COOKIES['X-Bonita-API-Token'],
        #     'JSESSIONID': request.COOKIES['JSESSIONID'],
        #     'csrftoken': request.COOKIES['csrftoken'],
        #     'Content-Type': 'application/json'
        # }

        response = requests.post(url)
        # response = requests.get(
        #     'http://localhost:8080/bonita/API/bpm/process?f=name=AprobacionDeMedicamentos&p=0&c=10')
        # , headers=headers)
        print('case', response)
        return response

    def get_process_id(self, request):
        # request = self.login(request)
        url = 'http://localhost:8080/bonita/API/bpm/process?c=100&p=0'
        # url = 'http://localhost:8080/cookies'
        # headers = {
        #     'X-Bonita-API-Token': request.COOKIES['X-Bonita-API-Token'],
        #     # 'Content-Type': 'application/json',
        #     'Cookie': request.COOKIES['JSESSIONID'],
        #     # 'cache-control': 'no-cache',
        # }
        # response = requests.post(url, headers=headers)
        response = requests.get(url, cookies=request.COOKIES)
        print(response.status_code)
        print('getProcessId', response.content.decode())
        print(response.content.decode()[0]['id'])
        self.process_id = response.content
        return response

    def get_users(self, request):
        url = 'http://localhost:8080/bonita/API/identity/group'
        response = requests.get(url)
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

        if response.status_code == 200:
            request.session['X-Bonita-API-Token'] = request.COOKIES['X-Bonita-API-Token']
            request.session['JSESSIONID'] = request.COOKIES['JSESSIONID']
            # requests.session['csrftoken'] = request.COOKIES['csrftoken']

        return request
