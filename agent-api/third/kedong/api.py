import requests
import json
from common import *


def get_notify_info(fault_info):
    if is_mock_third_api():
        data = {"result": {"send_department": "需要通知中心站、线路操作班、用电监察", "check_place": "去现场检查"}}
        return data

    try:
        data = {
            "fault_station": "%s站" % fault_info['fault_list'][0]['fac01_name'],
            "fault_station_id": fault_info['fault_list'][0]['seq_fac01'],
            "fault_device": fault_info['fault_list'][0]['dev_name'],
            "fault_device_id": fault_info['fault_list'][0]['fault_dev'],
            "fault_type": "4",
            "fault_uuid": "%d" % fault_info['fault_list'][0]['event_id']
        }
        data = json.dumps(data, ensure_ascii=False)

        url = "http://kdai.dcloud.sh.dc.sgcc.com.cn:8442/kdpai_notify"

        headers = {
            'Content-Type': 'application/json'
        }

        set_cache('api_get_notify_info_input', data)
        response = requests.post(url, data, headers=headers)
        result = json.loads(response.content)
        set_cache('api_get_notify_info_output', result)
        return result
    except Exception as e:
        set_cache('api_get_notify_info_output', str(e))
        return {}


if __name__ == "__main__":
    with open(get_path('/demo/6605.json'), 'r') as file:
        json_string = file.read()

    response = get_notify_info(json.loads(json_string))
    print(response)
