#Este modulo es el mas importante
#Hace dos cosas (dos funciones):
#1.Se conecta al api de pentera y lee
#los datos del ultimo test
#
#2.Parsea el resultado del test y devuelve
#una lista de usuarios crackeados.

import re
import requests
from enum import Enum
from app.service.pentera.config import config

class UnauthorizedException(Exception):
    pass

class LOGIN(Enum):
    method = 'POST'
    endpoint = 'auth/login'
    body = {"client_id": "%AUTH_ID%", "tgt": "%AUTH_TGT%"}
    uri = {}

class GET_TESTING_SCENARIOS(Enum):
    method = 'GET'
    endpoint = 'testing_scenarios'
    body = {}
    uri = {"token": "%AUTH_TOKEN%"}

class RUN_TESTING_SCENARIO(Enum):
    method = 'POST'
    endpoint = 'task/%template_id%/start_run'
    body = {}
    uri = {"token": "%AUTH_TOKEN%"}

class GET_TESTING_SCENARIO_HISTORY(Enum):
    method = 'GET'
    endpoint = 'testing_history'
    body = {}
    uri = {"token": "%AUTH_TOKEN%"}

class GET_TESTING_ACHIEVEMENTS(Enum):
    method = 'GET'
    endpoint = 'task_run/%task_run_id%/achievements'
    body = {}
    uri = {"token": "%AUTH_TOKEN%"}

class pentera:
    #Pattern to match everything between % and %    
    PATTERN = re.compile(r'%.*?%')
    INSTANCES = {}

    def __init__(self, endpoint):
        requests.packages.urllib3.disable_warnings()
        self.method = endpoint.method.value
        self.endpoint = endpoint.endpoint.value
        self.data = endpoint.body.value
        self.uri = endpoint.uri.value

    def act(self, extra_uri={}, extra_body={}):
        #Load data
        bodydata = self.data.copy()
        uridata = self.uri.copy()
        uridata.update(extra_uri)
        bodydata.update(extra_body)

        #Make substitutions

        for key, value in uridata.items():
            value_str = str(value)
            if self.PATTERN.match(value_str):
                if config.get(value_str[1:-1]) is not None:
                    uridata[key] = config.get(value_str[1:-1])
                else:
                    raise Exception('Invalid config')

        tokens = self.endpoint.split('/')
        for i in range(len(tokens)):
            if self.PATTERN.match(tokens[i]):
                tokens[i] = uridata[tokens[i][1:-1]]
        endpoint = '/'.join(tokens)
        
        uri = config.get("API_URL") + endpoint
        uri += '?' + '&'.join([f'{key}={value}' for key, value in uridata.items()])

        for key, value in bodydata.items():
            if self.PATTERN.match(value):
                if config.get(value[1:-1]) is not None:
                    bodydata[key] = config.get(value[1:-1])
                else:
                    raise Exception('Invalid config')


        #Execute requests
        if self.method == 'GET':
            response = requests.get(uri, verify=False)
        elif self.method == 'POST':
            response = requests.post(uri, data=bodydata, verify=False)
        else:
            raise Exception('Invalid method')

        #Process results
        if response.status_code == 200:
            jsdata = response.json()

            if jsdata["meta"]["status"] == "success":
                if "token" in jsdata["meta"]:
                    config.set("AUTH_TOKEN", jsdata["meta"]["token"])
                return jsdata
            else:
                raise Exception('Invalid response from pentera api: ' + jsdata["meta"]["errors"])
        elif response.status_code == 401:
            raise UnauthorizedException()
        else:
            raise Exception('Invalid response code: ' + str(response.status_code) + ' text: ' + response.text)

    @staticmethod
    def get(endpoint):
        if endpoint not in pentera.INSTANCES:
            pentera.INSTANCES[endpoint] = pentera(endpoint)
        return pentera.INSTANCES[endpoint]

class Schedule:
    def __init__(self):
        self.next_scheduled_task = None
        self.timezone = None
        self.type = None

    @staticmethod
    def from_json(data):
        schedule = Schedule()

        try:
            schedule.next_scheduled_task = data['next_scheduled_task']
            schedule.timezone = data['timezone']
            schedule.type = data['type']
        except KeyError:
            raise Exception('Invalid timezone data')
        
        return schedule

class TestingScenario:
    def __init__(self):
        self.template_id = None
        self.name = None
        self.description = None
        self.type = None
        self.schedule = None
        self.last_start_time = None
    
    @staticmethod
    def from_json(data):
        testing_scenario = TestingScenario()

        try:
            testing_scenario.template_id = data['template_id']
            testing_scenario.name = data['name']
            testing_scenario.description = data['description']
            testing_scenario.type = data['type']
            testing_scenario.schedule = Schedule.from_json(data['schedule'])
            testing_scenario.last_start_time = data['last_start_time']
        except KeyError:
            raise Exception('Invalid testing scenario')
        
        return testing_scenario

class Login:
    def __init__(self):
        self.tgt = None
        self.token = None

    @staticmethod
    def from_json(data):
        login = Login()

        try:
            login.tgt = data['tgt']
            login.token = data['token']
        except KeyError:
            raise Exception('Invalid login data')
        
        return login

class StartedTaskRunsStatus:
    def __init__(self):
        self.task_run_id = None
        self.template_id = None
        self.start_time = None
        self.type = None

    @staticmethod
    def from_json(data):
        started_task_runs_status = StartedTaskRunsStatus()

        try:
            started_task_runs_status.task_run_id = data['task_run_id']
            started_task_runs_status.template_id = data['template_id']
            started_task_runs_status.start_time = data['start_time']
            started_task_runs_status.type = data['type']
        except KeyError:
            raise Exception('Invalid started task runs status')
        
        return started_task_runs_status

class TaskRun:
    def __init__(self):
        self.task_run_id = None
        self.template_id = None
        self.start_time = None
        self.end_time = None
        self.status = None
        self.type = None
        self.name = None
        self.description = None
        self.duration = None

    @staticmethod
    def from_json(data):
        task_run = TaskRun()

        try:
            task_run.task_run_id = data['task_run_id']
            task_run.template_id = data['template_id']
            task_run.start_time = data['start_time']
            task_run.end_time = data['end_time']
            task_run.status = data['status']
            task_run.type = data['type']
            task_run.name = data['name']
            task_run.description = data['description']
            task_run.duration = data['duration']
        except KeyError:
            raise Exception('Invalid task run')
        
        return task_run

class Achievement:
    def __init__(self):
        self.id = None
        self.creation_time = None
        self.name = None
        self.summary = None
        self.severity = None
        self.parameters = None
        self.target  = None
        self.target_id = None
        self.results = None
        self.insight = None
        
    @staticmethod
    def from_json(data):
        achievement = Achievement()

        try:
            achievement.id = data['id']
            achievement.creation_time = data['creation_time']
            achievement.name = data['name']
            achievement.summary = data['summary']
            achievement.severity = data['severity']
            achievement.parameters = data['parameters']
            achievement.target  = data['target']
            achievement.target_id = data['target_id']
            achievement.results = data['results']
            achievement.insight = data['insight']
        except KeyError:
            raise Exception('Invalid achievement')
        
        return achievement

class Transformers:
    def __init__(self):
        pass

    @staticmethod
    def scenario_from_json(data):
        scenarios = []
        for scenario in data['testing_scenarios']:
            scenarios.append(TestingScenario.from_json(scenario))
        return scenarios
     
    @staticmethod
    def login_from_json(data):
        return Login.from_json(data)

    @staticmethod
    def started_task_runs_status_from_json(data):
        tasks = []
        for task_run_status in data['startedTaskRunsStatus']:
            tasks.append(StartedTaskRunsStatus.from_json(task_run_status))
        return tasks

    @staticmethod
    def login_from_config():
        login = Login()
        login.tgt = config.get("AUTH_TGT")
        login.token = config.get("AUTH_TOKEN")
        return login

    @staticmethod
    def task_runs_from_json(data):
        tasks_run = []
        for task_run in data['task_runs']:
            tasks_run.append(TaskRun.from_json(task_run))
        return tasks_run

    @staticmethod
    def achievements_from_json(data):
        achievements = []
        for achievement in data['achievements']:
            achievements.append(Achievement.from_json(achievement))
        return achievements

class PenteraService:

    @staticmethod
    def login():
        login = pentera.get(LOGIN)
        result = login.act()
        config.set('AUTH_TGT', result['tgt'])
        config.set('AUTH_TOKEN', result['token'])
        return Transformers.login_from_json(result)

    @staticmethod
    def logout():
        config.set("AUTH_TOKEN", "")
        return Transformers.login_from_config()
        
    @staticmethod
    def get_testing_scenarios():
        testing_scenarios = pentera.get(GET_TESTING_SCENARIOS)
        return Transformers.scenario_from_json(testing_scenarios.act())
        
    @staticmethod
    def start_testing_scenario(template_id):
        run_testing_scenario = pentera.get(RUN_TESTING_SCENARIO)
        return Transformers.started_task_runs_status_from_json(
            run_testing_scenario.act(extra_uri={"template_id": template_id})
        )

    @staticmethod
    def get_testing_history(start_time, end_time):
        testing_history = pentera.get(GET_TESTING_SCENARIO_HISTORY)
        return Transformers.task_runs_from_json(
            testing_history.act(extra_uri={"start_timestamp": start_time, "end_timestamp": end_time})
        )

    @staticmethod
    def get_testing_achievements(task_run_id, achievement_name=None):
        testing_achievements = pentera.get(GET_TESTING_ACHIEVEMENTS)
        results = Transformers.achievements_from_json(
            testing_achievements.act(extra_uri={"task_run_id": task_run_id})
        )
        
        if achievement_name is not None:
            res = []
            for achievement in results:
                if achievement_name == achievement.name:
                    res.append(achievement)
            return res
        
        return results