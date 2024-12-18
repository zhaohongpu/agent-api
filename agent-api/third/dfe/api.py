import requests
from common import *

# 给东方电子投送故障信息
def post_fault_info(event_id, fault_json_str):
    if is_mock_third_api():
        return {}

    try:
        url = "http://10.130.16.118:8084/DFTP/giantModel/setNariGzData"

        headers = {
            'Content-Type': 'application/json'
        }

        if isinstance(fault_json_str, dict):
            fault_json_str = to_json(fault_json_str)

        post = {
            'eventId': event_id,
            'eventData': fault_json_str
        }

        response = requests.post(url, json.dumps(post, ensure_ascii=False), headers=headers, timeout=5)
        response = json.loads(response.content)
        set_cache('api_post_fault_info_output', response)
        return response
    except Exception as e:
        set_cache('api_post_fault_info_output', str(e))
        return {}

# 给东方电子投送转供方案信息
def post_plan_info(plan_json_str, type=""):
    if is_mock_third_api():
        return None

    try:
        url = "http://10.130.16.118:8084/DFTP/giantModel/setZdZgData"

        headers = {
            'Content-Type': 'application/json'
        }

        if isinstance(plan_json_str, dict):
            plan_json_str = to_json(plan_json_str)

        set_cache("api_post_plan_info_%s_input" % type, plan_json_str)
        response = requests.post(url, json.dumps(plan_json_str, ensure_ascii=False), headers=headers, timeout=5)
        response = json.loads(response.content)
        set_cache("api_post_plan_info_%s_output" % type, response)
        return response
    except Exception as e:
        set_cache('api_post_plan_info_output', str(e))
        return {}

# 重要用户分析
def get_vip_info(event_id):
    if is_mock_third_api():
        result = {"data": [{"result": "电源数由2变为1", "vipName": "上海申康医院发展中心", "oldSource": 2}]}
        return result

    try:
        if not isinstance(event_id, str):
            event_id = str(event_id)

        url = "http://10.130.16.118:8084/DFTP/vipUserFault/multiToSingleSupply/" + event_id
        response = requests.get(url)
        response = json.loads(response.content)
        set_cache('api_get_vip_info_output', response)
        return response
    except Exception as e:
        set_cache('api_get_vip_info_output', str(e))
        return {'data': []}


if __name__ == "__main__":
    with open(get_path('/demo/6605.json'), 'r') as file:
        json_string = file.read()

    response = post_fault_info("6605", json_string)
    print(response)

    response = get_vip_info(6605)
    print(response)

    with open(get_path('/demo/plan_nn.json'), 'r') as file:
        data = file.read()
        data = json.loads(data)
        result = post_plan_info(data['data'], 'nn')
        print(result)

    with open(get_path('/demo/plan_n1.json'), 'r') as file:
        data = file.read()
        data = json.loads(data)
        result = post_plan_info(data['data'], 'n1')
        print(result)
