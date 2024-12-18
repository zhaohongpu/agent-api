import json

import requests
import urllib.parse

def test_fault_desc_api():
    data = "event_id=6605"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/fault_desc', data=data, headers=headers)
    print(response.json())

def test_fault_analysis_api():
    data = "event_id=6605"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/fault_analysis', data=data, headers=headers)
    print(response.json())

def test_create_plan_api():
    data = ""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/create_plan', data=data, headers=headers)
    print(response.json())

def test_create_plan_n1_api():
    data = ""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/create_plan_n1', data=data, headers=headers)
    print(response.json())


def test_create_plan_single_api():
    data = ""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/create_plan_single', data=data, headers=headers)
    print(response.json())

def test_create_ticket_api():
    data = ""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/create_ticket', data=data, headers=headers)
    print(response.json())

def test_exec_ticket_api():
    data = ""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/exec_ticket', data=data, headers=headers)
    print(response.json())


def test_create_plan_nn_v2_api():
    data = {
        'subName': '横沔站',
        'isYaoKong': 'false',
        'userNumberWeight': '90',
        'lineLoadRateThreshold': '80',
        'isBusBarRecover': 'false',
        'disableDev': 'xxx1,xxx2'
    }

    data = urllib.parse.urlencode(data)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/create_plan_nn_v2', data=data, headers=headers)
    print(response.json())


def test_optimize_plan_nn_v2_api():
    data = {
        'subName': '横沔站',
        'conclusionText': '横沔站 事故发生后0条馈线自切至站外不失电，失电用户数4523，通过倒送母线及一级转供恢复3771户用户，通过二级转供及电缆拼接复电0户用户，剩余752户用户未复电',
        'conclusionTwoText': '横沔站有2台主变、3段母线，厂站最高负载率71.74%；下级馈线可自切至站外馈线0条、直送用户数0条、重要用户进线0条、有转供路径的馈线7条、无转供路径的馈线6条',
        'score': '-20',

        'isYaoKong': 'false',
        'userNumberWeight': '90',
        'lineLoadRateThreshold': '80',
        'isBusBarRecover': 'false',
        'disableDev': 'xxx1,xxx2'
    }

    data = urllib.parse.urlencode(data)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/optimize_plan_nn_v2', data=data, headers=headers)
    print(response.json())

def test_create_plan_n1_v2_api(type='n_1'):
    data = {
        'subName': '医高站',
        'devName': '2号主变',
        'isYaoKong': 'false',
        'userNumberWeight': '90',
        'lineLoadRateThreshold': '80',
        'isBusBarRecover': 'false',
        'disableDev': 'xxx1,xxx2'
    }

    data = urllib.parse.urlencode(data)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('http://127.0.0.1:8188/agent/api/create_plan_n1_v2?type='+ type, data=data, headers=headers)
    print(response.json())

if __name__ == '__main__':
    test_fault_desc_api()
    test_fault_analysis_api()
    test_create_plan_api()
    test_create_plan_n1_api()
    test_create_plan_single_api()
    test_create_ticket_api()
    test_exec_ticket_api()

    test_create_plan_nn_v2_api()
    test_optimize_plan_nn_v2_api()
    test_create_plan_n1_v2_api(type='n_1')
    test_create_plan_n1_v2_api(type='single')